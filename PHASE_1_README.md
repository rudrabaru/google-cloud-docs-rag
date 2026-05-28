# Phase 1: Crawl and Build Raw Corpus

## Overview

Phase 1 crawls Google Cloud Load Balancing documentation and builds a high-quality local dataset. This phase establishes the foundation for all downstream RAG components.

**Target**: 50–300 clean markdown documents from GCP Load Balancing docs  
**Tech Stack**: Python, Crawl4AI, Pydantic, ChromaDB (for later phases)

---

## Project Structure

```
gcp-rag/
├── raw_docs/              # Raw crawled documents (markdown + JSON)
├── processed_docs/        # Cleaned, validated documents
├── chunks/                # (Phase 2) Chunked documents
├── embeddings/            # (Phase 3) Vector embeddings
├── notebooks/
│   └── phase1_inspection.ipynb  # Data exploration & visualization
├── src/
│   ├── crawler/
│   │   ├── crawl.py       # Main crawler using Crawl4AI
│   │   ├── filters.py     # URL filtering logic
│   │   └── metadata.py    # Pydantic schemas
│   └── processing/
│       └── pipeline.py    # Cleaner, deduplicator, validator
├── main.py                # Phase 1 entry point
├── requirements.txt       # Dependencies
└── .gitignore             # Excludes data directories
```

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Phase 1

```bash
python main.py
```

This will:
- Crawl GCP Load Balancing docs (depth=3, max 100 pages)
- Save raw documents to `raw_docs/`
- Process documents (clean, deduplicate, validate)
- Save processed documents to `processed_docs/`
- Generate `processing_reports.json` with detailed metrics

### 3. Inspect Results

Open and run the Jupyter notebook:

```bash
jupyter notebook notebooks/phase1_inspection.ipynb
```

This notebook allows you to:
- Visualize document statistics (word counts, depth distribution)
- Compare raw vs processed documents
- Inspect individual document content
- Verify data quality

---

## Modules

### `src/crawler/crawl.py`

**Main crawler using Crawl4AI for deep web crawling.**

**Key Classes:**
- `WebCrawler` — Orchestrates the crawl with queue-based page discovery
- `crawl_gcp_load_balancing()` — Convenience function for GCP docs

**Features:**
- Deep crawling (configurable depth)
- URL filtering with deduplication
- Markdown extraction and metadata capture
- Rate limiting for respectful crawling
- Comprehensive logging and metrics

**Usage:**
```python
from src.crawler.crawl import crawl_gcp_load_balancing

docs = await crawl_gcp_load_balancing(
    start_url="https://docs.cloud.google.com/load-balancing/docs/load-balancing-overview",
    max_depth=3,
    max_pages=100,
    output_dir="./raw_docs"
)
```

### `src/crawler/filters.py`

**URL filtering to control which pages are crawled.**

**Key Classes:**
- `URLFilter` — Generic URL filtering logic
- `GCPLoadBalancingFilter` — Pre-configured for GCP Load Balancing docs

**Features:**
- Domain allowlisting
- Regex pattern exclusion (PDFs, images, pagination)
- Duplicate detection
- Pagination parameter filtering

**Example:**
```python
from src.crawler.filters import GCPLoadBalancingFilter

url_filter = GCPLoadBalancingFilter()
if url_filter.should_crawl(url):
    # Crawl this URL
    pass
```

### `src/crawler/metadata.py`

**Pydantic schemas for type-safe document metadata.**

**Key Classes:**
- `CrawledDocument` — Schema for crawled page with metadata
- `CrawlConfig` — Configuration for crawler parameters
- `CrawlMetrics` — Metrics from a crawl run

### `src/processing/pipeline.py`

**Content cleaning, deduplication, and validation.**

**Key Classes:**
- `ContentCleaner` — Removes navigation noise and boilerplate
- `DuplicateRemover` — Detects and removes duplicate documents
- `ContentValidator` — Validates document quality (word count, markdown syntax)
- `ProcessingPipeline` — Orchestrates the full processing workflow

**Features:**
- Markdown-aware cleaning (preserves code blocks, tables)
- Hash-based duplicate detection
- Word count validation (min 100, max 15,000 words configurable)
- Markdown syntax validation

**Example:**
```python
from src.processing.pipeline import ProcessingPipeline

pipeline = ProcessingPipeline(
    raw_dir="./raw_docs",
    processed_dir="./processed_docs",
    min_words=100,
    max_words=15000
)

processed_docs = pipeline.process()
pipeline.save_reports()
```

---

## Configuration

### Crawler Parameters (in `main.py`)

```python
crawl_gcp_load_balancing(
    start_url="https://docs.cloud.google.com/load-balancing/docs/load-balancing-overview",
    max_depth=3,              # Crawl depth (3 is usually sufficient)
    max_pages=100,            # Maximum pages to crawl
    output_dir="./raw_docs"   # Output directory
)
```

### Processing Parameters (in `main.py`)

```python
ProcessingPipeline(
    raw_dir="./raw_docs",
    processed_dir="./processed_docs",
    min_words=100,            # Discard if below (usually nav-only pages)
    max_words=15000           # Discard if above (likely auto-generated refs)
)
```

---

## Output

### Raw Documents (`raw_docs/`)

Each crawled page is saved as:
- `{filename}.json` — Full metadata (URL, title, content, links, etc.)
- `{filename}.md` — Markdown content (human-readable)

**Example JSON structure:**
```json
{
  "url": "https://docs.cloud.google.com/load-balancing/docs/overview",
  "title": "Load Balancing Overview",
  "markdown_content": "# Load Balancing Overview\n\n...",
  "crawl_depth": 1,
  "crawled_at": "2026-05-28T...",
  "outgoing_links": ["url1", "url2"],
  "word_count": 1500,
  "status_code": 200
}
```

Also includes:
- `crawl_summary.json` — Overall crawl statistics and config

### Processed Documents (`processed_docs/`)

Cleaned, deduplicated, validated documents:
- `{filename}.json` — Cleaned content with metadata
- `processing_reports.json` — Detailed processing metrics

**Metrics in report:**
```json
{
  "processing_log": {
    "total_input": 100,
    "cleaned": 100,
    "deduplicated": 5,
    "validated": 95,
    "failed": 0
  },
  "deduplication_report": {...},
  "validation_report": {...}
}
```

---

## Typical Workflow

### 1. First Run (Setup Phase)

```bash
# Install dependencies
pip install -r requirements.txt

# Verify setup
python -c "from src.crawler.crawl import crawl_gcp_load_balancing; print('✓ Setup OK')"

# Run crawler on small sample first
# Edit main.py: set max_pages=10 for test
python main.py
```

### 2. Inspect Results

```bash
# Check raw_docs directory
ls raw_docs/ | head -10

# Review processing reports
cat processed_docs/processing_reports.json

# Open inspection notebook
jupyter notebook notebooks/phase1_inspection.ipynb
```

### 3. Full Crawl

```bash
# Edit main.py: set max_pages=100 for full crawl
python main.py

# Monitor progress in terminal logs
```

### 4. Manual Quality Check

```bash
# Review 5-10 processed documents manually
# Check for:
# - Readable markdown
# - No visible junk (menus, footers)
# - Good semantic coherence
```

---

## Troubleshooting

### Crawl Timeouts

If `crawl.py` times out on certain pages:
- Increase `timeout_seconds` in `CrawlConfig`
- Add problematic URLs to `exclude_patterns` in filter

### Low Crawl Coverage

If fewer documents than expected:
- Verify `GCPLoadBalancingFilter` keywords match your docs
- Check `max_depth` — may need to increase to 4
- Review `exclude_patterns` — may be too aggressive

### Processing Failures

If many documents fail validation:
- Check `min_words` and `max_words` thresholds
- Review `processing_reports.json` for validation reasons
- Adjust thresholds and re-run pipeline

### Memory Issues

If running out of memory:
- Reduce `max_pages` to crawl fewer documents initially
- Process in batches instead of all at once

---

## Next Steps

After Phase 1 is complete:

1. **Verify data quality** using inspection notebook
2. **Proceed to Phase 2**: Chunking System
   - Split documents into 500-800 token chunks
   - Preserve semantic boundaries
   - Build chunk metadata

3. **Phase 3**: Embeddings + Vector Database
   - Generate embeddings using `sentence-transformers`
   - Store in ChromaDB
   - Test semantic search

---

## Key Insights

### Why This Approach?

1. **Data Quality First**: RAG quality depends primarily on retrieval quality, which depends on data quality. Phase 1 ensures a clean foundation.

2. **Observable Pipeline**: Every stage saves outputs to disk. You can inspect raw → cleaned → validated documents at any time.

3. **Local-First**: No cloud dependencies initially. Everything runs locally for faster iteration.

4. **Learning-Focused**: Each module is simple and understandable. Avoid frameworks that hide complexity.

### Common Pitfalls

- **Not inspecting**: Always use the inspection notebook. Manual review catches issues automation misses.
- **Premature optimization**: Don't optimize crawl speed until coverage is good.
- **Wrong thresholds**: Word count bounds affect data quality. Adjust after manual inspection.
- **Skipping deduplication**: Sidebar duplicates are common and must be removed.

---

## References

- [Crawl4AI Documentation](https://github.com/unclecode/crawl4ai)
- [Google Cloud Load Balancing Docs](https://docs.cloud.google.com/load-balancing/docs)
- [Pydantic Documentation](https://docs.pydantic.dev)

---

## Contact & Questions

For issues or questions during Phase 1:
1. Check `processing_reports.json` for detailed error logs
2. Review inspection notebook for data quality insights
3. Consult troubleshooting section above

---

**Phase 1 Status**: Ready for crawling  
**Created**: May 28, 2026  
**Last Updated**: May 28, 2026
