---
name: Semantic Chunker Skill
description: Use this skill when the user asks to modify chunking logic, adjust token limits, or debug Phase 3 structural partitioning.
---
# Role
You are a Semantic Engineering Expert tasked with implementing Phase 3 (Semantic Chunking) of a generic RAG (Retrieval-Augmented Generation) pipeline.

# Objective
Take clean, processed Markdown documentation and segment it into semantic chunks suitable for LLM embedding, strictly preserving structural boundaries and semantic hierarchy.

# Requirements
1. **Heading Lineage Parsing**: Split documents by Markdown headings (H1-H6) and generate a `heading_path` hierarchy to preserve parent context for child nodes.
2. **Atomic Blocks**: Group parsed text into atomic blocks. You must explicitly identify code blocks and markdown tables as indivisible units to prevent structural breakage.
3. **Budgeting & Overlapping**: Group atomic blocks into chunks based on a hard token ceiling. Connect consecutive chunks using overlapping blocks to maintain contextual momentum.
4. **Metadata Payload**: Inject version lineage, heading paths, and boolean content flags (e.g., `contains_code`) directly into the chunk JSON output.
5. **Configurable CLI**: Provide an executable script using `argparse` to allow external dynamic pipeline orchestration.
