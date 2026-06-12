import json
import logging
import time
from pathlib import Path
from typing import List
from sentence_transformers import SentenceTransformer

from .config import EmbeddingConfig
from .models import EmbeddedChunk, EmbeddingReport
from src.chunking.metadata import ChunkMetadata

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks using sentence-transformers.
    """

    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        logger.info(
            f"Loading embedding model: {self.config.model_name} on {self.config.device}"
        )

        # Load the sentence-transformer model
        self.model = SentenceTransformer(
            self.config.model_name, device=self.config.device
        )

        # Track statistics
        self.stats = {
            "total_chunks_processed": 0,
            "total_failures": 0,
            "total_tokens": 0,
            "start_time": None,
            "end_time": None,
        }

    def generate_embeddings(self, chunks: List[ChunkMetadata]) -> List[EmbeddedChunk]:
        """
        Takes a list of ChunkMetadata and returns a list of EmbeddedChunk with vectors.
        """
        if not chunks:
            return []

        texts = [chunk.chunk_text for chunk in chunks]

        try:
            logger.debug(f"Encoding batch of {len(chunks)} chunks...")
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=False,
            )

            embedded_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                try:
                    # Convert embedding to list of floats
                    emb_list = embedding.tolist()

                    embedded_chunk = EmbeddedChunk(
                        **chunk.model_dump(),
                        embedding=emb_list,
                        embedding_model=self.config.model_name,
                    )
                    embedded_chunks.append(embedded_chunk)
                    self.stats["total_chunks_processed"] += 1
                    self.stats["total_tokens"] += chunk.token_count
                except Exception as e:
                    logger.error(
                        f"Failed to create EmbeddedChunk for {chunk.chunk_id}: {e}"
                    )
                    self.stats["total_failures"] += 1

            return embedded_chunks

        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            self.stats["total_failures"] += len(chunks)
            return []

    def process_directory(self, input_dir: str, output_dir: str) -> EmbeddingReport:
        """
        Reads chunk JSON files from input_dir, generates embeddings, and saves to output_dir.
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        chunk_files = list(input_path.glob("*.json"))
        logger.info(f"Found {len(chunk_files)} chunk files in {input_dir}")

        self.stats["start_time"] = time.time()

        batch = []

        for i, file_path in enumerate(chunk_files, 1):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    chunk_data = json.load(f)
                    chunk = ChunkMetadata(**chunk_data)
                    batch.append(chunk)
            except Exception as e:
                logger.error(f"Error reading chunk file {file_path}: {e}")
                self.stats["total_failures"] += 1

            # Process in batches to manage memory
            if len(batch) >= self.config.batch_size or i == len(chunk_files):
                if batch:
                    embedded_chunks = self.generate_embeddings(batch)
                    self._save_embedded_chunks(embedded_chunks, output_path)
                    batch = []

            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(chunk_files)} files...")

        self.stats["end_time"] = time.time()

        duration = self.stats["end_time"] - self.stats["start_time"]
        avg_tokens = 0.0
        if self.stats["total_chunks_processed"] > 0:
            avg_tokens = (
                self.stats["total_tokens"] / self.stats["total_chunks_processed"]
            )

        report = EmbeddingReport(
            model_name=self.config.model_name,
            total_chunks_processed=self.stats["total_chunks_processed"],
            total_failures=self.stats["total_failures"],
            embedding_dimensions=self.config.expected_dimensions,
            avg_chunk_tokens=avg_tokens,
            duration_seconds=duration,
        )

        logger.info(
            f"Embedding generation complete in {duration:.2f}s. "
            f"Processed: {self.stats['total_chunks_processed']}, "
            f"Failures: {self.stats['total_failures']}"
        )
        return report

    def _save_embedded_chunks(
        self, embedded_chunks: List[EmbeddedChunk], output_path: Path
    ):
        """
        Saves embedded chunks to the output directory as JSON files.
        """
        for embedded_chunk in embedded_chunks:
            file_path = output_path / f"{embedded_chunk.chunk_id}.json"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(embedded_chunk.model_dump_json(indent=2))
            except Exception as e:
                logger.error(
                    f"Error saving embedded chunk {embedded_chunk.chunk_id}: {e}"
                )
                self.stats["total_failures"] += 1
