import os
from pathlib import Path
from src.processing.cleaner import ProcessingPipeline
from scripts.version_utils import get_latest_version, get_next_version

def main():
    raw_base = Path("raw_docs")
    processed_base = Path("processed_docs")
    
    # Get the latest raw_docs version
    latest_raw_version = get_latest_version(raw_base)
    if latest_raw_version == "v0":
        print("No raw documents found. Run Phase 1 first.")
        return
        
    input_dir = raw_base / latest_raw_version
    
    # Determine the next processed_docs version
    processed_base.mkdir(exist_ok=True)
    next_processed_version = get_next_version(processed_base)
    output_dir = processed_base / next_processed_version
    
    reports_dir = Path(f"reports/processing_{next_processed_version}")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Phase 2 Cleaner")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Reports: {reports_dir}")
    
    pipeline = ProcessingPipeline(
        raw_dir=str(input_dir),
        processed_dir=str(output_dir),
        version=next_processed_version
    )
    
    pipeline.process()
    pipeline.save_reports(output_dir=str(reports_dir))
    
    print(f"Phase 2 Complete. Processed documents saved to: {output_dir}")

if __name__ == "__main__":
    main()
