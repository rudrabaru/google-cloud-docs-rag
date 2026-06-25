# Phase 5: Retrieval & Database

## Overview
Phase 5 loads the validated semantic vectors into a persistent Vector Database (ChromaDB) and exposes a fast, latency-optimized query interface. This allows user queries to mathematically match and retrieve the most relevant sections of the crawled corpus.

## Implementation Details

### 1. Vector Store Management
The `ChromaDBManager` abstracts the complexities of the database. It handles batch ingestion, metadata flattening (e.g., converting hierarchical list arrays to string paths), and persistent storage management. It relies on the generic `embedding_validation_report.json` to configure correct distance metrics.

### 2. Dense Retrieval Queries
The `DenseRetriever` accepts natural language queries, embeds them on the fly using the identical Phase 4 Transformer model, and queries the ChromaDB index using Cosine Similarity or L2 distance. 

### 3. Cross-Encoder Reranking
To improve precision, the retrieval phase incorporates an optional Cross-Encoder reranking step (`OptionalReranker`). When enabled, the system retrieves an expanded candidate pool (e.g., `top_k * 4`) via dense retrieval, then reranks these candidates using a highly accurate cross-encoder model to return the final `top_k`. This achieves a strong balance between dense retrieval speed and cross-encoder accuracy.

### 3. Sublist Token Matching (Evaluation Tracking)
For evaluation pipelines, retrieving documents uses highly accurate token-aware sublist mapping. This ensures benchmarking logic evaluates true hit-rates regardless of string-truncation variations.

## Tradeoffs
- **Metadata Limitations**: ChromaDB strictly limits metadata values to strings, ints, floats, and booleans. Nested structures (like the chunk's hierarchical path) must be flattened, slightly reducing complex metadata querying capabilities.
- **Cold Start Latency**: Instantiating the embedding model and connecting to the Persistent ChromaDB instance incurs a brief cold-start overhead upon the first query.

## Potential Failure Modes
- Mismatched Transformer models between Phase 4 and Phase 5 will result in dimension errors or completely hallucinated similarity scores.
- Querying a non-existent or un-populated database collection will crash the retrieval module.
