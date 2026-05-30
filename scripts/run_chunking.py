#!/usr/bin/env python
"""
Phase 2 Orchestration: Document Chunking Pipeline

This script:
1. Loads processed documents from processed_docs/
2. Chunks them using semantic boundaries and token budgeting
3. Saves chunks to chunks/ directory
4. Generates quality reports and statistics
5. Creates inspection data for manual review

Run with: python chunk_processor.py
"""

import sys
import os
import json
import logging
import time
from pathlib import Path
from typing import List

# Set root directory
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.chunking import (
    DocumentChunker,
    ChunkingConfig,
    ChunkingInspector,
    ChunkMetadata
)
from src.versioning import VersionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_processed_documents(processed_base_dir: str = "./processed_docs", version: str = None) -> tuple:
    """
    Load all processed documents from the versioned processed_docs directory.
    
    Args:
        processed_base_dir: Base path to processed_docs directory
        version: Specific version to load (e.g., 'v1'). If None, loads latest.
    
    Returns:
        Tuple of (documents list, version used, version dir)
    """
    version_mgr = VersionManager(processed_base_dir)
    
    if version is None:
        version = version_mgr.get_latest_version()
        if version is None:
            raise ValueError("No processed document versions found. Run document_processor.py first.")
    
    logger.info(f"Loading documents from version: {version}")
    
    docs_dir = version_mgr.get_documents_dir(version)
    
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documents directory not found: {docs_dir}")
    
    documents = []
    markdown_files = sorted(docs_dir.glob("*.md"))
    
    logger.info(f"Found {len(markdown_files)} markdown files in {docs_dir}")
    
    for md_file in markdown_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from filename (convert slug back to title case)
            title = md_file.stem.replace('_', ' ').title()
            
            # Create document dict with markdown_content key (expected by chunker)
            doc = {
                'url': f"processed://{version}/{md_file.name}",
                'title': title,
                'markdown_content': content,  # Use markdown_content key for chunker compatibility
                'word_count': len(content.split()),
                'source_file': md_file.name,
            }
            
            documents.append(doc)
            
        except Exception as e:
            logger.error(f"Error loading {md_file.name}: {e}")
            continue
    
    logger.info(f"Successfully loaded {len(documents)} documents from {version}")
    
    version_dir = version_mgr.get_version_path(version)
    return documents, version, version_dir


def save_chunks(
    chunks: List[ChunkMetadata],
    chunks_dir: str,
    save_individual: bool = False
) -> None:
    """
    Save chunks to disk.
    
    Args:
        chunks: List of chunks to save
        chunks_dir: Output directory
        save_individual: Whether to save individual chunk JSON files
    """
    chunks_path = Path(chunks_dir)
    chunks_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving {len(chunks)} chunks to {chunks_dir}")
    
    # Save manifest (all chunks metadata)
    manifest = [c.dict() for c in chunks]
    manifest_file = chunks_path / "chunks_manifest.json"
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, default=str)
    
    logger.info(f"[OK] Saved manifest: {manifest_file}")
    
    # Group chunks by source document
    chunks_by_doc = {}
    for chunk in chunks:
        doc = chunk.source_document
        if doc not in chunks_by_doc:
            chunks_by_doc[doc] = []
        chunks_by_doc[doc].append(chunk.dict())
    
    grouped_file = chunks_path / "chunks_by_document.json"
    with open(grouped_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_by_doc, f, indent=2, default=str)
    
    logger.info(f"[OK] Saved grouped chunks: {grouped_file}")
    
    # Optionally save individual chunk files
    if save_individual:
        individual_dir = chunks_path / "individual_chunks"
        individual_dir.mkdir(exist_ok=True)
        
        for chunk in chunks:
            chunk_file = individual_dir / f"{chunk.chunk_id}.json"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk.dict(), f, indent=2, default=str)
        
        logger.info(f"[OK] Saved {len(chunks)} individual chunk files")


def main():
    """Main Phase 2 orchestration."""
    
    logger.info("=" * 80)
    logger.info("PHASE 2: Document Chunking System")
    logger.info("=" * 80)
    
    # Directories
    processed_docs_base = str(ROOT_DIR / "processed_docs")
    chunks_dir = str(ROOT_DIR / "chunks")
    
    # Configuration
    config = ChunkingConfig(
        chunk_size=700,
        overlap=125,
        preserve_markdown=True,
        min_chunk_tokens=50,
        max_chunk_tokens=1500
    )
    
    logger.info(f"\nConfiguration:")
    logger.info(f"  - Chunk Size: {config.chunk_size} tokens")
    logger.info(f"  - Overlap: {config.overlap} tokens")
    logger.info(f"  - Min Tokens: {config.min_chunk_tokens}")
    logger.info(f"  - Max Tokens: {config.max_chunk_tokens}")
    
    # ========================================================================
    # STAGE 1: LOAD PROCESSED DOCUMENTS
    # ========================================================================
    logger.info("\n[STAGE 1] Loading processed documents...")
    logger.info("-" * 80)
    
    try:
        documents, version, version_dir = load_processed_documents(processed_docs_base)
        logger.info(f"[OK] Loaded {len(documents)} documents from {version}")
        logger.info(f"[OK] Source: {version_dir / 'documents'}")
    except Exception as e:
        logger.error(f"[FAIL] Failed to load documents: {e}")
        return False
    
    if not documents:
        logger.error("[FAIL] No documents loaded")
        return False
    
    # ========================================================================
    # STAGE 2: CHUNK DOCUMENTS
    # ========================================================================
    logger.info("\n[STAGE 2] Chunking documents...")
    logger.info("-" * 80)
    
    start_time = time.time()
    
    try:
        chunker = DocumentChunker(config=config)
        chunks = chunker.chunk_batch(documents)
        elapsed = time.time() - start_time
        
        logger.info(f"[OK] Created {len(chunks)} chunks in {elapsed:.2f}s")
    except Exception as e:
        logger.error(f"[FAIL] Chunking failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    if not chunks:
        logger.error("[FAIL] No chunks created")
        return False
    
    # ========================================================================
    # STAGE 3: SAVE CHUNKS
    # ========================================================================
    logger.info("\n[STAGE 3] Saving chunks...")
    logger.info("-" * 80)
    
    try:
        save_chunks(chunks, chunks_dir, save_individual=False)
        logger.info("[OK] Chunks saved successfully")
    except Exception as e:
        logger.error(f"[FAIL] Failed to save chunks: {e}")
        return False
    
    # ========================================================================
    # STAGE 4: ANALYZE & REPORT
    # ========================================================================
    logger.info("\n[STAGE 4] Analyzing chunk quality...")
    logger.info("-" * 80)
    
    try:
        inspector = ChunkingInspector()
        report_json = inspector.generate_json_report(chunks, elapsed)
        
        # Save JSON report
        report_file = Path(chunks_dir) / "chunking_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_json, f, indent=2, default=str)
        
        logger.info(f"[OK] Saved JSON report: {report_file}")
        
        # Print summary
        summary = report_json['summary']
        tokens = report_json['tokens']
        
        logger.info(f"\n[SUMMARY]")
        logger.info(f"  Documents: {summary['total_documents']}")
        logger.info(f"  Chunks: {summary['total_chunks']}")
        logger.info(f"  Total Tokens: {tokens['total']:,}")
        logger.info(f"  Avg Tokens/Chunk: {tokens['avg_per_chunk']}")
        logger.info(f"  Token Range: {tokens['min']}-{tokens['max']}")
        logger.info(f"  In Target Range (500-800): {tokens['in_target_range_500_800']}")
        
        # Print token distribution
        dist = tokens['distribution']['buckets']
        logger.info(f"\n[TOKEN DISTRIBUTION]")
        logger.info(f"  <300: {dist['under_300']}")
        logger.info(f"  300-500: {dist['300_500']}")
        logger.info(f"  500-800: {dist['500_800']} (target)")
        logger.info(f"  800-1000: {dist['800_1000']}")
        logger.info(f"  >1000: {dist['over_1000']}")
        
        # Print edge cases
        edge = report_json['quality']['edge_cases']
        logger.info(f"\n[EDGE CASES]")
        logger.info(f"  Tiny (<50): {len(edge.get('tiny_chunks', []))}")
        logger.info(f"  Huge (>1000): {len(edge.get('huge_chunks', []))}")
        logger.info(f"  Orphaned: {len(edge.get('orphaned_chunks', []))}")
        
        # Print code detection statistics
        code_chunks = sum(1 for c in chunks if c.contains_code)
        logger.info(f"\n[CODE DETECTION]")
        logger.info(f"  Chunks with code: {code_chunks}/{len(chunks)}")
        
        # Print cleaning improvements
        logger.info(f"\n[PHASE 1 IMPROVEMENTS - ENABLED]")
        logger.info(f"  ✓ Footer removal: Active")
        logger.info(f"  ✓ Language selector removal: Active")
        logger.info(f"  ✓ Code block detection: {code_chunks} chunks tagged")
        logger.info(f"  ✓ Comprehensive validation: Applied during preprocessing")
        
    except Exception as e:
        logger.error(f"[FAIL] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========================================================================
    # COMPLETION
    # ========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 COMPLETE")
    logger.info("=" * 80)
    logger.info("\nNext Steps:")
    logger.info("  1. Review chunks_manifest.json for all chunk metadata")
    logger.info("  2. Run phase2_chunking_inspection.ipynb for detailed analysis")
    logger.info("  3. Verify semantic coherence by reading sample chunks")
    logger.info("  4. Ready for Phase 3: Embeddings & Vector Search")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
