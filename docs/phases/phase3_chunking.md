# Phase 3: Semantic Chunking

## Overview
This phase takes clean, processed documentation and segments it into semantic chunks suitable for embedding and vector retrieval in a RAG system. The objective is to maintain logical boundaries (like code blocks, tables, and paragraphs) while respecting LLM context window limits.

## Implementation Details

### 1. Section Parsing & Atomic Blocks
The document is split by Markdown headings (H1-H6), building a semantic hierarchy to preserve context. Within each section, text is grouped into atomic blocks. To prevent chopping code or data tables in half, the chunker first identifies code blocks and tables. These atomic blocks are treated as indivisible units during the token budgeting phase. If a code block exceeds the maximum token limit, it is flagged as an oversized chunk rather than being violently split.

### 2. Budgeting & Overlapping
Blocks are grouped into chunks up to a soft token limit. Consecutive chunks share overlap blocks (a defined token threshold) to ensure contextual continuity during retrieval.

### 3. Metadata Injection
Each chunk is annotated with critical structural metadata:
- Originating document and heading hierarchy.
- Content flags.
- Parent document lineage and chunking strategy versions.

## Tradeoffs
- **Atomic Preservation vs. Strict Budgets**: By refusing to split code blocks and tables, we guarantee high-quality structural retention. The tradeoff is that some chunks will violate strict token limits, which could truncate context windows downstream if embeddings or generation prompts are too tight.
- **Naive Overlap vs. Semantic Overlap**: The overlap mechanism duplicates the trailing blocks of the previous chunk. While effective, it might unnecessarily duplicate a massive code block if it falls within the overlap window, leading to redundant embedding costs.

## Potential Failure Modes
- **Massive Atomic Blocks**: A highly massive atomic block (e.g., thousands of lines of code) will completely bypass the standard size limits. This can crash downstream tokenizers during the embedding phase.
- **Lost Context in Tiny Chunks**: A tiny paragraph split from its heading may lose its semantic meaning. We combat this via merging rules, but aggressive heading structures might still result in fragmented chunks.
