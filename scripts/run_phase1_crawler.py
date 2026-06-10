import asyncio
from pathlib import Path
from src.crawler.crawl import run_crawler
from scripts.version_utils import get_next_version

async def main():
    base_dir = Path("raw_docs")
    base_dir.mkdir(exist_ok=True)
    
    html_base = Path("raw_html")
    html_base.mkdir(exist_ok=True)
    
    next_version = get_next_version(base_dir)
    
    output_dir = base_dir / next_version
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_dir = html_base / next_version
    html_dir.mkdir(parents=True, exist_ok=True)
    
    metrics_dir = output_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Phase 1 Crawler -> Output Version: {next_version}")
    
    await run_crawler(
        start_url="https://docs.cloud.google.com/load-balancing/docs",
        allowed_domains=["docs.cloud.google.com"],
        required_keywords=["load-balancing/docs"],
        max_depth=9999,
        max_pages=10000,
        soft_limit_pages=1000,
        warning_limit_pages=5000,
        abort_limit_pages=10000,
        output_dir=str(output_dir),
        html_dir=str(html_dir),
        metrics_dir=str(metrics_dir)
    )
    
    print(f"Phase 1 Complete. Raw documents saved to: {output_dir}")
    print(f"Raw HTML saved to: {html_dir}")
    print(f"Metrics saved to: {metrics_dir}")

if __name__ == "__main__":
    asyncio.run(main())
