import asyncio
from pathlib import Path
from src.crawler.crawl import run_crawler
from scripts.version_utils import get_next_version

async def main():
    base_dir = Path("raw_docs")
    base_dir.mkdir(exist_ok=True)
    
    next_version = get_next_version(base_dir)
    output_dir = base_dir / next_version
    output_dir.mkdir(exist_ok=True)
    
    reports_dir = Path(f"reports/crawling_{next_version}")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Phase 1 Crawler -> Output Version: {next_version}")
    
    # Example config (dynamically passed instead of hardcoded in class)
    await run_crawler(
        start_url="https://docs.cloud.google.com/load-balancing/docs/load-balancing-overview",
        allowed_domains=["docs.cloud.google.com"],
        required_keywords=["load-balancing", "load_balancing", "network-services"],
        max_depth=3,
        max_pages=100,
        output_dir=str(output_dir),
        report_dir=str(reports_dir)
    )
    
    print(f"Phase 1 Complete. Raw documents saved to: {output_dir}")
    print(f"Reports saved to: {reports_dir}")

if __name__ == "__main__":
    asyncio.run(main())
