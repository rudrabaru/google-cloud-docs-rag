"""
Main crawler module using Crawl4AI for deep web crawling.
Extracts structured markdown content and metadata from web pages.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import logging

# pyrefly: ignore [missing-import]
from crawl4ai import AsyncWebCrawler, CrawlResult
from .metadata import CrawledDocument, CrawlConfig, CrawlMetrics
from .filters import URLFilter, ConfigurableURLFilter


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebCrawler:
    """Main crawler orchestrator using Crawl4AI."""
    
    def __init__(
        self,
        config: CrawlConfig,
        url_filter: Optional[URLFilter] = None,
        output_dir: str = "./raw_docs",
    ):
        """
        Args:
            config: CrawlConfig with crawl parameters
            url_filter: URLFilter instance (if None, creates permissive filter)
            output_dir: Directory to save crawled documents
        """
        self.config = config
        self.url_filter = url_filter or URLFilter()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics = CrawlMetrics()
        self.crawled_docs: List[CrawledDocument] = []
        self.queue: List[tuple[str, int]] = [(config.start_url, 0)]  # (url, depth)
    
    async def crawl(self) -> List[CrawledDocument]:
        """
        Execute the crawl.
        
        Returns:
            List of CrawledDocument objects
        """
        start_time = time.time()
        logger.info(f"Starting crawl from {self.config.start_url}")
        logger.info(f"Config: max_depth={self.config.max_depth}, max_pages={self.config.max_pages}")
        
        try:
            async with AsyncWebCrawler(timeout=self.config.timeout_seconds) as crawler:
                processed_urls = set()
                
                while self.queue and len(self.crawled_docs) < self.config.max_pages:
                    url, depth = self.queue.pop(0)
                    
                    # Skip if already processed
                    if url in processed_urls:
                        continue
                    processed_urls.add(url)
                    
                    # Check filters
                    if not self.url_filter.should_crawl(url, reason_log=True):
                        self.metrics.total_urls_filtered += 1
                        continue
                    
                    self.metrics.total_urls_attempted += 1
                    logger.info(f"[{depth}] Crawling: {url}")
                    
                    # Crawl the page
                    doc = await self._crawl_page(crawler, url, depth)
                    
                    if doc:
                        self.crawled_docs.append(doc)
                        self.metrics.total_urls_crawled += 1
                        self.url_filter.mark_crawled(url)
                        
                        # Extract and queue new URLs (respecting depth limit)
                        if depth < self.config.max_depth:
                            new_urls = self._extract_links(url, doc.markdown_content)
                            for new_url in new_urls:
                                if new_url not in processed_urls:
                                    self.queue.append((new_url, depth + 1))
                    else:
                        self.metrics.total_urls_failed += 1
                    
                    # Respect rate limiting
                    await self._async_sleep(self.config.delay_seconds)
        
        except Exception as e:
            logger.error(f"Crawl failed with error: {e}")
            raise
        
        finally:
            end_time = time.time()
            self.metrics.crawl_duration_seconds = end_time - start_time
            self._finalize_metrics()
            logger.info(str(self.metrics))
        
        return self.crawled_docs
    
    async def _crawl_page(self, crawler, url: str, depth: int) -> Optional[CrawledDocument]:
        """
        Crawl a single page.
        
        Args:
            crawler: AsyncWebCrawler instance
            url: URL to crawl
            depth: Crawl depth
        
        Returns:
            CrawledDocument if successful, None if failed
        """
        try:
            result: CrawlResult = await crawler.arun(url)
            
            if result.status_code != 200:
                logger.warning(f"Status code {result.status_code} for {url}")
                return None
            
            title = self._extract_title(result)
            markdown_content = None
            
            # Try different possible attributes
            if hasattr(result, 'markdown') and result.markdown:
                markdown_content = result.markdown
            elif hasattr(result, 'markdown_content') and result.markdown_content:
                markdown_content = result.markdown_content
            elif hasattr(result, 'cleaned_html') and result.cleaned_html:
                markdown_content = result.cleaned_html
            elif hasattr(result, 'html') and result.html:
                markdown_content = result.html
            
            if not markdown_content:
                logger.warning(f"No markdown content extracted from {url}")
                logger.debug(f"Result attributes: {dir(result)}")
                return None
            
            word_count = len(markdown_content.split())
            
            # Extract links for future crawling
            links = self._extract_links(url, markdown_content, getattr(result, 'links', None))
            
            doc = CrawledDocument(
                url=url,
                title=title,
                markdown_content=markdown_content,
                crawl_depth=depth,
                crawled_at=datetime.utcnow(),
                outgoing_links=links,
                word_count=word_count,
                status_code=200,
            )
            
            # Save to disk (both JSON and Markdown)
            self._save_document(doc)
            
            logger.info(f"[OK] Crawled {url} ({word_count} words)")
            return doc
        
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _extract_title(self, result: CrawlResult) -> str:
        """Extract page title from crawl result."""
        # Try metadata first (most reliable)
        if hasattr(result, 'metadata') and result.metadata and isinstance(result.metadata, dict):
            if 'title' in result.metadata:
                return result.metadata['title']
        
        # Fallback: extract from markdown (first heading)
        if hasattr(result, 'markdown') and result.markdown:
            lines = result.markdown.split('\n')
            for line in lines:
                if line.startswith('# '):
                    return line.replace('# ', '').strip()
        
        # Last resort: use URL
        return urlparse(result.url if hasattr(result, 'url') else "").path.split('/')[-1]
    
    def _extract_links(self, base_url: str, markdown: str, crawl_links: Optional[dict] = None) -> List[str]:
        """
        Extract links from markdown or Crawl4AI result.
        
        Args:
            base_url: Base URL for resolving relative links
            markdown: Markdown content to extract links from
            crawl_links: Links dict from CrawlResult with 'internal' and 'external' keys
        
        Returns:
            List of absolute URLs
        """
        links_set = set()
        
        try:
            if crawl_links and isinstance(crawl_links, dict):
                internal_links = crawl_links.get('internal', [])
                if isinstance(internal_links, list):
                    for link in internal_links:
                        if isinstance(link, str) and link.strip():
                            links_set.add(link.strip())
                
                external_links = crawl_links.get('external', [])
                if isinstance(external_links, list):
                    for link in external_links:
                        if isinstance(link, str) and link.strip():
                            links_set.add(link.strip())
        except Exception as e:
            logger.debug(f"Error extracting Crawl4AI links: {e}")
        
        # Also extract links from markdown (markdown syntax [text](url))
        try:
            import re
            markdown_links = re.findall(r'\[.+?\]\((.+?)\)', markdown)
            for link in markdown_links:
                if link and isinstance(link, str):
                    abs_url = urljoin(base_url, link.strip())
                    links_set.add(abs_url)
        except Exception as e:
            logger.debug(f"Error extracting markdown links: {e}")
        
        # Convert to sorted list for consistency
        return sorted(list(links_set))
    
    def _save_document(self, doc: CrawledDocument):
        # Save to disk
        filename_safe = urlparse(doc.url).path.strip('/').replace('/', '_')
        if not filename_safe:
            filename_safe = "index"
        
        json_path = self.output_dir / f"{filename_safe}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(doc.model_dump(mode='json'), f, indent=2, default=str)
        
        md_path = self.output_dir / f"{filename_safe}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {doc.title or 'Untitled'}\n\n")
            f.write(f"**Source:** {doc.url}\n\n")
            f.write(doc.markdown_content)
    
    def _finalize_metrics(self):
        """Calculate final metrics."""
        if self.crawled_docs:
            total_words = sum(doc.word_count for doc in self.crawled_docs)
            self.metrics.total_words = total_words
            self.metrics.average_page_words = total_words / len(self.crawled_docs)
    
    @staticmethod
    async def _async_sleep(seconds: float):
        """Async sleep for rate limiting."""
        import asyncio
        await asyncio.sleep(seconds)
    
    def save_summary(self, filename: str = "crawl_summary.json", output_dir: Optional[str] = None):
        """Save crawl summary with all metadata."""
        summary = {
            "config": self.config.model_dump(),
            "metrics": self.metrics.model_dump(),
            "documents": [doc.model_dump(mode='json') for doc in self.crawled_docs],
            "filter_report": self.url_filter.get_filter_report(),
        }
        
        target_dir = Path(output_dir) if output_dir else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / filename
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Summary saved to {path}")
        return path


# Generic convenience function for crawling
async def run_crawler(
    start_url: str,
    allowed_domains: List[str] = None,
    required_keywords: List[str] = None,
    exclude_patterns: List[str] = None,
    max_depth: int = 3,
    max_pages: int = 100,
    output_dir: str = "./raw_docs",
    report_dir: Optional[str] = None,
) -> List[CrawledDocument]:
    """
    Run the crawler with generic configuration.
    
    Args:
        start_url: Starting URL
        allowed_domains: List of allowed domains
        required_keywords: Path keywords to require
        exclude_patterns: Regex patterns to exclude
        max_depth: Maximum crawl depth
        max_pages: Maximum pages to crawl
        output_dir: Output directory
        report_dir: Directory to save the crawl summary report
    
    Returns:
        List of crawled documents
    """
    config = CrawlConfig(
        start_url=start_url,
        max_depth=max_depth,
        max_pages=max_pages,
    )
    
    if exclude_patterns is None:
        exclude_patterns = [
            r".*\.pdf$", r".*\.jpg$", r".*\.png$", r".*\.gif$",
            r".*\.(zip|gz|tar)$", r".*/api-ref/.*", r".*/release-notes$",
            r".*\/search\?.*"
        ]
        
    url_filter = ConfigurableURLFilter(
        allowed_domains=allowed_domains,
        exclude_patterns=exclude_patterns,
        required_path_keywords=required_keywords,
        min_path_length=10,
        allow_pagination=False
    )
    
    crawler = WebCrawler(config, url_filter, output_dir)
    
    docs = await crawler.crawl()
    crawler.save_summary(output_dir=report_dir)
    
    return docs
