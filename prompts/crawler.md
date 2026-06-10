Act as a Senior Web Crawling Engineer.

Implement a generic documentation crawler for a provided seed URL.

Objective:

Build a complete corpus of technical documentation by crawling all relevant pages within a defined URL scope. The system must be source-agnostic and work for any generic documentation website (e.g., AWS, Azure, internal wikis).

Requirements:

1. Start from the seed URL.
2. Discover and follow all internal documentation links.
3. Crawl every unique page that belongs to the target documentation section.
4. Maintain a visited URL registry to prevent duplicate crawling.
5. Normalize URLs before storage and comparison.
6. Preserve crawl metadata for every page.

Scope Rules:

* Crawl only URLs that belong to the defined documentation subtree.
* Do not crawl pages outside the documentation scope.
* Do not crawl external domains.
* Do not crawl:
  * PDFs
  * images
  * downloads
  * search pages
  * login pages
  * feedback forms
  * support portals

* Do Not Crawl outgoing links outside of the target documentation subtree.

Content Requirements:

For every crawled page extract:

* URL
* page title
* raw HTML
* cleaned markdown
* discovered links
* crawl timestamp

Quality Requirements:

* Deduplicate URLs.
* Handle redirects correctly.
* Log crawl failures.
* Generate crawl metrics.
* Save crawl manifests and crawl reports.
* Ensure deterministic and reproducible crawling.

Deliverables:

1. Crawling architecture.
2. URL discovery strategy.
3. URL normalization strategy.
4. Deduplication strategy.
5. Crawl metrics and reporting.
6. Full implementation code.

The crawler must be completely generic to support future documentation sources by changing only the seed URL and crawl boundary. Avoid hardcoding any specific product names, website layouts, or domain-specific logic.
