# Generic Retrieval-Augmented Generation (RAG) Framework

## Overview
This repository contains a modular, fully generalized Retrieval-Augmented Generation (RAG) pipeline. Designed with strict corpus independence, the system requires no hardcoded domain knowledge, specific URLs, or predefined keyword heuristics. It processes arbitrary documentation websites into structurally preserved, semantically dense vectors for high-accuracy retrieval.

## Core Architectural Principles
1. **Corpus Independence**: Core pipeline behavior is determined by structural evidence, metadata, and measurable content characteristics, never by source identity.
2. **Structural Preservation**: The system explicitly preserves heading hierarchy, code blocks, and semantic grouping rather than relying solely on raw token limits.
3. **Evaluation-Driven Optimization**: Retrieval quality is benchmarked systematically using token-aware sublist mapping against reproducible evaluation datasets.
4. **Artifact Versioning**: Every phase generates strictly versioned outputs (`v1`, `v2`) containing primary artifacts, metadata manifests, and validation reports to ensure systemic traceability.

## Pipeline Architecture
The system operates sequentially through five primary execution phases, culminating in an independent evaluation layer.

### Phase 1: Crawling & Ingestion
An asynchronous, depth-aware HTTP crawler that traverses specified domains based on strict rate-limiting and boundary configurations. It converts raw DOM structures directly into semantic Markdown, extracting links and base text while isolating initial navigation elements.
* **Execution**: `python scripts/run_crawler.py`

### Phase 2: Heuristic Cleaning & Processing
Refines the raw Markdown through algorithmic content density analysis. It calculates text-to-link ratios and evaluates structural signatures to mathematically excise boilerplate, sidebars, and footers without removing vital code blocks or core content.
* **Execution**: `python scripts/run_processing.py`

### Phase 3: Semantic Chunking
Partitions processed documents based on AST-parsed header depths (`#`, `##`). It prioritizes semantic completeness, ensuring chunks maintain their hierarchical lineage (e.g., `Module > Submodule > Concept`) for enhanced LLM context delivery.
* **Execution**: `python scripts/run_chunking.py`

### Phase 4: Vector Embedding
Transforms semantic chunks into high-dimensional vector representations using robust Transformer models. Incorporates strictly-typed Pydantic validation to ensure tensor dimension integrity and generates automated validation manifests prior to database persistence.
* **Execution**: `python scripts/run_embedding.py`

### Phase 5: Retrieval & Database
Manages batch ingestion into a persistent ChromaDB instance. The dense retrieval module calculates cosine similarity and L2 distances to return highly relevant context sections in response to natural language queries.
* **Execution**: `python scripts/run_retrieval.py`

### Phase 6: Systematic Evaluation
A dedicated benchmarking suite that evaluates the retrieval pipeline against predefined, version-controlled datasets. It outputs rigorous metrics (Recall@K, MRR) and detailed evidence reports for iterative optimization.
* **Execution**: `python scripts/run_evaluation.py`

### Phase 7: Generation & LLM Routing
The generation wrapper that constructs optimized prompts within strict token budgets. It features automatic Fallback Routing (e.g., dynamically falling back to Groq if Gemini hits rate limits) and supports LLM-as-a-judge for evaluating answer faithfulness.
* **Execution**: `python scripts/run_generation.py`

### Phase 8: Conversational RAG & Streaming API
An advanced frontend-ready integration layer. It features a FastAPI server serving real-time SSE (Server-Sent Events) streaming, multi-turn chat history context injection, and Hybrid Search (combining Dense Chroma vectors with Sparse BM25 scoring via Reciprocal Rank Fusion).
* **Execution**: `python src/api/main.py`

### Observability Dashboard
A real-time Streamlit dashboard that visualizes token usage, latency bottlenecks, chunk retention, and ingestion statistics by parsing the versioned JSON manifests.
* **Execution**: `streamlit run scripts/dashboard.py`

## Repository Structure
```text
├── .github/skills/      # Modular AI-agent instructions dictating phase-specific architecture
├── docs/phases/         # Detailed engineering specifications for each pipeline phase
├── evaluation_datasets/ # Version-controlled benchmark JSON configurations
├── scripts/             # CLI execution scripts for triggering pipeline phases
├── src/                 # Core logic modules (crawling, processing, chunking, embedding, retrieving)
└── AGENTS.md            # Foundational system rules and development constraints
```

## System Requirements
- Python 3.12+
- Persistent storage capability for local ChromaDB SQLite instances
- CPU/GPU overhead for localized Transformer model execution
