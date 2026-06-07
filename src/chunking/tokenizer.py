"""
Token counting abstraction using tiktoken (OpenAI tokenizer).

This module provides consistent token counting across the chunking pipeline.
"""

# pyrefly: ignore [missing-import]
import tiktoken
from typing import List
import logging

logger = logging.getLogger(__name__)


class TokenCounter:
    """
    Wrapper around tiktoken for consistent token counting.
    Uses the cl100k_base encoding (same as OpenAI's GPT models).
    """
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize token counter.
        
        Args:
            encoding_name: tiktoken encoding to use (default: OpenAI's cl100k_base)
        """
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
            self.encoding_name = encoding_name
            logger.debug(f"TokenCounter initialized with {encoding_name} encoding")
        except Exception as e:
            logger.error(f"Failed to initialize TokenCounter: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a single text string."""
        if not text:
            return 0
        
        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return 0
    
    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple text strings efficiently."""
        return [self.count_tokens(text) for text in texts]
    
    def encode(self, text: str) -> List[int]:
        """Get token IDs for text (useful for debugging)."""
        if not text:
            return []
        
        try:
            return self.encoding.encode(text)
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return []
    
    def decode(self, tokens: List[int]) -> str:
        """Decode token IDs back to text (useful for debugging)."""
        if not tokens:
            return ""
        
        try:
            return self.encoding.decode(tokens)
        except Exception as e:
            logger.error(f"Error decoding tokens: {e}")
            return ""


class TokenBudget:
    """
    Manages token budgeting for chunk creation.
    Helps enforce chunk size constraints while creating overlaps.
    """
    
    def __init__(self, chunk_size: int, overlap: int, token_counter: TokenCounter = None):
        """
        Initialize token budget.
        
        Args:
            chunk_size: Target tokens per chunk (e.g., 700)
            overlap: Tokens to overlap between chunks (e.g., 125)
            token_counter: TokenCounter instance (creates new if None)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.token_counter = token_counter or TokenCounter()
        
        # Derived values
        self.new_content_per_chunk = chunk_size - overlap
        
        logger.debug(
            f"TokenBudget: size={chunk_size}, overlap={overlap}, "
            f"new_content_per_chunk={self.new_content_per_chunk}"
        )
    
    def fits_in_chunk(self, text: str, current_tokens: int) -> bool:
        """Check if adding text would exceed chunk budget."""
        additional_tokens = self.token_counter.count_tokens(text)
        would_exceed = current_tokens + additional_tokens > self.chunk_size
        
        return not would_exceed
    
    def get_remaining_budget(self, current_tokens: int) -> int:
        """Get remaining tokens available in current chunk."""
        remaining = self.chunk_size - current_tokens
        return max(0, remaining)
    
    def should_start_new_chunk(self, current_tokens: int) -> bool:
        """Check if it's time to start a new chunk."""
        # Start new chunk if we're close to or over capacity
        return current_tokens >= self.chunk_size
    
    def get_overlap_text_tokens(self, text: str) -> int:
        """Calculate how many tokens of overlap text to keep for next chunk."""
        total_tokens = self.token_counter.count_tokens(text)
        overlap_tokens = min(self.overlap, total_tokens)
        return overlap_tokens
