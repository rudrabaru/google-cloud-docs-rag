# Phase 2: Document Cleaning & Validation

This phase describes the processing, cleaning, deduplication, and validation of raw crawled documentation. The objective is to filter out navigation menus, footers, boilerplate, and duplicate pages to ensure only high-quality, dense information is passed to the chunking phase.

## Overview

The cleaning pipeline takes the raw Markdown documents and runs them through an orchestrated series of steps:
1. **Generic Cleaning**: Evaluates content blocks using a multi-signal heuristic pipeline to strip out noise without relying on hardcoded site-specific keywords.
2. **Deduplication**: Detects and eliminates exact text duplicates using cryptographic hashing.
3. **Content Validation**: Ensures the cleaned document meets minimal length and structural requirements (e.g., minimum words, valid markdown).

Outputs are stored securely in versioned directories in both Markdown and JSON formats, with explicit version tracking injected into the metadata.

## Implementation Details

### 1. Multi-Signal Boilerplate Removal
Unlike legacy keyword filters that search for specific phrases like "skip to main content" or "copyright", the modern cleaning pipeline relies strictly on generic structural, statistical, and semantic signals. It parses the document line by line, evaluating blocks across several dimensions:
- **Document Frequency**: How often a normalized block appears across the entire corpus.
- **Positioning**: Where the block is physically located (edge vs. middle of the document).
- **Link Density**: The ratio of hyperlink tokens to textual tokens.
- **Information Density**: The presence of substantive text vs short navigational stubs.
- **Structural Context**: The physical neighborhood of a block (e.g., sandwiched between two navigation menus).
- **Content Diversity**: The ratio of unique vocabulary to total vocabulary.

Blocks are removed based on a **Confidence-Tiered system** where multiple independent signals must agree before dropping content, explicitly protecting code blocks, tables, and heading structures. This enables the cleaner to process any documentation corpus generically.

### 2. Versioned Outputs
The pipeline reads from the raw versioned storage and writes to a new processed versioned storage. Both JSON metadata and Markdown files are written. Crucially, the document version is embedded directly into the metadata payload to guarantee traceability. Highly detailed reports (boilerplate detection, removed blocks, review sets) are generated to allow human auditing of the heuristic decisions.

### 3. Tradeoffs
- **Signal Heuristics vs. Perfect Accuracy**: By relying on statistical density signals rather than exact keywords, we trade absolute precision for universal generalization. A uniquely formatted link-dense but valid API reference table might occasionally score high for noise.
- **Line-by-Line Evaluation vs. DOM Context**: The cleaner works on parsed Markdown, lacking the original HTML DOM tree. This means we cannot simply drop `<nav>` tags, making the heuristic scoring mathematically complex but entirely decoupling the logic from web development standards.

### 4. Potential Failure Modes
- **Aggressive False Positives**: Valid content (like a massive list of related links or API endpoints) might trigger a high boilerplate score and get erroneously removed if the confidence tiers are configured too strictly.
- **Markdown Corruption**: Edge-case parsing bugs in the markdown conversion from Phase 1 might confuse the content validator, leading to wholesale document rejection.
- **Version Skew**: If the input raw version is out of sync with expected content, downstream processing logic may fail or produce invalid outputs.
