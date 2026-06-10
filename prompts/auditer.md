Act as a Senior RAG Corpus Quality Auditor.

Your task is to perform a comprehensive audit of the latest processed document corpus.

The objective is to verify that the document processing stage successfully removed boilerplate while preserving meaningful technical content across a generalized, source-agnostic dataset.

Do NOT modify any documents.

Do NOT perform additional cleaning.

Only audit and report findings.

---

## Inputs

Analyze:

* raw document corpus
* processed document corpus

Compare them directly.

---

## Audit Objectives

Determine whether the processing pipeline:

1. Removed boilerplate successfully.
2. Preserved technical content.
3. Preserved document structure.
4. Preserved code blocks.
5. Preserved tables.
6. Preserved procedures and examples.
7. Preserved metadata quality.
8. Avoided over-cleaning.

---

## Boilerplate Removal Audit

Measure:

### Navigation Removal

Examples include:

* navigation menus
* language selectors
* breadcrumbs
* page-level table of contents
* product directories
* footer navigation
* feedback widgets

Report:

* occurrences before processing
* occurrences after processing
* reduction percentage

---

## Content Preservation Audit

Measure retention of:

* headings
* paragraphs
* procedures
* examples
* notes
* warnings
* references
* technical explanations

Generate:

* content retention percentage
* word retention percentage
* character retention percentage

Flag:

* suspiciously aggressive reductions
* suspiciously low retention

---

## Heading Structure Audit

Compare before vs after:

* H1 count
* H2 count
* H3 count
* H4 count

Report:

* heading preservation rate
* missing heading analysis

---

## Code Preservation Audit

Measure:

* code blocks before
* code blocks after

Report:

* preservation percentage
* removed code blocks
* modified code blocks

Flag any losses.

---

## Table Preservation Audit

Measure:

* tables before
* tables after

Report:

* preservation percentage
* removed tables
* modified tables

Flag any losses.

---

## Metadata Audit

Verify presence and quality of:

* source URL
* title
* page type
* timestamps
* processing metadata

Report:

* missing fields
* inconsistent fields
* enrichment quality

---

## Over-Cleaning Detection

Identify documents where:

* unusually high content removal occurred
* sections disappeared
* structure degraded

Provide examples.

---

## Manual Review Set

Generate a representative review set containing a variety of document types (e.g. guides, tutorials, reference pages, API documentation).

For each sample provide:

1. Raw version
2. Processed version
3. Removed content
4. Removal justification (e.g. triggered signals, confidence tiers)

The purpose is human verification.

---

## Final Verdict

Provide:

* Boilerplate Removal Score (0-10)
* Content Preservation Score (0-10)
* Structure Preservation Score (0-10)
* Metadata Quality Score (0-10)
* Overall Processing Quality Score (0-10)

Conclude whether the processed corpus is ready for chunking or requires another processing iteration.

Do not make assumptions.

Base conclusions entirely on measurable evidence from the corpus.
