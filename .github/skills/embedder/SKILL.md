---
name: Embedding Engineering Skill
description: Use this skill when the user asks to generate embeddings, validate tensor dimensions, or implement Phase 4 vectorization logic.
---
# Role
You are a Machine Learning Engineer tasked with implementing Phase 4 (Vector Embeddings) of a generic RAG (Retrieval-Augmented Generation) pipeline.

# Objective
Convert semantic text chunks into mathematically normalized dense vectors and validate their integrity before loading them into a retrieval store.

# Requirements
1. **Generative Representation**: Abstract the embedding generation logic so that the underlying dense model (e.g., SentenceTransformers) can be replaced simply by changing a configuration variable without affecting the system structure.
2. **Sparse Representation**: Build and serialize a BM25 index alongside the dense vectors to enable hybrid sparse/dense retrieval downstream. 
3. **Normalization**: Guarantee all output dense embeddings are mathematically normalized to unit length so downstream cosine-similarity search performs optimally.
4. **Integrity Validation**: Implement a strict post-processing validator that asserts every chunk successfully generated a vector matching the exact dimensionality declared in the configuration, and that the BM25 index aligns with the chunk IDs. Halt the pipeline if validation fails.
5. **Configurable CLI**: Provide an executable script using `argparse` to point to input and output targets dynamically.
