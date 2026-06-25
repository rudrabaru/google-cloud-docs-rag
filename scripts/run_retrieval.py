"""
What it does: Runs one single query and prints the actual raw text of the chunks, their similarity scores, and their source URLs directly to your terminal.
When to use it: For manual retrieval inspection and debugging of how a query is retrieved and where and why it failed.
"""

import sys
import os
import json
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieving.vector_store import ChromaDBManager
from src.retrieving.retriever import DenseRetriever, OptionalReranker, HybridRetriever
from scripts.version_utils import get_latest_version


def main():
    parser = argparse.ArgumentParser(description="Test Retrieving")
    parser.add_argument(
        "--query", type=str, required=True, help="Query to test retrieval"
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default="corpus_v1",
        help="Name for the vector database collection.",
    )
    parser.add_argument(
        "--top_k", type=int, default=3, help="Number of chunks to retrieve"
    )
    parser.add_argument(
        "--use_reranker", action="store_true", help="Use cross-encoder reranker"
    )
    parser.add_argument(
        "--use_hybrid", action="store_true", help="Use BM25 + Dense Hybrid Search"
    )
    args = parser.parse_args()

    base_embeddings_dir = Path("embeddings")
    embed_version = get_latest_version(base_embeddings_dir)

    if embed_version == "v0":
        print("Error: No embeddings found.")
        return

    metrics_dir = base_embeddings_dir / embed_version / "metrics"
    manifest_path = metrics_dir / "embedding_validation_report.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    distance_metric = manifest.get("distance_metric", "cosine")

    db_manager = ChromaDBManager(
        collection_name=args.collection_name, distance_metric=distance_metric
    )

    print(f"Connected to ChromaDB collection: {args.collection_name}")

    dense_retriever = DenseRetriever(vector_store=db_manager)
    
    if args.use_hybrid:
        bm25_path = base_embeddings_dir / embed_version / "bm25_index.pkl"
        if not bm25_path.exists():
            print(f"Error: BM25 index not found at {bm25_path}. Run build_vector_db.py again.")
            return
        retriever = HybridRetriever(dense_retriever=dense_retriever, bm25_index_path=bm25_path)
    else:
        retriever = dense_retriever

    print(f"\nQuery: {args.query}")
    
    if args.use_reranker:
        print(f"Using {'Hybrid' if args.use_hybrid else 'Dense'} Retrieval + Cross-Encoder Reranking")
        dense_result = retriever.retrieve(args.query, top_k=args.top_k * 4)
        reranker = OptionalReranker()
        result = reranker.rerank(args.query, dense_result.chunks, top_k=args.top_k)
        # Preserve original embedding/search latency for metrics if needed
        result.embedding_latency_ms = dense_result.embedding_latency_ms
        result.search_latency_ms = dense_result.search_latency_ms
        result.latency_ms += dense_result.latency_ms
    else:
        result = retriever.retrieve(args.query, top_k=args.top_k)

    print(f"Latency: {result.latency_ms:.2f}ms")
    print("\nResults:")
    for i, c in enumerate(result.chunks):
        doc = c.metadata.get("source_url", c.source_document)
        print(
            f"[{i+1}] Score: {c.similarity_score:.4f} | Doc: {doc} | Section: {c.metadata.get('section_title', '')}"
        )
        print(c.text[:200] + "...\n")


if __name__ == "__main__":
    main()
