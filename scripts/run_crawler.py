import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawling.crawl import run_crawler
from scripts.version_utils import get_next_version


async def main():
    parser = argparse.ArgumentParser(description="Run the RAG Document Crawler")
    parser.add_argument(
        "--seed_url",
        type=str,
        required=True,
        help="The seed URL to start crawling from.",
    )
    parser.add_argument(
        "--allowed_domains",
        type=str,
        nargs="+",
        required=True,
        help="List of allowed domains to crawl.",
    )
    parser.add_argument(
        "--required_keywords",
        type=str,
        nargs="*",
        default=[],
        help="Keywords required in the URL path.",
    )
    parser.add_argument("--max_depth", type=int, default=3, help="Maximum crawl depth.")
    parser.add_argument(
        "--max_pages", type=int, default=1000, help="Maximum number of pages to crawl."
    )
    parser.add_argument(
        "--output_dir", type=str, default="raw_docs", help="Base directory for output."
    )
    args = parser.parse_args()

    base_dir = Path(args.output_dir)
    next_version = get_next_version(base_dir)
    output_dir = base_dir / next_version
    html_dir = Path("raw_html") / next_version
    metrics_dir = output_dir / "metrics"

    print(f"Starting Phase 1 Crawler -> Output Version: {next_version}")

    await run_crawler(
        start_url=args.seed_url,
        allowed_domains=args.allowed_domains,
        required_keywords=args.required_keywords,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        output_dir=output_dir,
        html_dir=html_dir,
        metrics_dir=metrics_dir,
    )


if __name__ == "__main__":
    asyncio.run(main())
