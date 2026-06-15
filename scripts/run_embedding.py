import sys
import os
import json
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embedding.config import EmbeddingConfig
from src.embedding.generator import EmbeddingGenerator
from src.embedding.validator import EmbeddingValidator
from src.chunking.metadata import ChunkMetadata
from scripts.version_utils import get_latest_version, get_next_version


def main():
    parser = argparse.ArgumentParser(description="Run Phase 4: Embeddings Generation")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="chunks",
        help="Directory containing semantic chunks.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="embeddings",
        help="Directory for output embeddings.",
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default="corpus_v1",
        help="Name for the vector database collection.",
    )
    args = parser.parse_args()

    chunks_base = Path(args.input_dir)
    embeddings_base = Path(args.output_dir)

    latest_chunks = get_latest_version(chunks_base)
    if latest_chunks == "v0":
        print(f"Error: No chunks found in {args.input_dir}")
        return

    input_chunks_file = chunks_base / latest_chunks / "all_chunks.json"
    if not input_chunks_file.exists():
        print(f"Error: {input_chunks_file} not found")
        return

    print(f"Using chunks from: {input_chunks_file}")

    with open(input_chunks_file, "r", encoding="utf-8") as f:
        chunks_data_raw = json.load(f)
    
    chunks_data = [ChunkMetadata(**c) for c in chunks_data_raw]

    next_embed = get_next_version(embeddings_base)
    output_dir = embeddings_base / next_embed
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = output_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting Phase 4 Embedding -> Output Version: {next_embed}")

    config = EmbeddingConfig(output_version=next_embed)
    generator = EmbeddingGenerator(config)

    embeddings = generator.generate_embeddings(chunks_data)

    validator = EmbeddingValidator(config)
    report = validator.validate(embeddings)
    report["collection_name"] = args.collection_name

    with open(
        metrics_dir / "embedding_validation_report.json", "w", encoding="utf-8"
    ) as f:
        json.dump(report, f, indent=2)

    if report["is_valid"]:
        print("Embeddings passed validation!")
        output_file = output_dir / "embeddings.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([json.loads(e.model_dump_json()) for e in embeddings], f, indent=2)
        print(f"Saved to {output_file}")
    else:
        print("Validation Failed. Check report.")


if __name__ == "__main__":
    main()
