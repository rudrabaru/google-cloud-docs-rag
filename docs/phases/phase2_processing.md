# Phase 2: Heuristic Cleaning & Processing

## Overview
The processing phase refines raw semantic Markdown extracted during Phase 1 by applying a series of generalized content heuristics. It mathematically strips out navigation noise, boilerplate text, and headers/footers without relying on domain-specific hardcoded keywords.

## Implementation Details

### 1. Link Density Analysis
Instead of hardcoding class names or IDs (like `#sidebar`), the processor calculates the ratio of hyperlinked text to plain text within text blocks. Sections with extraordinarily high link density (typical of navigation menus, TOCs, and footers) are identified mathematically and excised.

### 2. Structural Component Preservation
The processor uses Markdown ast-parsing to guarantee that semantic blocks like Code (` ``` `), Tables, and explicit lists are never accidentally purged, regardless of their text-to-link density or length. 

### 3. Whitespace and Artifact Normalization
Cleans excessive empty lines, fragmented list artifacts, and dangling anchors resulting from the raw DOM-to-Markdown conversion.

## Tradeoffs
- **False Positives in Density Rules**: Aggressive link-density stripping might occasionally prune highly interconnected "Further Reading" reference lists at the end of valid documents. We prefer false positives (leaving slight noise) over false negatives (deleting vital context) as dictated by AGENTS.md.
- **Computational Overhead**: Line-by-line heuristic parsing across large documents introduces processing latency compared to simple regex matching.

## Potential Failure Modes
- Over-pruning of valid content if link-density thresholds are tuned too aggressively for the target corpus.
- Preservation of repetitive boilerplate if the structural signature does not trigger standard heuristics (e.g., repeating inline text links).
