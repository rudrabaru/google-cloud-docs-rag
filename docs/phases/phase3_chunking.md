# Phase 3: Semantic Chunking

## Overview
Chunking is the process of partitioning large, processed Markdown documents into smaller, localized segments of text optimized for vector embedding and context windows. The system explicitly prioritizes structural hierarchy over hard token limits.

## Implementation Details

### 1. Structural Hierarchy Parsing
The chunker scans the document using Markdown header depths (`#`, `##`, `###`). It maps the hierarchical path of every block of text, ensuring that when a chunk is isolated, its lineage (e.g., "API Reference > Authentication > JWT") is embedded into its metadata.

### 2. Token-Aware Partitioning
Instead of slicing documents blindly every 500 tokens (which destroys code blocks or sentences), the chunker respects semantic boundaries. It will attempt to keep a section intact. If a section exceeds the token threshold, it breaks it recursively at the paragraph or sentence level, preserving the original header context.

### 3. Code Block Integrity
Code blocks are treated as atomic units. They are rarely split unless absolutely necessary (exceeding maximum token limits).

## Tradeoffs
- **Variable Chunk Sizes**: Because the chunker respects semantic boundaries, the resulting output sizes are highly variable (e.g., some are 100 tokens, others 800 tokens). This can cause slight imbalances in dense retrieval mechanics but drastically improves LLM synthesis quality.
- **Metadata Overhead**: Attaching hierarchical lineage arrays to every chunk inflates the size of the final JSON artifacts.

## Potential Failure Modes
- Extremely large, unbroken code blocks or tables that cannot be partitioned may exceed model context windows or get truncated forcefully.
- Malformed Markdown syntax from Phase 2 could trick the AST parser, resulting in improperly mapped header lineages.
