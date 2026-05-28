"""
Content cleaning pipeline to remove noise and ensure data quality.
Includes cleaner, deduplicator, and validator modules.
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ContentCleaner:
    """Removes navigation noise and unwanted content from markdown."""
    
    def __init__(self):
        self.patterns_to_remove = [
            (r"^#+\s*Navigation.*?(?=^#+|\Z)", "navigation heading"),
            (r"^#+\s*(Feedback|Send feedback).*?(?=^#+|\Z)", "feedback section"),
            (r"^#+\s*(Related|See also).*?(?=^#+|\Z)", "related links section"),
            (r"^\s*[\*\-]\s+\[.*?\]\(.*?\)\s*$", "breadcrumb"),
            (r"(?:^|\n)[\*\-\+]\s{1,}\[.*?\]\(.*?\)(?:\n|$)", "single-item lists (likely nav)"),
        ]
    
    def clean(self, content: str, title: str = "") -> str:
        """
        Clean markdown content by removing noise.
        
        Args:
            content: Raw markdown content
            title: Page title (helps identify sections to keep)
        
        Returns:
            Cleaned markdown content
        """
        # Remove common noise patterns
        for pattern, reason in self.patterns_to_remove:
            content = re.sub(pattern, "", content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove excessive whitespace
        content = re.sub(r"\n\n\n+", "\n\n", content)
        
        # Remove lines that are only navigation-like content
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like pure navigation
            if self._is_navigation_line(line):
                continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Final whitespace cleanup
        content = content.strip()
        
        return content
    
    def _is_navigation_line(self, line: str) -> bool:
        """Check if a line is likely navigation content."""
        line_lower = line.lower().strip()
        
        # Very short lines with only links
        if len(line_lower) < 50 and line.count('[') > 0 and line.count(']') > 0:
            # But keep lines with meaningful text
            text_part = re.sub(r'\[.*?\]\(.*?\)', '', line_lower)
            if len(text_part.strip()) < 10:
                return True
        
        # Skip empty lines (kept separately)
        if not line_lower:
            return False
        
        return False


class DuplicateRemover:
    """Detects and removes duplicate documents."""
    
    def __init__(self):
        self.content_hashes = {}  # hash -> (url, title)
        self.removed_duplicates = []
    
    def is_duplicate(self, content: str, url: str) -> bool:
        """
        Check if content is duplicate.
        
        Args:
            content: Document content
            url: Document URL
        
        Returns:
            True if duplicate, False if new
        """
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
        """Generate hash of content for duplicate detection."""
        # Normalize before hashing
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_report(self) -> dict:
        """Get duplicate removal report."""
        return {
            "total_duplicates_removed": len(self.removed_duplicates),
            "removed": self.removed_duplicates,
        }


class ContentValidator:
    """Validates document quality and rejects low-quality content."""
    
    def __init__(
        self,
        min_words: int = 100,
        max_words: int = 15000,
    ):
        """
        Args:
            min_words: Minimum word count (discard if below)
            max_words: Maximum word count (discard if above, likely auto-generated)
        """
        self.min_words = min_words
        self.max_words = max_words
        self.validation_log = []
    
    def validate(self, content: str, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate document content.
        
        Args:
            content: Markdown content
            url: Document URL
        
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        # Check word count
        word_count = len(content.split())
        
        if word_count < self.min_words:
            reason = f"Too short: {word_count} words (min: {self.min_words})"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        if word_count > self.max_words:
            reason = f"Too long: {word_count} words (max: {self.max_words})"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        # Check for markdown syntax validity
        if not self._is_valid_markdown(content):
            reason = "Invalid markdown syntax"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        return True, None
    
    def _is_valid_markdown(self, content: str) -> bool:
        """Check if markdown has valid syntax."""
        # Check for balanced code fences
        code_fences = content.count('```')
        if code_fences % 2 != 0:
            return False
        
        # Check for balanced brackets
        if content.count('[') != content.count(']'):
            return False
        
        return True
    
    def get_report(self) -> dict:
        """Get validation report."""
        report = {
            "total_validated": len(self.validation_log),
            "validations": self.validation_log,
        }
        return report


class ProcessingPipeline:
    """Orchestrates cleaning, deduplication, and validation."""
    
    def __init__(
        self,
        raw_dir: str = "./raw_docs",
        processed_dir: str = "./processed_docs",
        min_words: int = 100,
        max_words: int = 15000,
    ):
        """
        Args:
            raw_dir: Directory with raw crawled documents
            processed_dir: Directory to save processed documents
            min_words: Minimum word count for valid documents
            max_words: Maximum word count for valid documents
        """
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        self.cleaner = ContentCleaner()
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
        """
        Process all documents in raw_dir.
        
        Returns:
            List of processed document metadata
        """
        logger.info(f"Starting processing pipeline from {self.raw_dir}")
        
        # Find all JSON files in raw_docs
        json_files = list(self.raw_dir.glob("*.json"))
        self.processing_log["total_input"] = len(json_files)
        
        logger.info(f"Found {len(json_files)} raw documents")
        
        for json_file in json_files:
            try:
                # Load raw document
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                # Extract fields
                url = doc_data.get("url")
                title = doc_data.get("title", "")
                content = doc_data.get("markdown_content", "")
                
                # Step 1: Clean
                cleaned_content = self.cleaner.clean(content, title)
                self.processing_log["cleaned"] += 1
                
                # Step 2: Check for duplicates
                if self.deduplicator.is_duplicate(cleaned_content, url):
                    self.processing_log["deduplicated"] += 1
                    logger.info(f"⊘ Duplicate removed: {url}")
                    continue
                
                # Step 3: Validate
                is_valid, reason = self.validator.validate(cleaned_content, url)
                if not is_valid:
                    self.processing_log["failed"] += 1
                    logger.info(f"[FAIL] Validation failed ({reason}): {url}")
                    continue
                
                self.processing_log["validated"] += 1
                
                # Save processed document
                processed_data = doc_data.copy()
                processed_data["markdown_content"] = cleaned_content
                processed_data["processing_timestamp"] = str(json_file.stat().st_mtime)
                
                self._save_processed(processed_data)
                self.processed_docs.append(processed_data)
                
                logger.info(f"[OK] Processed: {url}")
            
            except Exception as e:
                self.processing_log["failed"] += 1
                logger.error(f"Error processing {json_file}: {e}")
        
        logger.info(str(self._get_summary()))
        return self.processed_docs
    
    def _save_processed(self, doc_data: dict):
        """Save processed document."""
        filename = Path(doc_data.get("url", "index")).name + ".json"
        filename = re.sub(r'[^a-z0-9._-]', '_', filename.lower())
        
        path = self.processed_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, default=str)
    
    def _get_summary(self) -> str:
        """Generate processing summary."""
        return f"""
Processing Summary:
  - Total Input Documents: {self.processing_log['total_input']}
  - Cleaned: {self.processing_log['cleaned']}
  - Deduplicated: {self.processing_log['deduplicated']}
  - Validated & Kept: {self.processing_log['validated']}
  - Failed/Discarded: {self.processing_log['failed']}
  - Final Count: {len(self.processed_docs)}
        """
    
    def save_reports(self, output_dir: str = "./processed_docs"):
        """Save detailed processing reports."""
        output_dir = Path(output_dir)
        
        reports = {
            "processing_log": self.processing_log,
            "deduplication_report": self.deduplicator.get_report(),
            "validation_report": self.validator.get_report(),
        }
        
        path = output_dir / "processing_reports.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, default=str)
        
        logger.info(f"Reports saved to {path}")
        return path
