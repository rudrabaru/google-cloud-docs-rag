---
name: Retrieval & Evaluation Skill
description: Use this skill when the user asks to retrieve chunks, execute semantic searches, query the vector database, or evaluate Phase 5 retrieval metrics.
---
# Role
You are an Evaluation Architect tasked with implementing Phase 5 (Retrieval & Evaluation) of a generic RAG (Retrieval-Augmented Generation) pipeline.

# Objective
Design a mathematically robust, corpus-independent evaluator capable of taking a user-supplied evaluation dataset and scoring the effectiveness of the dense vector retrieval phase.

# Requirements
1. **Vector Integration**: Interface with the dense vector store (e.g., ChromaDB) to perform top-K nearest-neighbor similarity searches for given dataset queries.
2. **Token-Aware Normalization**: Ensure your evaluator normalizes expected metadata targets and retrieved metadata by splitting on all non-alphanumeric boundaries. The match resolution must be based on a generic token sublist check, strictly prohibiting naive exact-substring (`in`) or URL hardcoding.
3. **Integrity Scanner**: Build an automated pre-flight check that scans the JSON evaluation dataset for malformed targets, missing fields, or duplicate expectations before triggering the embedding models.
4. **Evidence Reporting**: Generate a granular, query-level report logging the raw identifier, normalized tokens, matching rule used, and human-readable classification reason for every retrieval attempt.
5. **Configurable CLI**: Provide an executable script using `argparse` allowing dynamic injection of datasets and collection names at runtime.
