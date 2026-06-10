# Phase 1: Raw Crawled Documents

This phase describes the automated ingestion and storage of raw documentation crawled from source websites. The objective is to efficiently explore the documentation graph, fetch raw web pages, extract content natively into markdown format, and retain comprehensive structural metadata without any transformative manipulation.

## Overview

The crawling pipeline is an asynchronous, depth-aware web crawler designed to systematically explore technical documentation pages. It traverses the website up to a configured maximum depth and page limit. To ensure polite traversal and stability, the crawler incorporates rate limiting, request delays, and configurable timeouts.

The raw documents are stored securely as a dual-file pair for each discovered page, preserving both the raw HTML/text and its structural context in a versioned structure. Crawl reports and manifests are stored alongside the data.

## Implementation Details

### 1. Link Discovery & Filtering
During the crawl, the system extracts all internal and external links from the parsed HTML and Markdown. The URL filtering component evaluates discovered URLs based on allowed domains, regex exclusion patterns, and required path keywords. This generic design allows the crawler to adapt to any documentation site (e.g., AWS, Azure, internal wikis, open-source projects) without hardcoding domain-specific rules.

### 2. Markdown Extraction
The crawler converts the Document Object Model (DOM) into semantic Markdown immediately upon fetching. It attempts to extract the main title and preserves textual elements, code blocks, lists, and tables natively. 

### 3. File Formats & Versioning
For every crawled page, two logical files are generated and stored side-by-side using safe URL path representations inside a versioned storage mechanism:
- **JSON Metadata**: Stores URL, title, markdown content, word count, and outgoing links.
- **Markdown Text**: Contains the human-readable standalone markdown.

### 4. Tradeoffs
- **Network Overhead vs. Completeness**: Fetching and parsing every page asynchronously is network-intensive. We trade speed for a complete offline graph of the documentation.
- **Naive Markdown Extraction**: By relying on the crawler's generic markdown converter, we capture some unnecessary navigation elements (sidebars, footers). This is a tradeoff to maintain a purely domain-agnostic crawler, delegating noise removal to Phase 2.

### 5. Potential Failure Modes
- **Crawler Timeouts & Rate Limits**: If a site employs aggressive rate limiting or bot protection, the crawler may encounter HTTP 403 or timeouts.
- **Infinite Traversal Loops**: Sites with dynamic or cyclical linking structures could trap the crawler. Maximum depth and total page limits are critical safety bounds to prevent this.
- **Over-Aggressive URL Filtering**: Misconfigured required keywords or exclusion patterns might silently skip valid documentation pages, leading to an incomplete corpus.
