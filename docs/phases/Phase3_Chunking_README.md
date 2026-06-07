# Phase 3: Semantic Document Chunking

This phase takes the clean, processed documentation and segments it into semantic chunks suitable for embedding and vector retrieval in a RAG system. The objective is to maintain logical boundaries (like code blocks, tables, and paragraphs) while respecting LLM context window limits.

## Overview

The `DocumentChunker` splits large markdown documents into smaller `ChunkMetadata` units. The process involves:
1. **Section Parsing**: The document is split by Markdown headings (H1-H6), building a `heading_path` hierarchy to preserve context.
2. **Block Extraction**: Within each section, text is grouped into atomic blocks (Code, Tables, Paragraphs).
3. **Budgeting & Grouping**: Blocks are grouped into chunks up to a soft token limit (e.g., 600 tokens).
4. **Overlapping**: Consecutive chunks share overlap blocks (e.g., 125 tokens) to ensure contextual continuity.
5. **Metadata Injection**: Each chunk is annotated with `document_version`, `chunk_version`, token counts, and content flags (`contains_code`, `table_chunk`).

Outputs are saved in `chunks/vN/` as individual JSON files for each chunk. The chunking summary is saved to `reports/chunking_vN/`.

## Implementation Details

### 1. Atomic Blocks
To prevent chopping code or data tables in half, the chunker first identifies ````code```` blocks and `| tables |`. These atomic blocks are treated as indivisible units during the token budgeting phase. If a code block exceeds the maximum token limit, it is flagged as an `oversized_chunk` rather than being violently split.

### 2. Version Lineage
To ensure end-to-end traceability, chunks store two distinct version markers:
- `document_version`: The version of the `processed_docs/vN` file it was derived from.
- `chunk_version`: The version of the chunking rules applied to generate this specific output.

### 3. Tradeoffs
- **Atomic Preservation vs. Strict Budgets**: By refusing to split code blocks and tables, we guarantee high-quality structural retention. The tradeoff is that some chunks will violate the `max_chunk_tokens` strict limit, which could truncate context windows downstream if embeddings or generation prompts are too tight.
- **Naive Overlap vs. Semantic Overlap**: The overlap mechanism simply duplicates the trailing blocks of the previous chunk. While effective, it might unnecessarily duplicate a huge code block if it falls within the overlap window, leading to redundant embedding costs.

### 4. Potential Failure Modes
- **Massive Atomic Blocks**: A 5,000-token JSON example block will completely bypass the standard size limits. This can crash downstream tokenizers during the embedding phase.
- **Lost Context in Tiny Chunks**: A tiny paragraph split from its heading may lose its semantic meaning. We combat this via `_merge_tiny_chunks()`, but aggressive heading structures might still result in fragmented chunks.
- **Tokenizer Drift**: The `TokenCounter` uses `tiktoken` (cl100k_base). If the downstream generation LLM uses a radically different tokenizer (e.g., Llama 3 or Gemini), our token limits might underestimate or overestimate the true size.
