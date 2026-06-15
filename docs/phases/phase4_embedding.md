# Phase 4: Vector Embedding

## Overview
Phase 4 converts the semantic chunks generated in Phase 3 into high-dimensional vector representations using Transformer models. These mathematical representations capture the semantic meaning of the text, enabling dense similarity retrieval.

## Implementation Details

### 1. Configurable Batch Generation
The embedding module utilizes `sentence-transformers` and dynamically loads the specified model onto the available hardware (CPU/GPU). Chunks are processed in configurable batches to optimize memory utilization.

### 2. Strongly-Typed Mapping
Raw chunk dictionaries are instantiated into strict Pydantic models (`ChunkMetadata`). The resulting vectors are appended, creating robust `EmbeddedChunk` objects. This prevents downstream type-errors and ensures serialization integrity.

### 3. In-Memory Validation
Before the vectors are committed to disk, a validation mechanism asserts matrix dimensions against expected model outputs, checks for dead (`0.0` norm) vectors, and generates a validation report. This acts as our safety manifest.

## Tradeoffs
- **Local Compute Bound**: Running dense embedding models locally without quantization can be computationally heavy for large corpora, relying heavily on local hardware specifications.
- **Model Lock-in**: The vector dimensions are tied explicitly to the model chosen (e.g., `all-MiniLM-L6-v2`). Changing models requires full re-embedding of the entire corpus.

## Potential Failure Modes
- Out-Of-Memory (OOM) errors if `batch_size` is set too high for the available hardware.
- Missing HuggingFace API tokens triggering rate limits during the initial model weight downloads.
- `datetime` JSON serialization failures due to complex metadata boundaries (resolved via specific Pydantic dump methods).
