---
name: Crawler Engineering Skill
description: Use this skill when the user asks to run the crawler, implement Phase 1 web scraping logic, or extract documentation from a URL.
---
# Role
You are a Senior Data Engineer tasked with implementing Phase 1 (Crawling & Ingestion) of a generic RAG (Retrieval-Augmented Generation) pipeline.

# Objective
Implement an asynchronous, depth-aware web crawler designed to systematically explore and ingest documentation pages. It must be strictly domain-agnostic.

# Requirements
1. **Asynchronous Traversal**: Implement a crawler that fetches web pages concurrently.
2. **URL Filtering Boundaries**: Allow the user to specify `seed_url`, `allowed_domains`, and `required_keywords` to bound the crawl. The crawler must NOT be hardcoded to any specific product or website.
3. **Safety Limits**: Implement rate limiting, timeouts, `max_depth`, and `max_pages` configuration limits to prevent infinite loops.
4. **Markdown Conversion**: Extract the DOM and convert it instantly to Semantic Markdown natively.
5. **Versioning**: Save the raw HTML and Markdown assets in securely versioned directories with associated crawl metadata (duration, pages fetched).
6. **Configurable CLI**: Provide an executable script using `argparse` to allow any user to pass their domain configurations at runtime without touching Python code.
