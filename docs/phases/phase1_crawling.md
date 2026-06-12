# Phase 1: Crawling & Ingestion

## Overview
The crawling pipeline is an asynchronous, depth-aware web crawler designed to systematically explore and ingest documentation pages. It traverses a designated seed up to a configured maximum depth and page limit. To ensure polite traversal and stability, the crawler incorporates rate limiting, request delays, and configurable timeouts.

## Implementation Details

### 1. URL Filtering & Boundaries
During the crawl, the system extracts all internal and external links from the parsed HTML and Markdown. The URL filtering component evaluates discovered URLs based on allowed domains, regex exclusion patterns, and required path keywords. This generic design allows the crawler to adapt to any documentation site without hardcoding domain-specific rules.

### 2. Markdown Conversion
The crawler converts the Document Object Model (DOM) into semantic Markdown immediately upon fetching. It attempts to extract the main title and preserves textual elements, code blocks, lists, and tables natively. 

### 3. Versioning
All output artifacts are strictly versioned. When a crawl completes, a new semantic version namespace is allocated. Metadata about the crawl (duration, pages fetched, bytes transferred) is persisted along with the raw HTML and Markdown assets.

## Tradeoffs
- **Naive Markdown Extraction**: By relying on a generic markdown converter, the system initially captures some unnecessary navigation elements (sidebars, footers). This is an explicit tradeoff to maintain a purely domain-agnostic crawler, delegating site-specific noise removal to the subsequent Processing phase.

## Potential Failure Modes
- **Aggressive Rate Limits**: If a site employs aggressive rate limiting or bot protection, the crawler may encounter HTTP 403 or timeouts.
- **Infinite Traversal Loops**: Sites with dynamic or cyclical linking structures could trap the crawler. Maximum depth and total page limits are enforced as critical safety bounds to prevent infinite loops.
