# Phase 6: Systematic Evaluation

## Overview
Phase 6 is the benchmarking suite for the retrieval pipeline. It evaluates the `DenseRetriever` against a version-controlled dataset of natural language queries, producing reproducible metrics that drive evidence-based improvement decisions.

## Implementation Details

### 1. Evaluation Dataset Format
Each query in the JSON dataset contains:
- `query`: Natural language question
- `expected_topic`: Human-readable topic label for failure analysis grouping
- `acceptable_documents`: List of acceptable source URL substrings (any match counts as a hit)
- `acceptable_headings`: Optional list of acceptable section headings (if provided, both document AND heading must match for an Exact Match)
- `difficulty`: `easy`, `medium`, or `hard` — used for per-group metric breakdown
- `category`: Topical category — used for per-group metric breakdown

### 2. Match Classification
The evaluator uses token-aware normalized sublist matching instead of exact string comparison. This prevents false negatives from URL formatting differences.

| Match Type | Condition |
|-----------|-----------|
| Exact Match | Correct document AND correct heading (if heading constraints given) |
| Partial Match | Correct document only |
| No Match | Neither document nor heading matched |

Metrics (Recall@K, MRR) are computed on the **first hit rank**, where a Partial Match and Exact Match both count as a hit. Exact Match rate is tracked separately.

### 3. Metrics Produced
- **Recall@1, Recall@3, Recall@5**: Fraction of queries where the correct document appeared in top 1/3/5 results
- **MRR (Mean Reciprocal Rank)**: Average of 1/rank across all queries; captures ranking quality
- **Metrics by Difficulty**: Recall@K and MRR broken down by `easy`, `medium`, `hard`
- **Metrics by Category**: Same breakdown by topical category

### 4. Versioning
Evaluation runs are nested under the retrieval implementation version:
```
retrieval/v1/evaluations/v1/   ← first evaluation run against retrieval v1
retrieval/v1/evaluations/v2/   ← re-run after dataset changes
```
A new retrieval version is created only when the retrieval *implementation* changes. A new evaluation version is created when the dataset or evaluation logic changes.

### 5. Outputs per Evaluation Run
All outputs live in `retrieval/vN/evaluations/vN/`:
- `evaluation_metrics.json` — overall and group metrics
- `evaluation_summary.md` — human-readable summary
- `evaluation_evidence_report.json` — per-query match classification reasoning
- `retrieval_review_validation.json` — sampled successes, partials, and failures for manual inspection
- `benchmark_integrity_report.json` — dataset validation (duplicates, missing fields)
- `benchmark_reliability_report.json` — evaluation quality self-assessment

## Tradeoffs
- **Multi-document acceptable sets**: Queries accept multiple valid source documents, reflecting that real retrieval may correctly satisfy a query from a different-but-equivalent document. This prevents false failures.
- **Partial vs Exact Match gap**: A large gap between Partial and Exact Match rates indicates the retriever finds the right page but wrong section. This points to chunking or heading-path quality issues.
- **Small dataset risk**: With fewer than 50 queries, Recall@K values can swing 5–10 percentage points from a single query change. The dataset was expanded to 52 queries (as of v2) for statistical reliability.

## Potential Failure Modes
- **Flawed evaluation dataset**: Expected documents may not exist in the index if the crawler didn't reach those pages. Always validate that acceptable_documents actually appear in the ChromaDB collection before trusting low recall numbers.
- **Metric saturation**: If Recall@5 approaches 1.0, the dataset is too easy. Add harder queries requiring multi-hop reasoning or rare sections.
