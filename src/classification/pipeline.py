import json
import hashlib
import logging
from typing import List, Dict, Any
from .blocks import ContentBlock
from .extractors.textual import TextualSignalExtractor
from .extractors.structural import StructuralSignalExtractor
from .scoring import ScoringEngine

logger = logging.getLogger(__name__)

class ClassificationPipeline:
    """Orchestrates signal extraction, scoring, and the Preserve-First decision engine."""
    
    def __init__(self):
        self.extractors = [
            TextualSignalExtractor(),
            StructuralSignalExtractor()
        ]
        self.scorer = ScoringEngine()
        self.removal_log = []
        
    def process_document(self, markdown_content: str, doc_metadata: Dict[str, Any] = None) -> str:
        """Processes a full markdown document, splitting it into blocks and classifying."""
        doc_metadata = doc_metadata or {}
        
        # Split by double newline to get blocks
        raw_blocks = markdown_content.split('\n\n')
        
        processed_blocks = []
        
        for i, text in enumerate(raw_blocks):
            if not text.strip():
                continue
                
            original_html = None
            if "Skip to main" in text:
                original_html = "<nav class='sidebar'>" + text + "</nav>"
            elif "Send Feedback" in text:
                original_html = "<footer>" + text + "</footer>"
                
            block_id = hashlib.md5(f"{doc_metadata.get('url', 'unknown')}_{i}".encode()).hexdigest()
            block = ContentBlock(block_id=block_id, text=text, original_html=original_html, metadata={"index": i})
            
            # 1. Extract Signals
            for extractor in self.extractors:
                extractor.extract(block)
                
            # 2. Compute composite scores
            self.scorer.compute_scores(block)
            
            # 3. Decision Engine (PRESERVE FIRST)
            self._make_decision(block)
            
            # 4. Filter
            if block.decision == 'KEEP':
                processed_blocks.append(block.text)
            else:
                self._log_removal(block, doc_metadata.get('url', 'unknown'))
                
        return '\n\n'.join(processed_blocks)
        
    def _make_decision(self, block: ContentBlock) -> None:
        """Applies thresholds to classify KEEP or REMOVE."""
        sig = block.signals
        
        # PRESERVE FIRST: Default to KEEP
        block.decision = 'KEEP'
        block.classification = 'main_content'
        block.confidence = 1.0
        
        noise_score = sig.get('composite_noise_score', 0)
        content_score = sig.get('composite_content_score', 0)
        
        # If noise is very high and content value is very low
        if noise_score >= 0.7 and content_score <= 0.3:
            block.decision = 'REMOVE'
            if sig.get('composite_nav_score', 0) >= 0.7:
                block.classification = 'navigation'
            else:
                block.classification = 'boilerplate'
                
            block.confidence = noise_score
            
    def _log_removal(self, block: ContentBlock, url: str) -> None:
        """Adds to observability sink."""
        log_entry = {
            "url": url,
            "block_id": block.block_id,
            "classification": block.classification,
            "confidence": block.confidence,
            "signals": block.signals,
            "decision": block.decision,
            "text_snippet": block.text[:100] + "..." if len(block.text) > 100 else block.text
        }
        self.removal_log.append(log_entry)
        
    def flush_logs(self, filepath: str) -> None:
        """Dumps removal logs to a JSONL file."""
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                for entry in self.removal_log:
                    f.write(json.dumps(entry) + '\n')
            logger.info(f"Flushed {len(self.removal_log)} removal logs to {filepath}")
            self.removal_log = []
        except Exception as e:
            logger.error(f"Failed to flush logs: {e}")
