import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from src.processing.pipeline import ProcessingPipeline
from scripts.version_utils import get_latest_version, get_next_version

if __name__ == "__main__":
    raw_base = Path("raw_docs")
    processed_base = Path("processed_docs")
    
    # Get the latest raw_docs version
    latest_raw_version = get_latest_version(raw_base)
    if latest_raw_version == "v0":
        print("No raw documents found. Run Phase 1 first.")
        sys.exit(1)
        
    input_dir = raw_base / latest_raw_version
    
    # Determine the next processed_docs version
    processed_base.mkdir(exist_ok=True)
    next_processed_version = get_next_version(processed_base)
    output_dir = processed_base / next_processed_version
    
    print(f"Starting Phase 2 Processing")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    
    pipeline = ProcessingPipeline(raw_dir=str(input_dir), output_dir=str(output_dir))
    pipeline.run()
    
    print(f"Phase 2 Complete. Processed documents saved to: {output_dir}")
