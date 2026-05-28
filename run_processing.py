#!/usr/bin/env python
"""
Standalone script to run Phase 1 processing pipeline on crawled documents.
Use this to process documents after crawling.
"""

import sys
import logging
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.processing.pipeline import ProcessingPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run processing pipeline on crawled documents."""
    
    logger.info("=" * 80)
    logger.info("PHASE 1: Processing Raw Corpus")
    logger.info("=" * 80)
    
    raw_docs_dir = "./raw_docs"
    processed_docs_dir = "./processed_docs"
    
    logger.info("\n[PROCESSING] Starting document processing...")
    logger.info("-" * 80)
    
    try:
        # Run processing pipeline
        pipeline = ProcessingPipeline(
            raw_dir=raw_docs_dir,
            processed_dir=processed_docs_dir,
        )
        
        processed_docs = pipeline.process()
        
        logger.info(f"\n[SUCCESS] Processing complete!")
        logger.info(f"  - Documents processed: {len(processed_docs)}")
        
        # Save reports
        pipeline.save_reports()
        logger.info("  - Reports saved")
        
    except Exception as e:
        logger.error(f"[ERROR] Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 COMPLETE")
    logger.info("=" * 80)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
