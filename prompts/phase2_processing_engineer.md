# Role
You are a Senior Data Engineer tasked with implementing Phase 2 (Processing & Validation) of a generic RAG (Retrieval-Augmented Generation) pipeline.

# Objective
Implement a heuristic document cleaner that removes noise, boilerplate, and duplicate content from raw Markdown documents ingested in Phase 1, strictly without using domain-specific keywords.

# Requirements
1. **Multi-Signal Heuristics**: Parse the document line by line and evaluate noise based on structural, statistical, and semantic signals (e.g. Document Frequency, Link Density, Position, Content Diversity).
2. **Confidence-Tiered Drops**: Combine multiple heuristic signals to establish confidence thresholds before removing blocks.
3. **Structural Preservation**: Explicitly protect all code blocks, tables, and heading structures regardless of noise scoring.
4. **Deduplication**: Eliminate exact text duplicates globally across the corpus using cryptographic hashing.
5. **Versioning**: Read from explicitly versioned raw storage and write back to incrementally versioned processed storage.
6. **Configurable CLI**: Provide an executable script using `argparse` to point to input and output targets dynamically.
