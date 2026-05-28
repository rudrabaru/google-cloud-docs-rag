#!/usr/bin/env python
"""
Debug script to test Crawl4AI and inspect the response structure.
Run this to diagnose what attributes are available on the CrawlResult.
"""

import asyncio
import json
from crawl4ai import AsyncWebCrawler


async def debug_crawl():
    """Test crawl and print detailed result information."""
    
    test_url = "https://docs.cloud.google.com/load-balancing/docs/load-balancing-overview"
    
    print("=" * 80)
    print("CRAWL4AI DEBUG TEST")
    print("=" * 80)
    print(f"URL: {test_url}\n")
    
    try:
        async with AsyncWebCrawler(timeout=30) as crawler:
            print("Crawling...")
            result = await crawler.arun(test_url)
            
            # Check for various possible timing attributes
            elapsed = "unknown"
            if hasattr(result, 'elapsed_time'):
                elapsed = f"{result.elapsed_time:.2f}s"
            elif hasattr(result, 'time_taken'):
                elapsed = f"{result.time_taken:.2f}s"
            
            print(f"✓ Crawl completed in {elapsed}")
            print(f"✓ Status code: {result.status_code if hasattr(result, 'status_code') else 'unknown'}")
            print(f"\n" + "=" * 80)
            print("RESULT ATTRIBUTES")
            print("=" * 80)
            
            # List all attributes
            attributes = dir(result)
            important_attrs = [
                'markdown', 'markdown_content', 'cleaned_html', 'html',
                'links', 'title', 'description', 'url', 'status_code',
                'media', 'metadata', 'content', 'text'
            ]
            
            print("\nImportant attributes:")
            for attr in important_attrs:
                if hasattr(result, attr):
                    value = getattr(result, attr)
                    if isinstance(value, str):
                        preview = value[:100] if value else "(empty)"
                        print(f"  ✓ {attr}: {preview}...")
                    elif isinstance(value, dict):
                        print(f"  ✓ {attr}: dict with {len(value)} keys")
                        if value:
                            print(f"      Keys: {list(value.keys())[:5]}")
                    elif isinstance(value, list):
                        print(f"  ✓ {attr}: list with {len(value)} items")
                        if value and isinstance(value[0], str):
                            print(f"      First item: {value[0][:100]}")
                    else:
                        print(f"  ✓ {attr}: {type(value).__name__}")
                else:
                    print(f"  ✗ {attr}: NOT AVAILABLE")
            
            print("\n" + "=" * 80)
            print("MARKDOWN CONTENT")
            print("=" * 80)
            
            # Try to get markdown
            markdown = None
            if hasattr(result, 'markdown') and result.markdown:
                markdown = result.markdown
                print("✓ Using result.markdown")
            elif hasattr(result, 'markdown_content') and result.markdown_content:
                markdown = result.markdown_content
                print("✓ Using result.markdown_content")
            elif hasattr(result, 'cleaned_html') and result.cleaned_html:
                markdown = result.cleaned_html
                print("✓ Using result.cleaned_html")
            
            if markdown:
                word_count = len(markdown.split())
                lines = len(markdown.split('\n'))
                print(f"  - Word count: {word_count}")
                print(f"  - Line count: {lines}")
                print(f"\nFirst 500 characters:\n{markdown[:500]}\n")
            else:
                print("✗ Could not find markdown content!")
            
            print("=" * 80)
            print("TEST COMPLETE")
            print("=" * 80)
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_crawl())
