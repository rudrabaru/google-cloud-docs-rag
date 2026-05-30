#!/usr/bin/env python
"""
Phase 2: Advanced document cleaning and preprocessing pipeline.

This script:
1. Loads v1 processed documents 
2. Applies AdvancedCleaner for sophisticated navigation/boilerplate removal
3. Validates document quality
4. Saves v2 cleaned documents to processed_docs/v2/
5. Generates Phase 2 processing reports with metrics

Run with: python document_processor_phase2.py
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

from src.processing.cleaner import ProcessingPipeline, AdvancedCleaner
from src.versioning import VersionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main Phase 2 document processing pipeline."""
    
    logger.info("=" * 80)
    logger.info("PHASE 2: Advanced Content Cleaning (Navigation & Boilerplate Removal)")
    logger.info("=" * 80)
    
    # Directories
    processed_docs_base = str(ROOT_DIR / "processed_docs")
    
    logger.info(f"\nBase directory: {processed_docs_base}")
    
    # Initialize version manager
    version_mgr = VersionManager(processed_docs_base)
    
    # Get latest version (should be v1)
    latest_version = version_mgr.get_latest_version()
    if not latest_version:
        logger.error("No previous version found. Run document_processor.py first.")
        sys.exit(1)
    
    logger.info(f"Loading from version: {latest_version}")
    v1_dir = version_mgr.get_documents_dir(latest_version)
    
    # Create v2 version
    version_name = version_mgr.get_next_version()
    version_dir = version_mgr.create_version(
        phase="Phase 2: Advanced Cleaning (Navigation & Boilerplate Removal)",
        enhancements=[
            "Advanced main content detection (heading hierarchy analysis)",
            "Sophisticated sidebar navigation removal (link-only lists)",
            "Repeated boilerplate block removal (>80% doc frequency)",
            "Aggressive nav line filtering (link density analysis)",
            "Enhanced validation with v1 comparison metrics",
            "Content preservation safeguards (headings, code, lists)",
        ],
        metrics={
            "source_version": latest_version,
            "documents_input": 0,
            "documents_output": 0,
            "documents_rejected": 0,
            "avg_content_reduction": "0%",
        }
    )
    
    logger.info(f"\nProcessing into version: {version_name}")
    logger.info(f"Version directory: {version_dir}")
    
    # Load v1 documents
    logger.info(f"\n[LOADING] Reading {latest_version} documents...")
    json_files = list(v1_dir.glob("*.md"))
    logger.info(f"Found {len(json_files)} documents to enhance")
    
    # Process each v1 document with AdvancedCleaner
    cleaner = AdvancedCleaner()
    validator_log = []
    documents_output = []
    anomalies = []
    total_original_lines = 0
    total_final_lines = 0
    
    for i, md_file in enumerate(json_files, 1):
        try:
            # Read v1 cleaned content
            with open(md_file, 'r', encoding='utf-8') as f:
                v1_content = f.read()
            
            # Apply Phase 2 cleaning
            v2_content = cleaner.clean(v1_content)
            
            # Get metrics
            v1_lines = len(v1_content.split('\n'))
            v2_lines = len(v2_content.split('\n'))
            reduction = ((v1_lines - v2_lines) / v1_lines * 100) if v1_lines > 0 else 0
            
            if reduction > 40:
                anomalies.append(f"{md_file.name}: Suspicious reduction ({reduction:.1f}%) - {v1_lines} -> {v2_lines} lines")
            
            total_original_lines += v1_lines
            total_final_lines += v2_lines
            
            # Save v2 document
            output_path = version_dir / "documents" / md_file.name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(v2_content)
            
            documents_output.append({
                "filename": md_file.name,
                "v1_lines": v1_lines,
                "v2_lines": v2_lines,
                "reduction_percent": round(reduction, 1),
                "status": "processed",
                "flagged": reduction > 40
            })
            
            logger.info(
                f"[{i}/{len(json_files)}] ✓ {md_file.name:50s} | "
                f"Lines: {v1_lines} → {v2_lines} ({reduction:+.1f}%)"
            )
            
        except Exception as e:
            logger.error(f"[FAIL] Error processing {md_file.name}: {e}")
            documents_output.append({
                "filename": md_file.name,
                "status": "failed",
                "error": str(e)
            })
            
    # Write anomaly log if needed
    if anomalies:
        anomaly_log_path = version_dir / "anomaly_log.txt"
        with open(anomaly_log_path, 'w', encoding='utf-8') as f:
            f.write("Phase 2 Anomaly Log (Reduction > 40%)\n")
            f.write("=" * 60 + "\n")
            f.write("\n".join(anomalies))
        logger.warning(f"Found {len(anomalies)} documents with suspiciously high reduction rates. See {anomaly_log_path}")
    
    # Generate metrics
    avg_reduction = ((total_original_lines - total_final_lines) / total_original_lines * 100) \
        if total_original_lines > 0 else 0
    
    logger.info(f"\nProcessing Summary:")
    logger.info(f"  - Total Input Documents: {len(json_files)}")
    logger.info(f"  - Successfully Processed: {len(documents_output)}")
    logger.info(f"  - Avg Lines Removed: {avg_reduction:.1f}%")
    logger.info(f"  - Total Lines: {total_original_lines} → {total_final_lines}")
    
    # Save processing reports
    logger.info(f"\n[SAVING] Writing v2 documents and reports...")
    
    # Update version manifest
    version_manifest = {
        "version": version_name,
        "phase": "Phase 2: Advanced Cleaning",
        "source_version": latest_version,
        "documents_processed": len(documents_output),
        "avg_content_reduction_percent": round(avg_reduction, 1),
        "metrics": {
            "total_input_lines": total_original_lines,
            "total_output_lines": total_final_lines,
            "avg_lines_per_doc_before": round(total_original_lines / len(json_files), 1),
            "avg_lines_per_doc_after": round(total_final_lines / len(documents_output), 1),
        }
    }
    
    manifest_path = version_dir / "version_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(version_manifest, f, indent=2)
    
    logger.info(f"[OK] Manifest saved: {manifest_path}")
    
    # Save detailed processing report
    report_path = version_dir / "processing_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "version": version_name,
            "summary": {
                "documents_processed": len(documents_output),
                "avg_content_reduction_percent": round(avg_reduction, 1),
                "total_lines_removed": total_original_lines - total_final_lines,
            },
            "documents": documents_output
        }, f, indent=2)
    
    logger.info(f"[OK] Report saved: {report_path}")
    
    # Update version history
    version_mgr.save_version_history()
    history_file = Path(processed_docs_base) / 'VERSION_HISTORY.md'
    logger.info(f"[OK] Version history updated: {history_file}")
    
    logger.info("\n" + "=" * 80)
    logger.info(f"PHASE 2 COMPLETE - Version {version_name}")
    logger.info("=" * 80)
    logger.info(f"\nVersion Information:")
    logger.info(f"  Version: {version_name}")
    logger.info(f"  Location: {version_dir}")
    logger.info(f"  Documents: {version_dir / 'documents'}")
    logger.info(f"  Manifest: {manifest_path}")
    logger.info(f"  Report: {report_path}")
    logger.info(f"\nNext Steps:")
    logger.info(f"  1. Review {report_path} for Phase 2 metrics")
    logger.info(f"  2. Compare v1 vs v2 metrics")
    logger.info(f"  3. Run: python scripts/run_phase3.py")
    logger.info(f"  4. Continue with Phase 3 if needed")


if __name__ == "__main__":
    main()
