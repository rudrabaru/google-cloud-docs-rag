Act as a Senior RAG Data Processing Engineer.

Implement a generic boilerplate detection and removal system for the Document Processing stage.

The objective is to identify and remove website chrome, navigation artifacts, and other non-content elements while preserving all meaningful information required for retrieval.

The system must remain perfectly corpus-agnostic and reusable across future documentation sources without code changes.

---

## Core Principles

Content preservation is the highest priority.

If uncertainty exists between removing and preserving content:

PRESERVE THE CONTENT.

Do NOT hardcode:

* source-specific phrases (e.g. "skip to main content")
* page titles
* URLs
* product names
* section names
* navigation labels
* domain-specific keywords

Use structural, statistical, and semantic signals instead.

---

## Boilerplate Detection Strategy

Analyze content at the block level.

A block may be:

* heading
* paragraph
* list
* table
* code block
* callout
* note
* warning

For each block compute a boilerplate score using multiple independent signals.

---

### Signal 1: Document Frequency

Measure how frequently a block (or mathematically normalized block) appears across the corpus.

Generate:

* document frequency
* corpus occurrence percentage

Interpretation:

* > 5% → candidate boilerplate
* > 20% → strong candidate
* > 50% → high-confidence candidate

Frequency alone must never trigger deletion.

---

### Signal 2: Position

Evaluate where the block appears:

* near beginning of document
* near end of document
* middle of document

Navigation and footer elements often cluster near document boundaries.

Position alone must never trigger deletion.

---

### Signal 3: Link Density

Measure:

* number of links
* ratio of link tokens to text tokens

Blocks containing mostly links are stronger boilerplate candidates.

---

### Signal 4: Information Density

Reward blocks containing:

* explanations
* concepts
* procedures
* examples
* technical descriptions
* architecture discussions

Penalize blocks containing:

* mostly links
* short navigation labels
* repetitive directory structures

---

### Signal 5: Structural Context

Consider neighboring blocks.

Examples:

* large clusters of short link-heavy blocks
* repeated navigation structures
* repeated footer structures

Treat surrounding context as evidence.

---

### Signal 6: Content Diversity

Evaluate:

* unique word ratio
* semantic richness
* technical vocabulary density

Navigation blocks generally have low diversity.

Technical content generally has higher diversity.

---

## Preservation Rules

Always strongly favor preserving:

* headings
* heading hierarchy
* technical explanations
* procedures
* numbered steps
* examples
* notes
* warnings
* best practices
* limitations
* architecture descriptions
* code blocks
* configuration snippets
* API examples
* tables
* schemas

These elements may contribute to retrieval quality and should never be removed based solely on frequency or position.

---

## Confidence Tiers & Removal Rules

Remove a block only when strict confidence tiers are met. Do not remove based on a single generic score.

Example tiers:
* **Tier 1 (Obvious Chrome)**: Extremely high document frequency combined with very low word count.
* **Tier 2 (Multi-Signal Match)**: Elevated boilerplate score combined with independent triggers from at least two distinct signals (e.g., edge-of-document AND low diversity).
* **Tier 3 (Link Walls)**: Highly repetitive blocks consisting almost entirely of links.

Require multiple independent signals before removal. Avoid single-rule decisions.

---

## Explainability

Every removed block must include a reason.

Generate comprehensive reports (e.g., removed blocks, triggered signals).

For each removal log:

* content preview
* document frequency
* position
* link density
* boilerplate score
* removal reason
* which independent signals were triggered

All removals must be transparent and auditable.

---

## Validation

Generate:

* boilerplate detection reports
* removed blocks reports
* review sets

Measure:

* content retention percentage
* heading retention
* code retention
* table retention
* boilerplate reduction

---

## Review Set

Generate representative examples showing:

1. Original block
2. Boilerplate score
3. Removal decision
4. Justification (signals triggered)

Include:

* removed blocks
* preserved blocks
* borderline cases (blocks that scored high but narrowly survived)

The goal is to verify that meaningful content is not being removed and to continually tune the heuristic confidence tiers.

---

## Success Criteria

The resulting system should:

* remove navigation artifacts
* remove footer artifacts
* remove repeated website chrome
* preserve technical content
* preserve document structure
* preserve code blocks
* preserve tables
* preserve examples
* remain completely source-agnostic
* remain explainable and auditable

Optimize for content preservation and retrieval quality over aggressive cleaning.
