import sys
import os
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing.cleaner import DocumentCleaner
from scripts.version_utils import get_latest_version, get_next_version


def main():
    parser = argparse.ArgumentParser(
        description="Run Phase 2: Document Processing & Cleaning"
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="raw_docs",
        help="Directory containing raw crawled docs.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="processed_docs",
        help="Directory for cleaned docs.",
    )
    args = parser.parse_args()

    raw_base = Path(args.input_dir)
    processed_base = Path(args.output_dir)

    # Get the latest raw_docs version
    latest_raw = get_latest_version(raw_base)
    if latest_raw == "v0":
        print(f"Error: No raw documents found in {args.input_dir}")
        return

    input_dir = raw_base / latest_raw
    print(f"Using raw documents from: {input_dir}")

    # Determine the next processed_docs version
    next_processed = get_next_version(processed_base)
    output_dir = processed_base / next_processed
    metrics_dir = output_dir / "metrics"

    print(f"Starting Phase 2 Processing -> Output Version: {next_processed}")

    cleaner = DocumentCleaner(
        input_dir=input_dir, output_dir=output_dir, metrics_dir=metrics_dir
    )
    cleaner.process_all()


if __name__ == "__main__":
    main()
