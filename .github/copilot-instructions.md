# AI Engineering Development Instructions

You are assisting in the development of a Retrieval-Augmented Generation (RAG) system designed to support technical documentation and future heterogeneous knowledge sources.

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

## Corpus Independence Requirements

The system must not rely on corpus-specific assumptions.

Avoid implementations that depend on:

- specific websites
- specific documentation providers
- specific products
- predefined section names
- predefined navigation labels
- hardcoded keywords
- manually curated removal lists

Examples of forbidden patterns:

if "What's next" in text:
if "Related resources" in text:
if "Google Cloud Documentation" in text:
if "Stay organized with collections" in text:

unless supported by generic structural evidence.

Prefer structural, statistical, metadata-based, or content-density-based approaches over keyword matching.

# Generalization Test

Before finalizing any implementation, perform the following thought experiment:

Assume the current corpus is replaced tomorrow by:

- AWS documentation
- Azure documentation
- Kubernetes documentation
- Confluence pages
- research papers
- PDFs
- internal company documentation

Would the implementation still function correctly without code changes?

If not:

- redesign the implementation
- isolate corpus-specific behavior
- document the limitation explicitly

Generalization is the default expectation.

# Source Independence Requirements

Do not introduce source-specific processing logic into core pipeline stages.

Forbidden patterns include:

- source-specific cleaners
- source-specific chunkers
- source-specific retrievers
- source-specific embedding pipelines
- source-specific reranking logic

Examples:

if source == "google_cloud":
if source == "aws":
if "docs.cloud.google.com" in url:
GoogleCloudProcessor()
AWSChunker()

Core pipeline behavior must be determined by:

- structure
- metadata
- measurable signals
- content characteristics

not source identity.

Source-specific adapters may exist only as optional plugins and must never become mandatory dependencies of the core pipeline.

# Content Preservation Requirements

Content should never be removed solely because it appears unimportant.

Removal must be supported by measurable evidence.

Examples of acceptable evidence:

- extremely high duplication
- navigation-only structures
- repeated boilerplate detected structurally
- retrieval contamination confirmed through evaluation

Examples of unacceptable evidence:

- section title contains a specific keyword
- content "looks unimportant"
- content is short
- content is uncommon

When uncertain:

PRESERVE THE CONTENT.

Prefer false positives over false negatives.

Removing useful information is more costly than retaining small amounts of noise.

# Structural Preservation Requirements

Preserve:

- heading hierarchy
- section boundaries
- parent-child relationships
- code blocks
- tables
- lists
- procedural steps
- semantic grouping

Do not merge content across unrelated heading paths unless there is strong evidence that the content forms a single semantic unit.

Heading hierarchy should be treated as a first-class retrieval signal.

# Chunking Constraints

Chunking decisions must not be driven solely by token counts.

Token counts are guidance, not rules.

Always prioritize:

1. Semantic completeness
2. Retrieval usefulness
3. Heading hierarchy preservation
4. Content integrity

before optimizing for chunk size targets.

A small chunk can be valid.
A large chunk can be valid.

The objective is retrieval quality, not token-count uniformity.

# Corpus-Tuned Threshold Rule

Do not introduce thresholds, limits, chunk sizes, overlaps, retrieval parameters, or scoring rules solely because they perform well on the current corpus.

Every threshold must include:

- rationale
- validation evidence
- expected tradeoffs

Thresholds should generalize across future corpora whenever possible.

Corpus-specific tuning should be treated as an experiment and documented explicitly.

# Retrieval Engineering Principles

Retrieval quality is the foundation of the RAG system.

Prioritize retrieval relevance, explainability, observability, and evaluation over retrieval speed or implementation convenience.

The objective of retrieval is to consistently return the most relevant information required to answer a query.

When retrieval failures occur:

Do not immediately modify prompts, rerankers, or LLM behavior.

First investigate:

* document quality
* chunk quality
* embedding quality
* retrieval configuration
* metadata quality

Treat retrieval as an independent subsystem.

Prefer:

Query
→ Retrieval
→ Evaluation
→ Optimization

over:

Query
→ Retrieval
→ Generation
→ Guessing

Retrieval quality should be measurable independently from generation quality.

Do not hard-code retrieval behavior based on:

* document names
* heading names
* URL patterns
* predefined categories
* known query patterns
* corpus-specific assumptions

Retrieval decisions should be driven by:

* embeddings
* metadata
* ranking signals
* semantic similarity
* measurable evaluation results

Avoid query-specific hacks and retrieval shortcuts.

If retrieval quality issues occur:

1. Measure the failure.
2. Identify the root cause.
3. Validate the failure through representative examples.
4. Quantify impact.
5. Introduce targeted improvements only when justified by evidence.

Prefer solving classes of retrieval problems rather than individual retrieval examples.

Retrieval improvements should be guided by:

* Recall@K
* MRR
* retrieval relevance
* retrieval consistency
* manual retrieval inspection
* failure analysis

Do not optimize retrieval solely for benchmark metrics.

Improvements should also preserve:

* explainability
* maintainability
* corpus independence
* retrieval usefulness

Before introducing advanced retrieval techniques such as:

* hybrid search
* reranking
* query expansion
* multi-query retrieval
* agentic retrieval

establish a baseline and demonstrate that the simpler approach is insufficient.

Favor evidence-driven improvements over complexity-driven improvements.

# Corpus Audit Rule

Before rebuilding any upstream pipeline stage:

* perform an audit
* quantify quality issues
* identify root causes
* inspect representative samples
* measure impact

Do not rebuild stages solely because downstream metrics are imperfect.

Use evidence to determine whether failures originate from:

* documents
* processing
* chunking
* metadata
* embeddings
* retrieval
* generation

Prefer targeted improvements over full pipeline rewrites.

Rebuilding a stage should be the result of measurable evidence, not uncertainty.

# Evaluation-Driven Development

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

# Metrics Are Signals, Not Objectives

Metrics guide engineering decisions.

Do not optimize solely for metric improvement.

Improvements should also preserve:

* explainability
* maintainability
* retrieval usefulness
* semantic integrity
* corpus independence

Higher metrics do not automatically indicate a better system.

When metrics improve, verify that:

* retrieval quality actually improved
* content preservation remains intact
* chunk quality remains acceptable
* behavior generalizes beyond evaluation examples

Optimize for robust system quality rather than benchmark scores alone.

# Retrieval Observability

For every evaluation query:

- Save query text
- Save expected document
- Save retrieved chunks
- Save similarity scores
- Save hit@1, hit@3, hit@5

Generate:

Persist evaluation artifacts,
metrics,
failure reports,
and debugging outputs.

All evaluation outputs must be reproducible and auditable.

Store all outputs under:
retrieval/vN

where 'N' = 1,2,3,...

Do not only print metrics to console.
All retrieval evaluations must be reproducible and auditable.

# Anti-Hardcoding Rule

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

# Future-Proofing Requirements

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

# Architecture Decision Making

Before introducing a new dependency, framework, abstraction, pipeline stage, retrieval strategy, or evaluation method:

Document:

* the problem being solved
* alternative approaches considered
* expected benefits
* tradeoffs
* maintenance cost

Prefer the simplest solution that satisfies current requirements.

Complexity must be justified by measurable improvements.

# Metadata Independence Rule

Metadata may guide pipeline decisions only when the metadata itself was derived through generic methods.

Avoid metadata generated from:

- URL naming conventions
- provider-specific paths
- product-specific assumptions
- manually curated labels

Prefer metadata derived from:

- document structure
- content analysis
- statistical evidence
- classification models

Pipeline behavior should not depend on metadata that exists only because of characteristics of the current corpus.

# Evidence Before Modification

Before modifying any pipeline stage:

1. Measure the current behavior.
2. Quantify the problem.
3. Identify root cause.
4. Estimate expected impact.
5. Validate improvement after implementation.

Avoid speculative fixes.

Prefer evidence-driven changes over intuition-driven changes.

Do not introduce complexity solely because a problem might exist.

Changes should be justified by measurable observations, representative examples, or evaluation results.

# RAG Engineering Mindset

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

# Embedding Engineering

Treat embeddings as a measurable system component rather than a black box.

Before introducing vector databases or retrieval optimizations:

* validate embedding generation
* validate metadata preservation
* validate embedding consistency
* validate semantic similarity behavior

Always inspect:

* embedding dimensions
* embedding generation failures
* representative similarity results
* nearest-neighbor quality

Embedding quality should be evaluated before retrieval quality.

Do not assume poor retrieval is caused by retrieval logic until embedding quality has been validated.

# Baseline-First Development

Always build and validate the simplest working version first.

For every major phase:

1. Implement the simplest useful solution.
2. Establish a baseline.
3. Measure behavior.
4. Identify bottlenecks.
5. Introduce complexity only when justified.

Examples:

* basic embeddings before advanced embeddings
* similarity search before hybrid search
* vector retrieval before rerankers
* single-query retrieval before multi-query retrieval
* standard RAG before agentic RAG

Do not introduce advanced techniques unless there is evidence that the baseline is insufficient.

Favor understanding and observability over sophistication.

# Pipeline Versioning

Every pipeline stage must follow the same versioning model.

Examples:

* raw documents (raw_docs/vN)
* processed documents (processed_docs/vN)
* chunks (chunks/vN)
* embeddings (embeddings/vN)
* retrieval results (retrieval_results/vN)
* evaluation datasets (evaluation_datasets/vN)
* evaluation reports (evaluation_reports/vN)
* reranking outputs (reranking_outputs/vN)

Use:

phase_name/vN/

instead of:

phase_name_vN/

or other naming conventions.

Each version must:

* preserve previous versions
* remain reproducible
* contain its own metrics
* contain its own manifests
* contain its own validation outputs

Versioning rules apply to all existing and future pipeline stages.

Do not introduce alternative versioning schemes.

If already one run is done on any phase, then use v+1 for the next run and mention v1 for the first one if not mentioned initially.

# Artifact Consistency

Every artifact-producing phase should maintain a predictable structure.

Each phase should contain:

* primary outputs
* metrics
* manifests
* validation results

Example:

phase_name/
└── vN/
    ├── outputs
    └── metrics/

Future phases should follow the same organizational principles rather than inventing new layouts.

# Special Notes

After each update requested by the user in the prompt, optimize the code for modularity, readability and maintainability, not just functionality. Refactor as needed to keep the codebase clean and understandable. Remove all unnecessary code and comments. Ensure that the code is well-organized and follows best practices for Python development.

Also update, the phase-wise documentation in the docs folder with clear explanations of the implementation, tradeoffs, and potential failure modes for each phase of the RAG pipeline. This documentation should be updated after each significant change to the codebase to ensure it remains accurate and helpful for future reference. Remember the docs folder should only contain documentation related to each phase of the RAG pipeline, not the code or bug fixes.

Never remove content because of specific words. Remove content only because of measurable structural evidence.