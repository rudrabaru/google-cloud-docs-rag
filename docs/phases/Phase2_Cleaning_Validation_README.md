# Phase 2: Document Cleaning & Validation

This phase describes the processing, cleaning, deduplication, and validation of raw crawled documentation. The objective is to filter out navigation menus, footers, boilerplate, and duplicate pages to ensure only high-quality, dense information is passed to the chunking phase.

## Overview

The cleaning pipeline takes the raw Markdown documents and runs them through a `ProcessingPipeline`. This pipeline orchestrates:
1. **GenericCleaner**: Evaluates content blocks using a `ClassificationPipeline` (signal-based heuristic logic) to strip out noise without relying on hardcoded site-specific keywords.
2. **DuplicateRemover**: Detects and eliminates exact text duplicates using MD5 hashing.
3. **ContentValidator**: Ensures the cleaned document meets minimal length and structural requirements (e.g., minimum words, valid markdown).

Outputs are stored securely in `processed_docs/vN/` in both `.md` and `.json` formats, with explicit versioning tracking injected into the metadata.

## Implementation Details

### 1. Signal-Based Classification
Unlike legacy keyword filters that search for "skip to main content" or "copyright", the `ClassificationPipeline` relies on structural signals. It parses the document line by line, scoring blocks based on:
- **Noise Score**: High link density, repetitive short phrases, specific structural patterns common in footers/nav bars.
- **Content Score**: High word count, code blocks, complex formatting.

Blocks with a high noise-to-content ratio are dropped. This enables the cleaner to process GCP, AWS, or Azure documentation generically.

### 2. Versioned Outputs
The pipeline reads from `raw_docs/vX/` and writes to `processed_docs/vY/`. Both `.json` and `.md` files are written. Crucially, the `document_version` is embedded directly into the JSON metadata payload to guarantee traceability.
Reports (processing summaries, deduplication logs) are isolated and saved to `reports/processing_vY/`.

### 3. Tradeoffs
- **Signal Heuristics vs. Perfect Accuracy**: By relying on density signals (like link-to-text ratio) rather than exact keywords, we trade absolute precision for generalization. An incredibly link-dense but valid API reference table might occasionally be scored as "noise" and dropped.
- **Line-by-Line Evaluation vs. DOM Context**: The cleaner works on parsed Markdown, lacking the original HTML DOM tree. This means we cannot simply drop `<nav>` or `<footer>` tags, making the heuristic scoring more complex but the input format much simpler.

### 4. Potential Failure Modes
- **Aggressive False Positives**: Valid content (like a massive list of related links or API endpoints) might trigger a high noise score and get erroneously removed.
- **Markdown Corruption**: Edge-case parsing bugs in the markdown conversion from Phase 1 might confuse the `ContentValidator`, leading to wholesale document rejection.
- **Version Skew**: If the input version `raw_docs/vN` is out of sync with expected content, downstream processing logic may fail or produce invalid chunks.
