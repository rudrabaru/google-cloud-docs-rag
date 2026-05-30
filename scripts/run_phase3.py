#!/usr/bin/env python
"""
Phase 3: Document Quality Enhancements and Validation.

This script:
1. Loads Phase 2 processed documents (v4)
2. Applies Processor for table normalization, heading extraction, and structural metadata
3. Computes structure-preservation metrics
4. Saves Phase 3 cleaned documents to processed_docs/v5/
5. Saves companion .meta.json files for each document
6. Generates Phase 3 processing reports
"""

import sys
import os
import json
import logging
from pathlib import Path

# Set root directory
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.processing.quality import Processor
from src.versioning import VersionManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 80)
    logger.info("PHASE 3: Document Quality Enhancements and Metadata Generation")
    logger.info("=" * 80)
    
    processed_docs_base = str(ROOT_DIR / "processed_docs")
    version_mgr = VersionManager(processed_docs_base)
    
    latest_version = version_mgr.get_latest_version()
    if not latest_version:
        logger.error("No previous version found. Run previous processors first.")
        sys.exit(1)
        
    logger.info(f"Loading from version: {latest_version}")
    v_dir = version_mgr.get_documents_dir(latest_version)
    
    version_name = version_mgr.get_next_version()
    version_dir = version_mgr.create_version(
        phase="Phase 3: Quality Enhancements & Metadata Generation",
        enhancements=[
            "Heading hierarchy extraction",
            "Table normalization and repair",
            "Structural metadata generation (.meta.json)",
            "Structure-preservation metrics"
        ],
        metrics={
            "source_version": latest_version,
            "documents_processed": 0
        }
    )
    
    logger.info(f"\nProcessing into version: {version_name}")
    json_files = list(v_dir.glob("*.md"))
    logger.info(f"Found {len(json_files)} documents to enhance")
    
    processor = Processor()
    documents_output = []
    
    # Validation totals
    total_metrics = {
        "headings_before": 0, "headings_after": 0,
        "lists_before": 0, "lists_after": 0,
        "tables_before": 0, "tables_after": 0,
        "code_blocks_before": 0, "code_blocks_after": 0
    }
    
    for i, md_file in enumerate(json_files, 1):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            metrics_before = processor._count_structural_elements(content)
            
            normalized_content, metadata = processor.process(content)
            
            metrics_after = metadata["structural_elements"]
            
            # Aggregate metrics
            for key in ["headings", "lists", "tables", "code_blocks"]:
                total_metrics[f"{key}_before"] += metrics_before[key]
                total_metrics[f"{key}_after"] += metrics_after[key]
                
            # Write .md
            output_path_md = version_dir / "documents" / md_file.name
            output_path_md.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path_md, 'w', encoding='utf-8', errors='replace') as f:
                f.write(normalized_content)
                
            # Write .meta.json
            output_path_meta = output_path_md.with_suffix('.meta.json')
            with open(output_path_meta, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
                
            documents_output.append({
                "filename": md_file.name,
                "status": "processed",
                "metrics_before": metrics_before,
                "metrics_after": metrics_after
            })
            
            if i % 10 == 0 or i == len(json_files):
                logger.info(f"Processed {i}/{len(json_files)} documents")
                
        except Exception as e:
            logger.error(f"Error processing {md_file.name}: {e}")
            
    logger.info("\nValidation Metrics (Structure Preservation):")
    for key in ["headings", "lists", "tables", "code_blocks"]:
        before = total_metrics[f"{key}_before"]
        after = total_metrics[f"{key}_after"]
        diff = after - before
        logger.info(f"  - {key.capitalize()}: {before} → {after} ({diff:+})")
        
    # Save Report
    report_path = version_dir / "processing_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "version": version_name,
            "summary": {
                "documents_processed": len(documents_output),
                "structure_preservation": total_metrics
            },
            "documents": documents_output
        }, f, indent=2)
        
    # Update manifest
    manifest_path = version_dir / "version_manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    manifest["documents_processed"] = len(documents_output)
    manifest["structure_preservation"] = total_metrics
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        
    version_mgr.save_version_history()
    
    logger.info(f"\nPHASE 3 COMPLETE - {version_name}")
    logger.info(f"Report: {report_path}")

if __name__ == "__main__":
    main()
