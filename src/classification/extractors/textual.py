import re
from typing import Dict
from ..blocks import ContentBlock

class TextualSignalExtractor:
    """Extracts text-based signals like link density, word count, code presence."""
    
    def extract(self, block: ContentBlock) -> None:
        text = block.text.strip()
        
        # Word count (normalized for score: e.g. 0 to 1 where 1 is 100+ words)
        words = text.split()
        word_count = len(words)
        block.signals['word_count'] = min(word_count / 100.0, 1.0)
        
        # Link density
        # Approximating link density in Markdown: `[text](url)`
        link_matches = re.findall(r'\[(.*?)\]\((.*?)\)', text)
        link_count = len(link_matches)
        
        if word_count > 0:
            # Ratio of linked words to total words (approximation)
            linked_words = sum(len(match[0].split()) for match in link_matches)
            block.signals['link_density'] = min(linked_words / word_count, 1.0)
        else:
            block.signals['link_density'] = 1.0 if link_count > 0 else 0.0
            
        block.signals['link_count_raw'] = float(link_count)
        
        # Information density (words per line)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            avg_words_per_line = word_count / len(lines)
            block.signals['info_density'] = min(avg_words_per_line / 15.0, 1.0) # 15 words per line is dense prose
        else:
            block.signals['info_density'] = 0.0
            
        # Structure presences
        block.signals['has_code'] = 1.0 if '```' in text or '`' in text else 0.0
        block.signals['has_table'] = 1.0 if '|' in text and '\n|' in text else 0.0
        block.signals['has_list'] = 1.0 if re.search(r'^[\*\-\+]\s+', text, re.MULTILINE) else 0.0
