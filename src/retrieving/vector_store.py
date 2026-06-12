import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from src.embedding.models import EmbeddedChunk

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """
    Manages interaction with ChromaDB for storing and retrieving embedded chunks.
    """

    def __init__(
        self,
        persist_directory: str = ".chroma_db",
        collection_name: str = "docs_v1",
        distance_metric: str = "cosine",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.distance_metric = distance_metric

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": self.distance_metric}
        )
        logger.info(
            f"Initialized ChromaDB at {persist_directory} with collection '{collection_name}' (space: {self.distance_metric})"
        )

    def _prepare_metadata(self, chunk: EmbeddedChunk) -> Dict[str, Any]:
        """
        Prepares metadata for ChromaDB by flattening lists and ensuring types are supported.
        ChromaDB only supports str, int, float, bool.
        """
        metadata = {
            "chunk_id": chunk.chunk_id,
            "source_document": chunk.source_document,
            "source_url": getattr(chunk, "source_url", ""),
            "title": chunk.title,
            "section_title": chunk.section_title,
            "contains_code": chunk.contains_code,
            "contains_table": chunk.contains_table,
            "content_type": chunk.content_type,
            "chunk_version": chunk.chunk_version,
            "document_version": chunk.document_version,
        }

        # Convert heading_path list to a string
        if chunk.heading_path:
            metadata["heading_path"] = " > ".join(chunk.heading_path)
        else:
            metadata["heading_path"] = ""

        return metadata

    def load_chunks(self, chunks: List[EmbeddedChunk]) -> int:
        """
        Loads a list of EmbeddedChunks into the ChromaDB collection.
        Returns the number of successfully added chunks.
        """
        if not chunks:
            return 0

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            embeddings.append(chunk.embedding)
            metadatas.append(self._prepare_metadata(chunk))
            documents.append(chunk.chunk_text)

        try:
            self.collection.add(
                ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents
            )
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to load chunks into ChromaDB: {e}")
            return 0

    def load_from_directory(self, embeddings_dir: str, batch_size: int = 100) -> int:
        """
        Reads all embedded chunk JSON files from a directory and loads them into ChromaDB in batches.
        """
        dir_path = Path(embeddings_dir)
        json_files = list(dir_path.glob("*.json"))

        logger.info(f"Found {len(json_files)} embedded chunk files in {embeddings_dir}")

        total_loaded = 0
        current_batch = []

        for i, file_path in enumerate(json_files, 1):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chunk = EmbeddedChunk(**data)
                    current_batch.append(chunk)
            except Exception as e:
                logger.warning(f"Failed to read/parse {file_path}: {e}")

            if len(current_batch) >= batch_size or i == len(json_files):
                if current_batch:
                    loaded = self.load_chunks(current_batch)
                    total_loaded += loaded
                    current_batch = []

            if i % 500 == 0:
                logger.info(f"Processed {i}/{len(json_files)} files...")

        # Load any remaining chunks
        if current_batch:
            loaded = self.load_chunks(current_batch)
            total_loaded += loaded

        logger.info(f"Successfully loaded {total_loaded} chunks into ChromaDB.")
        return total_loaded

    def get_collection_size(self) -> int:
        """Returns the number of items in the collection."""
        return self.collection.count()
