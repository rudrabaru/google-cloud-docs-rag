import sys
import os
import json
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking.chunker import SemanticChunker
from scripts.version_utils import get_latest_version, get_next_version


def main():
    parser = argparse.ArgumentParser(description="Run Phase 3: Semantic Chunking")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="processed_docs",
        help="Directory containing cleaned docs.",
    )
    parser.add_argument(
        "--output_dir", type=str, default="chunks", help="Directory for output chunks."
    )
    args = parser.parse_args()

    processed_base = Path(args.input_dir)
    chunks_base = Path(args.output_dir)

    latest_processed = get_latest_version(processed_base)
    if latest_processed == "v0":
        print(f"Error: No processed documents found in {args.input_dir}")
        return

    input_dir = processed_base / latest_processed
    print(f"Using processed documents from: {input_dir}")

    next_chunks = get_next_version(chunks_base)
    output_dir = chunks_base / next_chunks
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = output_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting Phase 3 Chunking -> Output Version: {next_chunks}")

    chunker = SemanticChunker()
    docs = []

    for filepath in input_dir.rglob("*.json"):
        if filepath.parent.name == "metrics":
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            docs.append(json.load(f))

    print(f"Loaded {len(docs)} documents for chunking.")
    all_chunks = chunker.chunk_batch(docs)
    print(f"Generated {len(all_chunks)} chunks.")

    manifest = {
        "chunking_version": next_chunks,
        "source_processed_version": latest_processed,
        "total_documents": len(docs),
        "total_chunks": len(all_chunks),
    }

    with open(metrics_dir / "chunking_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    chunks_file = output_dir / "all_chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump([c.dict() for c in all_chunks], f, indent=2)

    print(f"Saved chunks to {chunks_file}")


if __name__ == "__main__":
    main()
