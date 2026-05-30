#!/usr/bin/env python
"""
Phase 1 Main Entry Point: Crawl and Build Raw Corpus

This script orchestrates the entire Phase 1 workflow:
1. Crawl Google Cloud Load Balancing documentation
2. Save raw documents with metadata
3. Clean and process documents
4. Validate document quality
5. Generate reports

Run with: python main.py
"""

import sys
import asyncio
import logging
from pathlib import Path

# Fix Windows encoding issues - use UTF-8 for console output
if sys.platform == 'win32':
    # Reconfigure stdout to use UTF-8 on Windows
    import io
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.crawler.crawl import crawl_gcp_load_balancing
from src.processing.cleaner import ProcessingPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main Phase 1 workflow."""
    
    logger.info("=" * 80)
    logger.info("PHASE 1: Crawl and Build Raw Corpus")
    logger.info("=" * 80)
    
    # Directories
    raw_docs_dir = "./raw_docs"
    processed_docs_dir = "./processed_docs"
    
    # ============================================================================
    # STAGE 1: CRAWL GOOGLE CLOUD LOAD BALANCING DOCS
    # ============================================================================
    logger.info("\n[STAGE 1] Starting web crawl...")
    logger.info("-" * 80)
    
    try:
        docs = await crawl_gcp_load_balancing(
            start_url="https://docs.cloud.google.com/load-balancing/docs/load-balancing-overview",
            max_depth=3,
            max_pages=100,
            output_dir=raw_docs_dir
        )
        logger.info(f"✓ Crawl completed: {len(docs)} documents")
    except Exception as e:
        logger.error(f"✗ Crawl failed: {e}")
        return
    
    # ============================================================================
    # STAGE 2: PROCESS (CLEAN, DEDUPLICATE, VALIDATE)
    # ============================================================================
    logger.info("\n[STAGE 2] Processing documents...")
    logger.info("-" * 80)
    
    try:
        pipeline = ProcessingPipeline(
            raw_dir=raw_docs_dir,
            processed_dir=processed_docs_dir,
            min_words=100,
            max_words=15000
        )
        processed_docs = pipeline.process()
        pipeline.save_reports(processed_docs_dir)
        
        logger.info(f"✓ Processing completed: {len(processed_docs)} documents")
    except Exception as e:
        logger.error(f"✗ Processing failed: {e}")
        return
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Raw documents: {raw_docs_dir}")
    logger.info(f"Processed documents: {processed_docs_dir}")
    logger.info(f"Total documents processed: {len(processed_docs)}")
    logger.info("\nNext steps:")
    logger.info("1. Inspect processed documents in processed_docs/")
    logger.info("2. Review processing_reports.json for details")
    logger.info("3. Run notebooks/phase1_inspection.ipynb for visualization")
    logger.info("4. Proceed to Phase 2: Chunking when ready")


if __name__ == "__main__":
    asyncio.run(main())
