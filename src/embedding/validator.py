import json
import logging
from pathlib import Path
from typing import List, Dict
import math
import statistics
import random

import torch
from sentence_transformers import util

from .config import EmbeddingConfig
from .models import EmbeddedChunk

logger = logging.getLogger(__name__)


class EmbeddingValidator:
    """
    Validates embeddings for correctness, dimension consistency, and semantic similarity.
    """

    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()

    def _load_all_chunks(self, embeddings_dir: str) -> List[EmbeddedChunk]:
        path = Path(embeddings_dir)
        files = list(path.glob("*.json"))
        all_chunks = []
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    all_chunks.append(EmbeddedChunk(**data))
            except Exception:
                pass
        return all_chunks

    def audit_distribution(self, embeddings_dir: str) -> Dict:
        chunks = self._load_all_chunks(embeddings_dir)
        if not chunks:
            return {}

        norms = []
        zero_vectors = 0
        near_zero = 0

        for c in chunks:
            vec = c.embedding
            norm = math.sqrt(sum(x * x for x in vec))
            norms.append(norm)
            if norm == 0:
                zero_vectors += 1
            elif norm < 1e-5:
                near_zero += 1

        return {
            "total_vectors": len(chunks),
            "vector_dimension": len(chunks[0].embedding) if chunks else 0,
            "zero_vectors": zero_vectors,
            "near_zero_vectors": near_zero,
            "distribution": {
                "min_norm": round(min(norms), 4),
                "max_norm": round(max(norms), 4),
                "avg_norm": round(sum(norms) / len(norms), 4),
                "median_norm": round(statistics.median(norms), 4),
                "std_dev": round(statistics.stdev(norms), 4) if len(norms) > 1 else 0.0,
            },
        }

    def detect_duplicates(
        self, embeddings_dir: str, threshold: float = 0.99
    ) -> List[Dict]:
        chunks = self._load_all_chunks(embeddings_dir)
        if len(chunks) < 2:
            return []

        # Optimize by computing chunked cosine similarities if memory is an issue
        # With 5350 chunks, 5350x5350 is 28M floats, perfectly fine for memory.
        embedding_matrix = torch.tensor([c.embedding for c in chunks])
        cos_sim = util.cos_sim(embedding_matrix, embedding_matrix)

        duplicates = []
        rows, cols = torch.where(cos_sim > threshold)
        for i, j in zip(rows.tolist(), cols.tolist()):
            if i < j:
                c1 = chunks[i]
                c2 = chunks[j]
                duplicates.append(
                    {
                        "chunk_id_1": c1.chunk_id,
                        "chunk_id_2": c2.chunk_id,
                        "source_document_1": c1.source_document,
                        "source_document_2": c2.source_document,
                        "heading_path_1": c1.heading_path,
                        "heading_path_2": c2.heading_path,
                        "similarity_score": round(cos_sim[i][j].item(), 4),
                    }
                )

        duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return duplicates[:100]

    def enhanced_similarity_validation(
        self, embeddings_dir: str, sample_size: int = 100
    ) -> Dict:
        chunks = self._load_all_chunks(embeddings_dir)
        if len(chunks) < 2:
            return {}

        queries = random.sample(chunks, min(sample_size, len(chunks)))
        embedding_matrix = torch.tensor([c.embedding for c in chunks])

        same_section_scores = []
        same_doc_scores = []
        diff_doc_scores = []

        for q in queries:
            q_vec = torch.tensor(q.embedding)
            sims = util.cos_sim(q_vec, embedding_matrix)[0].tolist()

            for i, c in enumerate(chunks):
                if c.chunk_id == q.chunk_id:
                    continue
                score = sims[i]
                if c.source_document == q.source_document:
                    if c.heading_path == q.heading_path and q.heading_path:
                        same_section_scores.append(score)
                    else:
                        same_doc_scores.append(score)
                else:
                    diff_doc_scores.append(score)

        avg_same_sec = (
            sum(same_section_scores) / len(same_section_scores)
            if same_section_scores
            else 0.0
        )
        avg_same_doc = (
            sum(same_doc_scores) / len(same_doc_scores) if same_doc_scores else 0.0
        )

        if diff_doc_scores:
            if len(diff_doc_scores) > 10000:
                diff_doc_scores = random.sample(diff_doc_scores, 10000)
            avg_diff_doc = sum(diff_doc_scores) / len(diff_doc_scores)
        else:
            avg_diff_doc = 0.0

        is_healthy = avg_same_sec >= avg_same_doc >= avg_diff_doc

        return {
            "average_similarity": {
                "same_section": round(avg_same_sec, 4),
                "same_document": round(avg_same_doc, 4),
                "different_document": round(avg_diff_doc, 4),
            },
            "pattern_holds": is_healthy,
            "samples_evaluated": len(queries),
        }
