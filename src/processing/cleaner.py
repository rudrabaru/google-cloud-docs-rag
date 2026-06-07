"""
Content cleaning pipeline to remove noise and ensure data quality.
Includes generic cleaner, deduplicator, and validator modules.
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from src.classification.pipeline import ClassificationPipeline

logger = logging.getLogger(__name__)


class GenericCleaner:
    """
    Wrapper around the multi-signal Classification Pipeline.
    Replaces old keyword-based cleaners.
    """
    
    def __init__(self):
        self.pipeline = ClassificationPipeline()
        
    def clean(self, content: str, title: str = "", url: str = "") -> str:
        """
        Clean markdown content using signal-based classification.
        """
        if not content:
            return ""
            
        metadata = {"title": title, "url": url}
        cleaned_text = self.pipeline.process_document(content, metadata)
        
        # Cleanup excessive whitespace
        cleaned_text = re.sub(r"\n\n\n+", "\n\n", cleaned_text)
        return cleaned_text.strip()


class DuplicateRemover:
    """Detects and removes duplicate documents."""
    
    def __init__(self):
        self.content_hashes = {}  # hash -> (url, title)
        self.removed_duplicates = []
    
    def is_duplicate(self, content: str, url: str) -> bool:
        content_hash = self._hash_content(content)
        
        if content_hash in self.content_hashes:
            self.removed_duplicates.append({
                "url": url,
                "original_url": self.content_hashes[content_hash][0],
                "reason": "exact_duplicate"
            })
            return True
        
        self.content_hashes[content_hash] = (url, content[:100])
        return False
    
    def _hash_content(self, content: str) -> str:
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_report(self) -> dict:
        return {
            "total_duplicates_removed": len(self.removed_duplicates),
            "removed": self.removed_duplicates,
        }


class ContentValidator:
    """Validates document quality and rejects low-quality content without hardcoded domain knowledge."""
    
    def __init__(
        self,
        min_words: int = 100,
        max_words: int = 15000,
    ):
        self.min_words = min_words
        self.max_words = max_words
        self.validation_log = []
    
    def validate(self, content: str, url: str) -> Tuple[bool, Optional[str]]:
        """Validate document content with critical checks only."""
        word_count = len(content.split())
        if not (self.min_words <= word_count <= self.max_words):
            reason = f"Too short/long: {word_count} words (range: {self.min_words}-{self.max_words})"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        if not self._is_valid_markdown(content):
            reason = "Invalid markdown syntax (seriously broken structure)"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        heading_count = sum(1 for line in content.split('\n') if line.startswith('#'))
        if heading_count < 1:
            reason = "No heading structure found (no content hierarchy)"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        return True, None
    
    def validate_comprehensive(self, content: str, url: str) -> dict:
        checks = {}
        
        word_count = len(content.split())
        checks['word_count_valid'] = self.min_words <= word_count <= self.max_words
        checks['markdown_valid'] = self._is_valid_markdown(content)
        
        # Check 3: Sidebar removed - link density should be reasonable
        link_count = content.count('[')
        para_count = len([l for l in content.split('\n') if len(l.strip()) > 20])
        link_density = link_count / max(para_count, 1)
        checks['sidebar_removed'] = link_density < 0.5
        
        # Check 4: Heading hierarchy present
        heading_count = sum(1 for line in content.split('\n') if line.startswith('#'))
        checks['heading_hierarchy_extracted'] = heading_count >= 1
        
        return checks
    
    def _is_valid_markdown(self, content: str) -> bool:
        lines = content.split('\n')
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
        
        if in_code_block:
            return False
        
        for line in lines:
            if line.strip().startswith('```'):
                continue
            
            bracket_stack = []
            in_link = False
            i = 0
            while i < len(line):
                if line[i] == '[':
                    bracket_stack.append('[')
                    in_link = True
                elif line[i] == ']':
                    if bracket_stack and bracket_stack[-1] == '[':
                        bracket_stack.pop()
                        in_link = False
                elif line[i] == '(' and in_link:
                    bracket_stack.append('(')
                elif line[i] == ')' and in_link:
                    if bracket_stack and bracket_stack[-1] == '(':
                        bracket_stack.pop()
                i += 1
            
            if len(bracket_stack) > 3:
                return False
        
        return True
    
    def get_report(self) -> dict:
        return {
            "total_validated": len(self.validation_log),
            "validations": self.validation_log,
        }


class ProcessingPipeline:
    """Orchestrates cleaning, deduplication, and validation."""
    
    def __init__(
        self,
        raw_dir: str = "./raw_docs",
        processed_dir: str = "./processed_docs",
        min_words: int = 100,
        max_words: int = 15000,
        version: str = "v1",
    ):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.version = version
        
        self.cleaner = GenericCleaner()
        self.deduplicator = DuplicateRemover()
        self.validator = ContentValidator(min_words, max_words)
        
        self.processed_docs = []
        self.processing_log = {
            "total_input": 0,
            "cleaned": 0,
            "deduplicated": 0,
            "validated": 0,
            "failed": 0,
        }
    
    def process(self) -> List[dict]:
        logger.info(f"Starting processing pipeline from {self.raw_dir}")
        json_files = list(self.raw_dir.glob("*.json"))
        self.processing_log["total_input"] = len(json_files)
        logger.info(f"Found {len(json_files)} raw documents")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                url = doc_data.get("url", "")
                title = doc_data.get("title", "")
                content = doc_data.get("markdown_content", "")
                
                # Clean
                cleaned_content = self.cleaner.clean(content, title, url)
                self.processing_log["cleaned"] += 1
                
                # Check for duplicates
                if self.deduplicator.is_duplicate(cleaned_content, url):
                    self.processing_log["deduplicated"] += 1
                    continue
                
                # Validate
                is_valid, reason = self.validator.validate(cleaned_content, url)
                if not is_valid:
                    self.processing_log["failed"] += 1
                    continue
                
                self.processing_log["validated"] += 1
                
                # Save processed document
                processed_data = doc_data.copy()
                processed_data["markdown_content"] = cleaned_content
                processed_data["processing_timestamp"] = str(datetime.utcnow() if 'datetime' in globals() else json_file.stat().st_mtime)
                processed_data["document_version"] = self.version
                
                self._save_processed(processed_data)
                self.processed_docs.append(processed_data)
            
            except Exception as e:
                self.processing_log["failed"] += 1
                logger.error(f"Error processing {json_file}: {e}")
        
        return self.processed_docs
    
    def _save_processed(self, doc_data: dict):
        filename = Path(doc_data.get("url", "index")).name + ".json"
        filename = re.sub(r'[^a-z0-9._-]', '_', filename.lower())
        
        # Save JSON
        json_path = self.processed_dir / filename
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, default=str)
            
        # Save Markdown
        md_filename = filename.replace('.json', '.md')
        md_path = self.processed_dir / md_filename
        with open(md_path, 'w', encoding='utf-8') as f:
            title = doc_data.get("title", "Untitled")
            url = doc_data.get("url", "")
            f.write(f"# {title}\n\n")
            f.write(f"**Source:** {url}\n")
            f.write(f"**Version:** {self.version}\n\n")
            f.write(doc_data.get("markdown_content", ""))
    
    def save_reports(self, output_dir: str = "./reports/processing", filename: str = "processing_report.json") -> str:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        report_file = output_path / filename
        
        report = {
            "processing_summary": self.processing_log,
            "deduplication_report": self.deduplicator.get_report(),
            "validation_report": self.validator.get_report()
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        return str(report_file)
