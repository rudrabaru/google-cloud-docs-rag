import sys
import os
import json
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieving.vector_store import ChromaDBManager
from src.embedding.models import EmbeddedChunk
from scripts.version_utils import get_latest_version


def main():
    parser = argparse.ArgumentParser(description="Build ChromaDB Vector Database")
    parser.add_argument(
        "--embeddings_dir",
        type=str,
        default="embeddings",
        help="Directory containing generated embeddings.",
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default="corpus_v1",
        help="Name for the vector database collection.",
    )
    args = parser.parse_args()

    base_embeddings_dir = Path(args.embeddings_dir)
    latest_version = get_latest_version(base_embeddings_dir)

    if latest_version == "v0":
        print(f"Error: No embeddings found in {args.embeddings_dir}")
        return

    embeddings_file = base_embeddings_dir / latest_version / "embeddings.json"
    manifest_file = (
        base_embeddings_dir / latest_version / "metrics" / "embedding_validation_report.json"
    )

    if not embeddings_file.exists() or not manifest_file.exists():
        print("Error: Missing embeddings.json or embedding_validation_report.json")
        return

    print(f"Loading embeddings from {latest_version}...")
    with open(embeddings_file, "r", encoding="utf-8") as f:
        embeddings_raw = json.load(f)
        
    embeddings_data = [EmbeddedChunk(**e) for e in embeddings_raw]

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    distance_metric = manifest.get("distance_metric", "cosine")

    db_manager = ChromaDBManager(
        collection_name=args.collection_name, distance_metric=distance_metric
    )

    print(
        f"Loading {len(embeddings_data)} embeddings to collection '{args.collection_name}' (Metric: {distance_metric})..."
    )
    db_manager.load_chunks(embeddings_data)
    print("Done!")


if __name__ == "__main__":
    main()
