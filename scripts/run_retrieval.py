import sys
import os
import json
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieving.vector_store import ChromaDBManager
from src.retrieving.retriever import DenseRetriever
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

    retriever = DenseRetriever(vector_store=db_manager)

    print(f"\nQuery: {args.query}")
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
