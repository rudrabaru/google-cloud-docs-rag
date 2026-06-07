from dataclasses import dataclass, field
from typing import Dict, Optional, Any

@dataclass
class ContentBlock:
    """Represents a discrete block of text (e.g. paragraph, list, table) with classification signals."""
    block_id: str
    text: str
    original_html: Optional[str] = None
    signals: Dict[str, float] = field(default_factory=dict)
    
    # Metadata for observability
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Final decisions
    decision: Optional[str] = None # 'KEEP' or 'REMOVE'
    classification: Optional[str] = None # 'main_content', 'navigation', 'boilerplate', etc.
    confidence: float = 0.0
