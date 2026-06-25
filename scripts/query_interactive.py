import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieving.vector_store import ChromaDBManager
from src.retrieving.retriever import DenseRetriever
from scripts.version_utils import get_latest_version


def main():
    parser = argparse.ArgumentParser(description="Interactive RAG Pipeline Tester")
    parser.add_argument(
        "--collection_name",
        type=str,
        default="corpus_v1",
        help="Name for the vector database collection.",
    )
    parser.add_argument(
        "--top_k", type=int, default=3, help="Number of results to retrieve per query"
    )
    args = parser.parse_args()

    print("==================================================")
    print("        RAG Pipeline Interactive Tester           ")
    print("==================================================")

    base_embeddings_dir = Path("embeddings")
    embed_version = get_latest_version(base_embeddings_dir)

    if embed_version == "v0":
        print("Error: No embeddings found. Please run the embedding phase first.")
        return

    metrics_dir = base_embeddings_dir / embed_version / "metrics"
    manifest_path = metrics_dir / "embedding_manifest.json"

    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    distance_metric = manifest.get("distance_metric", "cosine")

    print(
        f"Loading ChromaDB Collection: {args.collection_name} (Metric: {distance_metric})..."
    )
    db_manager = ChromaDBManager(
        collection_name=args.collection_name, distance_metric=distance_metric
    )

    print("Initializing Dense Retriever (all-MiniLM-L6-v2)...")
    retriever = DenseRetriever(vector_store=db_manager)
    print("System Ready!\n")

    while True:
        try:
            query = input("\nEnter your query (or type 'exit' to quit): ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting. Have a great day!")
                break

            print("\nSearching...")
            result = retriever.retrieve(query, top_k=args.top_k)

            print(
                f"\n--- Top {len(result.chunks)} Results (Latency: {result.latency_ms:.2f}ms) ---\n"
            )

            if not result.chunks:
                print("No results found.")
                continue

            for i, chunk in enumerate(result.chunks):
                doc_url = chunk.metadata.get("source_url", chunk.source_document)
                section = chunk.metadata.get("section_title", "N/A")
                score = chunk.similarity_score

                raw_path = chunk.metadata.get("heading_path", "")
                try:
                    parsed = json.loads(raw_path) if isinstance(raw_path, str) else raw_path
                    path_str = (
                        " > ".join(parsed)
                        if isinstance(parsed, list)
                        else str(parsed)
                    )
                except (json.JSONDecodeError, TypeError):
                    # Legacy fallback: if stored as " > " joined string
                    path_str = str(raw_path)

                print(f"[{i+1}] Score: {score:.4f}")
                print(f"URL: {doc_url}")
                if path_str:
                    print(f"Section: {path_str}")
                else:
                    print(f"Section: {section}")
                print("-" * 50)
                snippet = (
                    chunk.text[:300] + "..." if len(chunk.text) > 300 else chunk.text
                )
                print(snippet)
                print("=" * 50 + "\n")

        except KeyboardInterrupt:
            print("\nExiting. Have a great day!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
