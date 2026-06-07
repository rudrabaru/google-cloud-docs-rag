# AI Engineering Development Instructions

You are assisting in the development of a Retrieval-Augmented Generation (RAG) system for Google Cloud documentation.

The objective is to learn AI systems engineering deeply while building the system incrementally.

Core Development Philosophy:

* Prioritize understanding over abstraction.
* Prefer minimal working implementations first.
* Build incrementally and observably.
* Avoid unnecessary frameworks and premature optimization.
* Keep architectures transparent and inspectable.

Engineering Requirements:

* Always expose intermediate outputs for debugging.
* Print and inspect:

  * crawled markdown
  * cleaned text
  * chunk boundaries
  * retrieved chunks
  * similarity scores
  * generated prompts
  * LLM responses
* Explain WHY implementation decisions are made.
* Clearly separate:

  * crawling
  * processing
  * embeddings
  * retrieval
  * generation
  * evaluation

Coding Style:

* Prefer simple Python implementations.
* Keep modules small and understandable.
* Avoid excessive abstractions.
* Avoid unnecessary class hierarchies.
* Prefer readability over cleverness.
* Prefer explicit data flow.

Retrieval Engineering Priorities:

* Focus heavily on retrieval quality.
* Treat chunking quality as critical.
* Optimize for semantic coherence.
* Avoid noisy context construction.
* Encourage retrieval debugging before blaming the LLM.

Debugging Philosophy:
When failures occur, analyze:

* document quality
* chunking issues
* embedding quality
* retrieval relevance
* context contamination
* prompt construction
* token limitations

Avoid assuming the LLM is the primary issue.

Learning-Focused Behavior:

* Explain tradeoffs clearly.
* Highlight likely failure modes.
* Encourage manual inspection and experimentation.
* Prefer educational implementation over production complexity.

Avoid:

* premature enterprise architecture
* unnecessary orchestration frameworks
* complex agent systems
* hidden abstractions
* magic pipelines

The system should remain understandable end-to-end.

After each update requested by the user in the prompt, optimize the code for modularity, readability and maintainability, not just functionality. Refactor as needed to keep the codebase clean and understandable. Remove all unnecessary code and comments. Ensure that the code is well-organized and follows best practices for Python development.

Also update, the phase-wise documentation in the docs folder with clear explanations of the implementation, tradeoffs, and potential failure modes for each phase of the RAG pipeline. This documentation should be updated after each significant change to the codebase to ensure it remains accurate and helpful for future reference. Remember the docs folder should only contain documentation related to each phase of the RAG pipeline, not the code or bug fixes.

Maintain a consistent versioned folder structure across all processing stages.

Requirements:

* Never overwrite previous versions.
* Every version must preserve the same internal structure.
* Store both human-readable (`.md`) and machine-readable (`.json`) processed documents.
* Store chunk outputs separately from processed documents.
* Store all metrics, manifests, validation outputs, review sets, and quality reports in a dedicated `metrics/` subfolder.
* All reports and validation outputs should be versioned.

Example:

```text
raw_docs/
├── *.md
└── *.json

processed_docs/vN/
├── *.md
├── *.json
└── metrics/
    ├── quality_report.json
    ├── validation_report.json
    └── ...

chunks/vN/
├── *.json
└── metrics/
    ├── chunk_quality_report.json
    ├── chunks_manifest.json
    ├── chunks_by_document.json
    ├── chunks_by_category.json
    ├── review_set.json
    └── ...

reports/
├── processing_vN/
└── chunking_vN/
```

Each document and chunk must include version metadata (`document_version`, `chunk_version`) to ensure traceability across pipeline stages.

When introducing this structure, apply it consistently across all existing versions and future versions, including:

```text
processed_docs/v1 ... processed_docs/vN
chunks/v1 ... chunks/vN
```

No version should use a different layout, naming convention, or metrics organization.

If already one run is done on any phase, then use v+1 for the next run and mention v1 for the first one if not mentioned initially.

## Corpus-Agnostic Engineering

The system must remain corpus-agnostic.

Do not implement logic that depends on:

* specific websites
* specific documentation providers
* specific URLs
* specific products
* specific technologies
* specific heading names
* specific keywords
* specific document structures

Avoid hard-coded rules such as:

```python
if "Google Cloud" in title:
    ...

if heading == "What's next":
    ...

if "Related resources" in section:
    ...
```

Prefer:

* structural signals
* semantic signals
* metadata-driven decisions
* content classification
* measurable heuristics
* configurable thresholds

When implementing:

* cleaning
* processing
* chunking
* embeddings
* retrieval
* reranking
* evaluation

Always ask:

"Will this still work correctly for AWS docs, Azure docs, Kubernetes docs, PDFs, internal wikis, and unknown future corpora?"

If the answer is no, redesign the approach.

Corpus-specific assumptions should be treated as technical debt and explicitly justified.

Favor generalizable solutions over dataset-specific optimizations.

---

## Retrieval System Design

Optimize for retrieval quality rather than benchmark metrics.

Do not hard-code retrieval behavior based on:

* document names
* heading names
* URL patterns
* predefined categories
* known query patterns
* known document layouts

Retrieval decisions should be driven by:

* embeddings
* metadata
* ranking signals
* semantic similarity
* measurable evaluation results

If retrieval quality issues occur:

Do not introduce special-case handling first.

Instead:

1. Measure the failure.
2. Identify the root cause.
3. Evaluate document quality.
4. Evaluate chunk quality.
5. Evaluate embedding quality.
6. Evaluate retrieval configuration.
7. Introduce targeted improvements only when justified by evidence.

Avoid query-specific hacks and retrieval shortcuts.

---

## Evaluation-Driven Development

Every major retrieval improvement should be validated through evaluation.

Before introducing complexity:

* establish a baseline
* measure current performance
* define success criteria
* quantify improvement

Prefer:

Measure
→ Analyze
→ Improve
→ Re-measure

over:

Guess
→ Implement
→ Hope

When possible, maintain representative evaluation datasets and retrieval test cases.

---

## Anti-Hardcoding Rule

Before introducing any rule, heuristic, threshold, filter, ranking signal, or special case:

Explain:

1. Why it exists.
2. What problem it solves.
3. How it was validated.
4. What failure mode it prevents.
5. Whether it generalizes to unknown corpora.

If a rule only works because of characteristics of the current dataset:

* treat it as an experiment
* document it clearly
* avoid making it a permanent architectural dependency

Prefer solving classes of problems rather than individual cases.

---

## Future-Proofing Requirements

Design every component with future corpus expansion in mind.

Assume future ingestion sources may include:

* technical documentation
* PDFs
* research papers
* internal knowledge bases
* company wikis
* API documentation
* structured datasets
* semi-structured documents
* unstructured text

Implementation decisions should not require rewriting major pipeline stages when new document sources are introduced.

Favor extensible designs over source-specific solutions.

---

## Architecture Decision Making

Before introducing a new dependency, framework, abstraction, pipeline stage, retrieval strategy, or evaluation method:

Document:

* the problem being solved
* alternative approaches considered
* expected benefits
* tradeoffs
* maintenance cost

Prefer the simplest solution that satisfies current requirements.

Complexity must be justified by measurable improvements.

---

## RAG Engineering Mindset

Always think in terms of the full retrieval pipeline:

Document Quality
→ Chunk Quality
→ Embedding Quality
→ Retrieval Quality
→ Context Construction
→ Generation Quality
→ Evaluation

When failures occur:

Do not assume the LLM is the primary cause.

Investigate upstream components first.

Most retrieval failures originate from:

* poor documents
* poor chunking
* poor embeddings
* poor retrieval configuration
* poor context construction

Optimize the entire system rather than individual components in isolation.
