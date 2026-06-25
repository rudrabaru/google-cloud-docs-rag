# Phase 1: Crawling & Ingestion

## Overview
The crawling pipeline is an asynchronous, depth-aware web crawler designed to systematically explore and ingest documentation pages. It traverses a designated seed up to a configured maximum depth and page limit. To ensure polite traversal and stability, the crawler incorporates rate limiting, request delays, and configurable timeouts.

## Implementation Details

### 1. Ingestion Strategies
The crawler supports two primary ingestion methods:
- **Depth-First Search (BFS) Crawling**: Navigates from a designated seed URL up to a configured maximum depth, extracting all internal and external links.
- **Sitemap XML Parsing**: Directly fetches and parses standard `sitemap.xml` files. This bypasses BFS constraints and ensures complete site coverage in a single request, eliminating the need to traverse the DOM for link discovery.

### 2. URL Filtering & Boundaries
During the crawl, the system evaluates discovered URLs based on allowed domains, regex exclusion patterns, and required path keywords. This generic design allows the crawler to adapt to any documentation site without hardcoding domain-specific rules.

### 3. Markdown Conversion
The crawler converts the Document Object Model (DOM) into semantic Markdown immediately upon fetching. It attempts to extract the main title and preserves textual elements, code blocks, lists, and tables natively. 

### 3. Versioning
All output artifacts are strictly versioned. When a crawl completes, a new semantic version namespace is allocated. Metadata about the crawl (duration, pages fetched, bytes transferred) is persisted along with the raw HTML and Markdown assets.

## Tradeoffs
- **Naive Markdown Extraction**: By relying on a generic markdown converter, the system initially captures some unnecessary navigation elements (sidebars, footers). This is an explicit tradeoff to maintain a purely domain-agnostic crawler, delegating site-specific noise removal to the subsequent Processing phase.
- **Client-Side Rendering Limits**: The current HTTP-based crawler evaluates static HTML and does not execute JavaScript. Highly dynamic SPAs may require headless browser rendering extensions.

## Potential Failure Modes
- Infinite traversal loops if bounding constraints (depth/allowed domains) are misconfigured.
- Throttling or IP blocking by target domains if rate limits are exceeded.
