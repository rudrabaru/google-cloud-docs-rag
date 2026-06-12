import time
import logging
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer

from pydantic import BaseModel
from .vector_store import ChromaDBManager
from src.embedding.config import EmbeddingConfig

logger = logging.getLogger(__name__)


class RetrievedChunk(BaseModel):
    chunk_id: str
    source_document: str
    text: str
    similarity_score: float
    metadata: Dict[str, Any]


class RetrievalResult(BaseModel):
    query: str
    top_k: int
    latency_ms: float
    embedding_latency_ms: float = 0.0
    search_latency_ms: float = 0.0
    rerank_latency_ms: float = 0.0
    chunks: List[RetrievedChunk]


class DenseRetriever:
    def __init__(
        self,
        vector_store: ChromaDBManager,
        embedding_config: Optional[EmbeddingConfig] = None,
    ):
        self.vector_store = vector_store
        self.config = embedding_config or EmbeddingConfig()
        logger.info(
            f"Loading embedding model for dense retrieval: {self.config.model_name}"
        )
        self.model = SentenceTransformer(
            self.config.model_name, device=self.config.device
        )

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        start_time = time.time()

        # 1. Embed query
        embed_start = time.time()
        query_embedding = self.model.encode(
            query,
            normalize_embeddings=self.config.normalize_embeddings,
            show_progress_bar=False,
        ).tolist()
        embed_latency = (time.time() - embed_start) * 1000

        # 2. Query ChromaDB
        search_start = time.time()
        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        search_latency = (time.time() - search_start) * 1000

        # 3. Format candidates
        candidates = []
        if results["ids"] and len(results["ids"]) > 0:
            ids = results["ids"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]
            documents = results["documents"][0]

            for i in range(len(ids)):
                # Similarity = 1.0 - distance
                similarity = 1.0 - distances[i] if distances[i] <= 1.0 else 0.0

                chunk = RetrievedChunk(
                    chunk_id=ids[i],
                    source_document=metadatas[i].get("source_document", ""),
                    text=documents[i],
                    similarity_score=similarity,
                    metadata=metadatas[i],
                )
                candidates.append(chunk)

        # Sort by similarity score descending (Chroma should already do this, but just to be sure)
        candidates.sort(key=lambda x: x.similarity_score, reverse=True)

        latency = (time.time() - start_time) * 1000

        return RetrievalResult(
            query=query,
            top_k=top_k,
            latency_ms=latency,
            embedding_latency_ms=embed_latency,
            search_latency_ms=search_latency,
            chunks=candidates,
        )


class OptionalReranker:
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: str = "cpu",
    ):
        from sentence_transformers import CrossEncoder

        self.model_name = model_name
        logger.info(f"Loading cross-encoder model: {self.model_name}")
        self.reranker = CrossEncoder(self.model_name, device=device)

    def rerank(
        self, query: str, candidates: List[RetrievedChunk], top_k: int
    ) -> RetrievalResult:
        if not candidates:
            return RetrievalResult(query=query, top_k=top_k, latency_ms=0, chunks=[])

        start_time = time.time()

        cross_inp = [[query, chunk.text] for chunk in candidates]
        cross_scores = self.reranker.predict(cross_inp)

        for i in range(len(candidates)):
            candidates[i].similarity_score = float(cross_scores[i])

        candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        reranked_chunks = candidates[:top_k]

        latency = (time.time() - start_time) * 1000

        return RetrievalResult(
            query=query,
            top_k=top_k,
            latency_ms=latency,
            rerank_latency_ms=latency,
            chunks=reranked_chunks,
        )
