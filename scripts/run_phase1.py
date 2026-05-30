#!/usr/bin/env python
"""
Phase 1: Document cleaning and preprocessing pipeline.

This script:
1. Loads raw documents from raw_docs/
2. Cleans documents (removes nav, footer, language selectors)
3. Validates document quality
4. Saves cleaned documents to processed_docs/
5. Generates processing reports

Run with: python document_processor.py
"""

import sys
import os
import json
import logging
from pathlib import Path

# Set root directory
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.processing.cleaner import ProcessingPipeline
from src.versioning import VersionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main document processing pipeline."""
    
    logger.info("=" * 80)
    logger.info("PHASE 1: Document Cleaning & Preprocessing")
    logger.info("=" * 80)
    
    # Directories
    raw_docs_dir = str(ROOT_DIR / "raw_docs")
    processed_docs_base = str(ROOT_DIR / "processed_docs")
    
    logger.info(f"\nInput directory: {raw_docs_dir}")
    logger.info(f"Base output directory: {processed_docs_base}")
    
    # Initialize version manager
    version_mgr = VersionManager(processed_docs_base)
    version_name = version_mgr.get_next_version()
    version_dir = version_mgr.create_version(
        phase="Phase 1: Cleaning & Preprocessing",
        enhancements=[
            "Footer removal (copyright, links, site policies)",
            "Language selector removal",
            "Navigation cleanup with pattern matching",
            "8-point comprehensive validation",
        ],
        metrics={
            "documents_targeted": 0,
            "documents_processed": 0,
            "documents_rejected": 0,
            "avg_words_per_doc": 0,
        }
    )
    
    logger.info(f"\nProcessing into version: {version_name}")
    logger.info(f"Version directory: {version_dir}")
    
    # Run pipeline
    pipeline = ProcessingPipeline(
        raw_dir=raw_docs_dir,
        processed_dir=str(version_dir),
        min_words=100,
        max_words=15000
    )
    
    logger.info("\n[PROCESSING] Starting document cleaning pipeline...")
    logger.info("-" * 80)
    
    try:
        processed_docs = pipeline.process()
    except Exception as e:
        logger.error(f"[FAIL] Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save cleaned documents and reports
    logger.info("\n[SAVING] Writing cleaned documents and reports...")
    logger.info("-" * 80)
    
    try:
        # Save individual cleaned documents
        docs_dir = version_dir / "documents"
        docs_dir.mkdir(exist_ok=True)
        
        doc_count = 0
        total_words = 0
        
        for doc in processed_docs:
            # Create markdown filename from URL, sanitized for Windows
            doc_name = doc.get('url', 'unknown').split('/')[-1]
            if not doc_name or doc_name == 'docs':
                doc_name = doc.get('title', 'untitled').replace(' ', '_').lower()
            
            # Sanitize: remove/replace invalid filename characters for Windows
            invalid_chars = r'<>:"/\|?*'
            for char in invalid_chars:
                doc_name = doc_name.replace(char, '_')
            
            # Remove non-breaking spaces and other special whitespace
            doc_name = doc_name.replace('\xa0', '_').replace('\u200b', '_')
            
            # Clean up multiple underscores
            while '__' in doc_name:
                doc_name = doc_name.replace('__', '_')
            
            doc_name = doc_name.strip('_')  # Remove leading/trailing underscores
            
            if not doc_name.endswith('.md'):
                doc_name += '.md'
            
            doc_path = docs_dir / doc_name
            
            # Write cleaned content
            content = doc.get('markdown_content') or doc.get('content', '')
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            doc_count += 1
            total_words += len(content.split())
            logger.debug(f"Saved: {doc_name}")
        
        logger.info(f"[OK] Saved {doc_count} cleaned documents to {docs_dir}")
        
        # Save reports
        reports_path = pipeline.save_reports(str(version_dir), filename="processing_report.json")
        logger.info(f"[OK] Reports saved: {reports_path}")
        
        # Update version manifest with final metrics
        avg_words = total_words // doc_count if doc_count > 0 else 0
        
        manifest_path = version_dir / "version_manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        manifest['metrics'].update({
            "documents_processed": doc_count,
            "documents_rejected": pipeline.processing_log['failed'],
            "avg_words_per_doc": avg_words,
        })
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"[OK] Updated version manifest: {manifest_path}")
        
    except Exception as e:
        logger.error(f"[FAIL] Failed to save documents/reports: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate version history
    logger.info("\n[VERSION HISTORY] Generating documentation...")
    logger.info("-" * 80)
    
    try:
        history_path = version_mgr.save_version_history()
        logger.info(f"[OK] Version history saved: {history_path}")
    except Exception as e:
        logger.warning(f"[WARN] Failed to save version history: {e}")
    
    # ========================================================================
    # COMPLETION
    # ========================================================================
    logger.info("\n" + "=" * 80)
    logger.info(f"PHASE 1 COMPLETE - Version {version_name}")
    logger.info("=" * 80)
    logger.info("\nPhase 1 Improvements Applied:")
    logger.info("  ✓ Footer removal: All footer sections stripped")
    logger.info("  ✓ Language selector removal: Language blocks removed")
    logger.info("  ✓ Navigation cleanup: Enhanced pattern matching")
    logger.info("  ✓ Comprehensive validation: Multi-check framework")
    logger.info(f"\nVersion Information:")
    logger.info(f"  Version: {version_name}")
    logger.info(f"  Location: {version_dir}")
    logger.info(f"  Documents: {version_dir / 'documents'}")
    logger.info(f"  Manifest: {version_dir / 'version_manifest.json'}")
    logger.info(f"  History: {Path(processed_docs_base) / 'VERSION_HISTORY.md'}")
    logger.info("\nNext Steps:")
    logger.info(f"  1. Review {version_dir / 'processing_report.json'} for quality metrics")
    logger.info(f"  2. Update scripts/run_chunking.py to reference {version_name}")
    logger.info(f"  3. Run: python scripts/run_chunking.py")
    logger.info(f"  4. Ready for Phase 2 iterations if needed")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
