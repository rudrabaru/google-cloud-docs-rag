# Phase 2: Processing & Validation

## Overview
This phase cleans and validates raw Markdown documents generated during ingestion. It removes boilerplate, duplicate blocks, and navigation artifacts without relying on corpus-specific keyword filters, ensuring a high-quality, dense signal for downstream chunking.

## Implementation Details

### 1. Multi-Signal Boilerplate Removal
The modern cleaning pipeline relies strictly on generic structural, statistical, and semantic signals. It parses the document line by line, evaluating blocks across several dimensions:
- **Document Frequency**: How often a normalized block appears across the entire corpus.
- **Positioning**: Where the block is physically located (edge vs. middle of the document).
- **Link Density**: The ratio of hyperlink tokens to textual tokens.
- **Information Density**: The presence of substantive text vs short navigational stubs.
- **Structural Context**: The physical neighborhood of a block.
- **Content Diversity**: The ratio of unique vocabulary to total vocabulary.

### 2. Confidence-Tiered System
Blocks are removed based on a Confidence-Tiered system where multiple independent signals must agree before dropping content. This system explicitly protects code blocks, tables, and heading structures, enabling the cleaner to process any documentation corpus generically.

### 3. Deduplication and Validation
The pipeline detects and eliminates exact text duplicates using cryptographic hashing. Furthermore, it ensures the cleaned document meets minimal length and structural requirements.

## Tradeoffs
- **Signal Heuristics vs. Perfect Accuracy**: By relying on statistical density signals rather than exact keywords, we trade absolute precision for universal generalization. A uniquely formatted link-dense but valid API reference table might occasionally score high for noise.
- **Line-by-Line Evaluation vs. DOM Context**: The cleaner works on parsed Markdown, lacking the original HTML DOM tree. This means we cannot simply drop specific semantic HTML tags, making the heuristic scoring mathematically complex but entirely decoupling the logic from web development standards.

## Potential Failure Modes
- **Aggressive False Positives**: Valid content might trigger a high boilerplate score and get erroneously removed if the confidence tiers are configured too strictly.
- **Markdown Corruption**: Edge-case parsing bugs in the markdown conversion from the previous phase might confuse the content validator, leading to wholesale document rejection.
