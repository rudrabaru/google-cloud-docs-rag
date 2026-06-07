import json
from pathlib import Path
from src.chunking.chunker import DocumentChunker
from src.chunking.metadata import ChunkingConfig
from scripts.version_utils import get_latest_version, get_next_version

def main():
    processed_base = Path("processed_docs")
    chunks_base = Path("chunks")
    
    # Get latest processed_docs version
    latest_processed_version = get_latest_version(processed_base)
    if latest_processed_version == "v0":
        print("No processed documents found. Run Phase 2 first.")
        return
        
    input_dir = processed_base / latest_processed_version
    
    # Determine the next chunks version
    chunks_base.mkdir(exist_ok=True)
    next_chunks_version = get_next_version(chunks_base)
    output_dir = chunks_base / next_chunks_version
    output_dir.mkdir(exist_ok=True)
    
    print(f"Starting Phase 3 Chunker")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    
    reports_dir = Path(f"reports/chunking_{next_chunks_version}")
    reports_dir.mkdir(parents=True, exist_ok=True)
    print(f"Reports: {reports_dir}")
    
    config = ChunkingConfig(
        source_version=latest_processed_version,
        output_version=next_chunks_version
    )
    
    chunker = DocumentChunker(config=config)
    
    # Load all processed documents
    docs = []
    for json_file in input_dir.glob("*.json"):
        if json_file.name == "processing_report.json":
            continue
        with open(json_file, 'r', encoding='utf-8') as f:
            docs.append(json.load(f))
            
    # Chunk
    all_chunks = chunker.chunk_batch(docs)
    
    # Save chunks
    for chunk in all_chunks:
        chunk_path = output_dir / f"{chunk.chunk_id}.json"
        with open(chunk_path, 'w', encoding='utf-8') as f:
            json.dump(chunk.model_dump(mode='json'), f, indent=2, default=str)
            
    chunker.save_reports(output_dir=str(reports_dir))
            
    print(f"Phase 3 Complete. Generated {len(all_chunks)} chunks in: {output_dir}")

if __name__ == "__main__":
    main()
