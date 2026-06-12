# Phase 5: Retrieval & Evaluation

## Overview
This final phase represents the intersection between indexing data and testing its semantic retrieval accuracy. It relies on a mathematical vector store (e.g., ChromaDB) and a strictly generic evaluation framework to measure the effectiveness of the entire RAG pipeline.

## Implementation Details

### 1. Vector Search
Embeddings and their associated semantic metadata are loaded into a scalable vector store. Given a natural-language query, it retrieves the Top-K chunks closest in distance metric space.

### 2. Token-Aware Generic Evaluation
The evaluation framework determines whether retrieved chunks match expected documentation answers. To enforce absolute corpus independence:
- Evaluator normalizes expected targets and retrieved metadata by tokenizing arrays by non-alphanumeric delimiters.
- It performs Token Sublist Matching instead of strict string matching.
- It generates precise metrics (`Recall@K`, `MRR`) alongside deeply structured evidence reports detailing exact reasons for match success/failures.

### 3. Automated Integrity Checks
Before any evaluation run, an automated scanner audits the user-provided evaluation dataset for malformed entries, missing tags, and duplication. This guarantees that evaluation failures map strictly to RAG deficiencies, not dataset formatting errors.

## Tradeoffs
- **Dense Retrieval Only (V1)**: The baseline system relies purely on semantic dense vectors. It may miss exact-keyword searches that a sparse retrieval algorithm (like BM25) would catch easily.
- **Top-K Limitations**: Without a secondary cross-encoder re-ranking step, the results rely purely on the bi-encoder spatial grouping, which might dilute context for highly nuanced queries.

## Potential Failure Modes
- **False Negatives in Substring Matches**: Even with robust Token-Aware arrays, highly generic chunk metadata might coincidentally match incorrect targets if the dataset queries are under-specified.
- **Recall Drift**: Changes in the chunking parameters (Phase 3) inherently disrupt the embedding vectors (Phase 4), leading to massive shifts in Retrieval scores if not constantly tracked via Evaluation matrices.
