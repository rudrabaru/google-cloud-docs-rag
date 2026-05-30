# Phase 1: Raw Crawled Documents

This phase describes the ingestion and storage format of the raw documentation crawled from Google Cloud Platform (GCP) resources. The objective of this phase is to capture the source material faithfully before any transformative processing, cleaning, or structural manipulation occurs.

## Overview

The ingestion pipeline fetches documentation pages and stores them in a dual-file format for each document. This ensures that both the parsed markup and the structured metadata associated with the page are retained for downstream processing.

The raw documents are stored in the `raw_docs/` directory.

## File Formats

For every crawled page, two corresponding files are generated:

### 1. JSON Metadata Files (`.json`)
The JSON files store the structural and source information of the web page. 
- **URL**: The original source link of the crawled documentation.
- **Title**: The title of the page as extracted from the source.
- **Markdown Content**: The complete, unfiltered markdown representation of the page, including all navigation elements, footers, sidebars, and raw textual content.

### 2. Markdown Files (`.md`)
The markdown files contain the standalone, uncleaned text of the crawled page. This acts as the direct textual counterpart to the content stored within the JSON file and is used as the primary input for the cleaning and validation pipelines in subsequent phases.

## Purpose

By decoupling the raw ingestion (Phase 1) from the cleaning process (Phase 2), the system maintains an immutable record of the source data. This architecture allows the cleaning heuristics and validation logic to be iteratively improved and re-run on the original data without needing to re-execute the resource-intensive crawling process.
