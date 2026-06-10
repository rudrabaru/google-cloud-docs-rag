import glob
import json
import os
import random
from pathlib import Path
from typing import List, Dict

from src.crawling.metadata import CrawledDocument
from src.processing.models import ProcessedDocument, Block
from src.processing.cleaner import DocumentCleaner
from src.processing.validator import ProcessingValidator

class ProcessingPipeline:
    def __init__(self, raw_dir: str, output_dir: str):
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "metrics").mkdir(exist_ok=True)
        (self.output_dir / "review").mkdir(exist_ok=True)
        
    def run(self):
        print("Starting Document Processing Pipeline...")
        
        # 1. Load documents
        json_files = glob.glob(f"{self.raw_dir}/*.json")
        raw_docs = []
        for f in json_files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    raw_docs.append(CrawledDocument(**data))
            except Exception as e:
                print(f"Error loading {f}: {e}")
                
        total_docs = len(raw_docs)
        print(f"Loaded {total_docs} documents.")
        if total_docs == 0:
            return
            
        cleaner = DocumentCleaner(total_docs)
        
        # 2. Parse blocks and compute frequencies (Pass 1)
        all_blocks_across_docs = []
        for doc in raw_docs:
            blocks = cleaner.parse_blocks(doc.markdown_content)
            all_blocks_across_docs.append(blocks)
            
        print("Computing corpus frequencies...")
        cleaner.process_corpus_frequencies(all_blocks_across_docs)
        
        processed_docs = []
        
        # 3. Clean and Validate (Pass 2)
        print("Cleaning and validating documents...")
        for i, doc in enumerate(raw_docs):
            blocks = all_blocks_across_docs[i]
            
            cleaned_blocks = cleaner.clean_document_blocks(blocks)
            
            # Count removals
            removed_blocks = sum(1 for b in blocks if b.is_removed)
            retained_blocks = len(cleaned_blocks)
            
            # Create ProcessedDocument
            pdoc = ProcessedDocument(**doc.model_dump())
            pdoc.blocks = blocks # include all blocks for review purposes
            pdoc.processing_stats.blocks_removed = removed_blocks
            pdoc.processing_stats.blocks_retained = retained_blocks
            
            # Generic page type classification based on URL paths
            url_lower = pdoc.url.lower()
            if "/tutorial" in url_lower or "/example" in url_lower:
                pdoc.page_category = "tutorial"
            elif "/api" in url_lower or "/reference" in url_lower:
                pdoc.page_category = "reference"
            elif "/overview" in url_lower or pdoc.url.endswith("/docs") or pdoc.url.endswith("/docs/"):
                pdoc.page_category = "overview"
            else:
                pdoc.page_category = "guide"
            
            # Validate
            ProcessingValidator.validate_document(doc.markdown_content, cleaned_blocks, pdoc)
            
            processed_docs.append(pdoc)
            
        # 4. Save results
        print("Saving processed documents...")
        for pdoc in processed_docs:
            # Create a safe filename
            safe_name = pdoc.url.split('://')[-1].replace('/', '_').replace('.', '_')
            
            # Save JSON (excluding full blocks to save space)
            json_path = self.output_dir / f"{safe_name}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(pdoc.model_dump_json(indent=2, exclude={'blocks', 'raw_html'}))
                
            # Save MD
            md_path = self.output_dir / f"{safe_name}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(pdoc.cleaned_markdown)
                
        # 5. Generate Reports
        print("Generating reports...")
        report = ProcessingValidator.generate_corpus_report(processed_docs)
        with open(self.output_dir / "metrics" / "processing_report.json", "w", encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        # Also save repeating blocks info (Boilerplate candidates)
        sorted_blocks = sorted(cleaner.block_document_counts.items(), key=lambda x: x[1], reverse=True)
        top_boilerplate = [{"hash": k, "count": v, "percentage": (v/total_docs)*100} for k, v in sorted_blocks[:100]]
        with open(self.output_dir / "metrics" / "repeated_blocks_report.json", "w", encoding='utf-8') as f:
            json.dump(top_boilerplate, f, indent=2)
            
        # Removed blocks report
        removed_blocks_report = []
        for doc in processed_docs:
            for b in doc.blocks:
                if b.is_removed:
                    removed_blocks_report.append({
                        "content_preview": b.content[:100].replace('\n', ' '),
                        "document_frequency": b.metrics.document_frequency,
                        "position": b.metrics.position_ratio,
                        "link_density": b.metrics.link_density,
                        "boilerplate_score": b.boilerplate_score,
                        "removal_reason": b.removal_reason,
                        "triggered_signals": getattr(b, 'triggered_signals', [])
                    })
        with open(self.output_dir / "metrics" / "removed_blocks_report.json", "w", encoding='utf-8') as f:
            json.dump(removed_blocks_report, f, indent=2)

        # Boilerplate detection report (summary of signals)
        signal_counts = {}
        for doc in processed_docs:
            for b in doc.blocks:
                for s in getattr(b, 'triggered_signals', []):
                    signal_counts[s] = signal_counts.get(s, 0) + 1
        with open(self.output_dir / "metrics" / "boilerplate_detection_report.json", "w", encoding='utf-8') as f:
            json.dump({"total_blocks_processed": sum(len(d.blocks) for d in processed_docs), "signals_triggered": signal_counts}, f, indent=2)
            
        # 6. Generate Manual Review Set
        print("Generating manual review set...")
        self._generate_review_set(processed_docs)
        print("Pipeline complete!")
        
    def _generate_review_set(self, processed_docs: List[ProcessedDocument]):
        # Select up to 15 documents representing different categories
        categories = {}
        for doc in processed_docs:
            categories.setdefault(doc.page_category, []).append(doc)
            
        review_samples = []
        # Take up to 4 from each category
        for cat, docs in categories.items():
            sample_size = min(4, len(docs))
            samples = random.sample(docs, sample_size)
            review_samples.extend(samples)
            
        review_data = []
        for doc in review_samples:
            removed_sections = [
                {"content": b.content, "reason": b.removal_reason, "score": b.boilerplate_score, "signals": getattr(b, 'triggered_signals', [])}
                for b in doc.blocks if b.is_removed
            ]
            preserved_sections = [
                {"content": b.content[:200], "score": b.boilerplate_score, "signals": getattr(b, 'triggered_signals', [])}
                for b in doc.blocks if not b.is_removed and b.boilerplate_score < 4.0
            ]
            borderline_sections = [
                {"content": b.content, "score": b.boilerplate_score, "signals": getattr(b, 'triggered_signals', [])}
                for b in doc.blocks if not b.is_removed and b.boilerplate_score >= 4.0
            ]
            review_data.append({
                "url": doc.url,
                "category": doc.page_category,
                "stats": doc.processing_stats.model_dump(),
                "removed_sections_count": len(removed_sections),
                "removed_sections": removed_sections[:10],
                "borderline_sections": borderline_sections,
                "preserved_sections_sample": preserved_sections[:5]
            })
            
        with open(self.output_dir / "review" / "review_set.json", "w", encoding='utf-8') as f:
            json.dump(review_data, f, indent=2)
