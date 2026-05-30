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
    """
    Advanced content cleaner that removes navigation, boilerplate, and sidebar noise
    while preserving documentation content.
    
    Strategy:
    1. Remove footer sections (copyright, terms, etc.)
    2. Remove language selectors
    3. Detect and remove navigation/sidebar structure
    4. Find main content start
    5. Preserve documentation headings, lists, code blocks
    """
    
    def __init__(self):
        
        # Footer keywords
        self.footer_keywords = {
            'send feedback', 'last updated', 'license', 'copyright',
            'terms of service', 'privacy policy', 'help', 'contact us',
            'except as otherwise noted', 'google developers', 'site policies',
            'creative commons', 'apache 2.0', 'except as otherwise'
        }
        
        # Language names
        self.language_keywords = {
            'english', 'deutsch', 'français', 'español', 'italiano',
            'português', '日本語', '中文', '한국어', 'русский',
            'polski', 'ไทย', 'العربية', 'עברית'
        }
        
        # Navigation keywords
        self.nav_keywords = {
            'skip to', 'technology areas', 'cross-product', 'sign in',
            'start free', 'more', 'close', 'product category', 'overviews',
            'guides', 'reference', 'resources', 'tutorials'
        }
    
    def clean(self, content: str, title: str = "") -> str:
        """
        Clean markdown content aggressively removing navigation.
        
        Args:
            content: Raw markdown content
            title: Page title (helps identify sections to keep)
        
        Returns:
            Cleaned markdown content
        """
        # Step 1: Remove footer
        content = self._remove_footer(content)
        
        # Step 2: Remove language selectors
        content = self._remove_language_selectors(content)
        
        # Step 3: Remove navigation sections
        content = self._remove_nav_sections(content)
        
        # Step 4: Remove pure navigation lines (link-only lines)
        content = self._remove_nav_lines(content)
        
        # Step 5: Find and keep main content
        content = self._extract_main_content(content)
        
        # Step 6: Cleanup excessive whitespace
        content = re.sub(r"\n\n\n+", "\n\n", content)
        content = content.strip()
        
        return content
    
    def _remove_footer(self, content: str) -> str:
        """Remove footer section from end of content."""
        lines = content.split('\n')
        footer_start = len(lines)
        
        # Scan from end to find footer
        for i in range(len(lines) - 1, -1, -1):
            line_lower = lines[i].lower().strip()
            
            # Check for footer keywords
            if any(kw in line_lower for kw in self.footer_keywords):
                footer_start = max(0, i - 2)
                break
        
        return '\n'.join(lines[:footer_start]).strip()
    
    def _remove_language_selectors(self, content: str) -> str:
        """Remove language selector blocks."""
        return '\n'.join(line for line in content.split('\n') if line.lower().strip() not in self.language_keywords)
    
    def _remove_nav_sections(self, content: str) -> str:
        """Remove navigation section headers and their content using content-aware classification."""
        lines = content.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if line is a heading
            if re.match(r'^#{1,6}\s', line):
                # Collect the section content
                section_lines = [line]
                j = i + 1
                while j < len(lines) and not re.match(r'^#{1,6}\s', lines[j]):
                    section_lines.append(lines[j])
                    j += 1
                
                # Analyze section content to see if it's purely navigation/boilerplate
                if self._is_nav_or_boilerplate_section(section_lines):
                    # Skip this section entirely
                    i = j
                    continue
            
            result.append(lines[i])
            i += 1
            
        return '\n'.join(result)
        
    def _is_nav_or_boilerplate_section(self, section_lines: list) -> bool:
        """Analyze if a section's content is purely navigation, boilerplate, feedback, or marketing."""
        if len(section_lines) <= 1:
            return False # Empty section, keep it just in case
            
        content_lines = section_lines[1:]
        text_content = '\n'.join(content_lines).strip()
        
        if not text_content:
            return False
            
        # Count links vs prose
        link_count = text_content.count('[')
        text_no_links = re.sub(r'\[.*?\]\(.*?\)', '', text_content)
        words = text_no_links.split()
        
        # If it's very short and has high link density -> likely nav
        if link_count > 0 and len(words) < 20:
            return True
            
        # Check for feedback/boilerplate
        text_lower = text_content.lower()
        if any(kw in text_lower for kw in ['was this helpful', 'send feedback', 'rate this page', 'privacy policy']):
            return True
            
        return False
    
    def _remove_nav_lines(self, content: str) -> str:
        """Remove pure navigation lines (link-only, no text)."""
        lines = content.split('\n')
        cleaned = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                cleaned.append(line)
                continue
            
            # Check for link-only lines
            if self._is_pure_nav_line(line):
                continue
            
            cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def _is_pure_nav_line(self, line: str) -> bool:
        """Check if line is pure navigation (only links/keywords, no content)."""
        line_lower = line.lower().strip()
        
        # Skip if it's a heading (has content)
        if line.startswith('#'):
            return False
        
        # Skip if it's a code block
        if line.startswith('```') or line.startswith('    '):
            return False
        
        # Check: is it mostly links with minimal text?
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', line))
        non_link_text = re.sub(r'\[.*?\]\(.*?\)', '', line_lower)
        non_link_length = len(non_link_text.strip())
        
        # If multiple links with almost no text: likely nav
        if link_count > 1 and non_link_length < 20:
            return True
        
        # Check: single short link with nav keywords
        if link_count == 1 and non_link_length < 50:
            # Check for nav keywords
            if any(kw in non_link_text for kw in self.nav_keywords):
                return True
        
        # Check: obvious nav keywords at line level
        if any(kw in line_lower for kw in {'skip to', 'technology areas', 'cross-product', 'sign in', 'start free', 'more\n'}):
            return True
        
        return False
    
    def _extract_main_content(self, content: str) -> str:
        """
        Extract main content by finding where actual documentation starts.
        Look for first substantial heading or content block.
        """
        lines = content.split('\n')
        content_start = 0
        
        # Find first H1 or H2 heading (likely content start)
        for i, line in enumerate(lines):
            if re.match(r'^#{1,2}\s', line):
                # Found first major heading
                content_start = i
                break
            
            # Or: find first paragraph with substantial text
            # Ignore list items, lines starting with links, or lines that are mostly links
            is_list = bool(re.match(r'^[\*\-\+]\s+', line))
            is_link = line.strip().startswith('[') or (line.count('[') > 0 and len(re.sub(r'\[.*?\]\(.*?\)', '', line).strip()) < 30)
            
            if len(line.strip()) > 50 and not is_list and not is_link:
                content_start = i
                break
        
        return '\n'.join(lines[content_start:]).strip()


class AdvancedCleaner:
    """
    Advanced content cleaner for Phase 2: sophisticated navigation/boilerplate removal
    while aggressively preserving documentation content.
    
    Strategy:
    1. Remove repeated boilerplate blocks (appear in many documents)
    2. Find main content boundary
    3. Remove sidebar navigation structures
    4. Remove header/footer boilerplate
    5. Aggressive link density filtering
    """
    
    def __init__(self):
        # Boilerplate markers
        self.boilerplate_keywords = {
            # Feedback widgets
            'send feedback', 'rate this page', 'was this helpful', 'create issue',
            # Footer boilerplate
            'except as otherwise noted', 'google developers', 'creative commons',
            'apache 2.0', 'site policies', 'terms of service', 'privacy policy',
            # Common boilerplate
            'last updated', 'last modified', 'copyright', 'all rights reserved',
        }
        
        # Navigation/sidebar keywords
        self.nav_keywords = {
            'skip to main', 'technology areas', 'cross-product', 'product category',
            'on this page', 'more information'
        }
        
        # Structure detectors
        self.main_heading_patterns = [
            r'^##\s+\w',  # H2 heading
            r'^###\s+\w',  # H3 heading
        ]
    
    def clean(self, content: str, title: str = "") -> str:
        """
        Apply aggressive Phase 2 cleaning while preserving documentation.
        
        Args:
            content: Already Phase 1 cleaned markdown
            title: Document title
        
        Returns:
            Phase 2 cleaned content
        """
        # Safety check
        if not isinstance(content, str):
            return str(content) if content else ""
        
        # Step 1: Find main content boundary
        main_start, main_end = self._find_main_content_bounds(content)
        
        # Step 2: Extract main content region
        lines = content.split('\n')
        main_lines = lines[main_start:main_end] if main_end <= len(lines) else lines[main_start:]
        
        # Step 3: Remove sidebar blocks from main content
        main_lines = self._remove_sidebar_blocks(main_lines)
        
        # Step 4: Remove boilerplate lines
        main_lines = self._remove_boilerplate_lines(main_lines)
        
        # Step 5: Aggressive nav line removal
        main_lines = self._aggressive_nav_removal(main_lines)
        
        # Step 6: Cleanup
        result = '\n'.join(main_lines)
        result = re.sub(r'\n\n\n+', '\n\n', result)
        result = result.strip()
        
        return result
    
    def _find_main_content_bounds(self, content: str) -> tuple:
        """Find where main documentation content starts and practical end."""
        lines = content.split('\n')
        main_start = 0
        main_end = len(lines)
        
        # Find main content start: first substantial documentation heading
        for i, line in enumerate(lines):
            # Look for H1, H2, or H3 heading
            if re.match(r'^#{1,3}\s+\w', line):
                main_start = i
                break
            
            # Or: first paragraph with lots of text (>100 chars)
            is_list = bool(re.match(r'^[\*\-\+]\s+', line))
            is_link = line.strip().startswith('[') or (line.count('[') > 0 and len(re.sub(r'\[.*?\]\(.*?\)', '', line).strip()) < 30)
            
            if len(line.strip()) > 100 and not is_list and not is_link:
                main_start = i
                break
        
        # Find practical end: last heading or content (not footer)
        for i in range(len(lines) - 1, -1, -1):
            line_lower = lines[i].lower().strip()
            
            # Skip footer keywords
            if any(kw in line_lower for kw in self.boilerplate_keywords):
                continue
            
            # First non-boilerplate line from end
            if len(line_lower) > 0:
                main_end = i + 1
                break
        
        return main_start, main_end
    
    def _remove_sidebar_blocks(self, lines: list) -> list:
        """
        Remove sidebar navigation blocks: nested link-only lists with consistent indentation.
        """
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line starts a sidebar block
            # Sidebar = multiple consecutive nested lists (only links, no prose)
            if self._is_sidebar_start(line):
                # Skip entire sidebar block
                i = self._skip_sidebar_block(lines, i)
            else:
                result.append(line)
                i += 1
        
        return result
    
    def _is_sidebar_start(self, line: str) -> bool:
        """Check if line starts a sidebar block."""
        line_lower = line.lower().strip()
        
        # Skip if not a list item
        if not re.match(r'^[\*\-\+]\s+', line):
            return False
            
        # Protect numbered procedures/lists (some numbered lists might have leading space or start with *)
        if re.match(r'^\s*\d+\.\s+', line) or re.match(r'^[\*\-\+]\s+\d+\.\s+', line):
            return False
        
        # Skip if has substantial text (not just link)
        text_part = re.sub(r'\[.*?\]\(.*?\)', '', line_lower)
        if len(text_part.strip()) > 40:
            return False
        
        # Check: mostly links with nav keywords
        link_count = line.count('[')
        if link_count > 0 and any(kw in line_lower for kw in self.nav_keywords):
            return True
        
        return False
    
    def _skip_sidebar_block(self, lines: list, start: int) -> int:
        """Skip past a sidebar block."""
        i = start
        indent_level = len(lines[i]) - len(lines[i].lstrip())
        
        while i < len(lines):
            line = lines[i]
            
            # End of list block (empty line or unindented non-list)
            if not line.strip():
                i += 1
                continue
            
            # If we hit a heading, stop
            if line.startswith('#'):
                break
            
            # If we hit content at same/lower indent, stop
            if line.strip() and not line.startswith((' ' * (indent_level + 1))):
                break
            
            i += 1
        
        return i
    
    def _remove_boilerplate_lines(self, lines: list) -> list:
        """Remove lines that are boilerplate (no documentation value)."""
        result = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip boilerplate keywords
            if any(kw in line_lower for kw in self.boilerplate_keywords):
                continue
            
            result.append(line)
        
        return result
    
    def _aggressive_nav_removal(self, lines: list) -> list:
        """
        Aggressively remove navigation lines using multiple heuristics.
        """
        result = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip empty
            if not line_lower:
                result.append(line)
                continue
            
            # Skip headings (always keep)
            if line.startswith('#'):
                result.append(line)
                continue
            
            # Skip code blocks
            if line.startswith('```') or line.startswith('    '):
                result.append(line)
                continue
            
            # Check if pure nav line
            if self._is_pure_nav_aggressive(line):
                continue
            
            result.append(line)
        
        return result
    
    def _is_pure_nav_aggressive(self, line: str) -> bool:
        """Aggressive check: is this a pure navigation line?"""
        if not isinstance(line, str):
            return False
        
        line_lower = line.lower().strip()
        
        # Count content
        link_count = line.count('[')
        text_part = re.sub(r'\[.*?\]\(.*?\)', '', line_lower)
        try:
            text_length = len(str(text_part).strip())
        except:
            text_length = 0
        
        # Heuristic 1: Multiple links, minimal text
        if link_count >= 2 and text_length < 20:
            return True
        
        # Heuristic 2: Single link, minimal text, nav keyword
        if link_count == 1 and text_length < 50:
            if any(kw in line_lower for kw in self.nav_keywords):
                return True
        
        # Heuristic 3: Link-only list item (- [text](url))
        if re.match(r'^[\*\-\+]\s+\[.*?\]\(.*?\)\s*$', line):
            if any(kw in line_lower for kw in self.nav_keywords):
                return True
        
        # Heuristic 4: Pure link with minimal text
        if line.startswith('[') and text_length < 10:
            return True
        
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
        
        # Keywords for quality checks
        self.nav_keywords = {
            'technology areas', 'cross-product', 'sign in', 'overview',
            'guides', 'reference', 'resources', 'start free', 'discover'
        }
        
        self.footer_keywords = {
            'send feedback', 'last updated', 'license', 'copyright'
        }
    
    def validate(self, content: str, url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate document content with critical checks only.
        Uses PRESERVE-FIRST philosophy: only reject if truly unusable.
        
        Args:
            content: Markdown content
            url: Document URL
        
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        # Only check CRITICAL items - reject only for real problems
        critical_checks = {
            'word_count_valid': False,
            'markdown_valid': False,
            'main_content_detected': False,
        }
        
        # Check word count
        word_count = len(content.split())
        critical_checks['word_count_valid'] = self.min_words <= word_count <= self.max_words
        if not critical_checks['word_count_valid']:
            reason = f"Too short/long: {word_count} words (range: {self.min_words}-{self.max_words})"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        # Check markdown validity
        critical_checks['markdown_valid'] = self._is_valid_markdown(content)
        if not critical_checks['markdown_valid']:
            reason = "Invalid markdown syntax (unbalanced brackets/fences)"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        # Check main content exists (at least has some structure)
        heading_count = sum(1 for line in content.split('\n') if line.startswith('#'))
        critical_checks['main_content_detected'] = heading_count >= 1
        if not critical_checks['main_content_detected']:
            reason = "No heading structure found (no content hierarchy)"
            self.validation_log.append({"url": url, "reason": reason})
            return False, reason
        
        # All critical checks passed
        return True, None
    
    def validate_comprehensive(self, content: str, url: str) -> dict:
        """
        Run comprehensive validation checks.
        Uses PRESERVE-FIRST philosophy: only reject if content is genuinely unusable.
        
        Returns:
            Dict of {check_name: bool}
        """
        checks = {}
        
        # Check 1: Word count (CRITICAL)
        word_count = len(content.split())
        checks['word_count_valid'] = self.min_words <= word_count <= self.max_words
        
        # Check 2: Markdown validity (CRITICAL)
        checks['markdown_valid'] = self._is_valid_markdown(content)
        
        # Check 3: Navigation removed (LENIENT - some nav OK)
        # Count lines that are pure nav links (link only, no text)
        pure_nav_lines = 0
        for line in content.split('\n'):
            line_lower = line.lower().strip()
            # Only count lines that are ONLY links with nav keywords
            if line.startswith('[') and line.count('[') > 0 and any(
                kw in line_lower for kw in {'skip to', 'technology areas', 'cross-product'}
            ):
                pure_nav_lines += 1
        
        # Allow some nav lines (up to 10) - preserve content > remove nav
        checks['navigation_removed'] = pure_nav_lines < 10
        
        # Check 4: Footer removed (LENIENT)
        footer_keyword_count = sum(
            1 for line in content.split('\n')
            if any(kw in line.lower() for kw in {'copyright', 'terms of service', 'privacy policy', 'except as otherwise noted'})
        )
        checks['footer_removed'] = footer_keyword_count == 0
        
        # Check 5: Sidebar removed - link density should be reasonable
        link_count = content.count('[')
        para_count = len([l for l in content.split('\n') if len(l.strip()) > 20])
        link_density = link_count / max(para_count, 1)
        checks['sidebar_removed'] = link_density < 0.5  # Less strict: allow up to 0.5 links per paragraph
        
        # Check 6: Main content starts early
        first_section = content[:300] if len(content) > 300 else content
        checks['main_content_detected'] = len(first_section.strip()) > 30  # More lenient
        
        # Check 7: Heading hierarchy present
        heading_count = sum(1 for line in content.split('\n') if line.startswith('#'))
        checks['heading_hierarchy_extracted'] = heading_count >= 1
        
        # Check 8: No excessive boilerplate repetition (LENIENT)
        repeated_lines = self._count_repeated_lines(content)
        checks['no_duplicate_boilerplate'] = repeated_lines < 15  # More lenient threshold
        
        return checks
    
    def _is_valid_markdown(self, content: str) -> bool:
        """Check if markdown has valid syntax."""
        # Check for balanced code fences
        code_fences = content.count('```')
        if code_fences % 2 != 0:
            return False
        
        # Check for balanced brackets
        if content.count('[') != content.count(']'):
            return False
        
        # Check for balanced parens in links
        if content.count('(') != content.count(')'):
            return False
        
        return True
    
    def _count_repeated_lines(self, content: str) -> int:
        """Count repeated lines (boilerplate indicator)."""
        lines = content.split('\n')
        line_counts = {}
        repeats = 0
        
        for line in lines:
            normalized = line.lower().strip()
            # Only count substantial lines
            if len(normalized) > 20:
                line_counts[normalized] = line_counts.get(normalized, 0) + 1
                if line_counts[normalized] > 1:
                    repeats += 1
        
        return repeats
    
    def get_report(self) -> dict:
        """Get validation report."""
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
        cleaner_type: str = "basic",  # "basic" or "advanced"
    ):
        """
        Args:
            raw_dir: Directory with raw crawled documents
            processed_dir: Directory to save processed documents
            min_words: Minimum word count for valid documents
            max_words: Maximum word count for valid documents
            cleaner_type: "basic" for ContentCleaner, "advanced" for AdvancedCleaner
        """
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize appropriate cleaner
        if cleaner_type == "advanced":
            self.cleaner = AdvancedCleaner()
        else:
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
    def save_reports(self, output_dir: str = "./processed_docs", filename: str = "processing_report.json") -> str:
        """Save processing and validation reports to JSON."""
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
