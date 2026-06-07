from ..blocks import ContentBlock

class StructuralSignalExtractor:
    """Extracts signals based on structural position (e.g., if we know its depth or tag)."""
    
    def extract(self, block: ContentBlock) -> None:
        # In this iteration, we don't have full DOM tree parsed out across the whole doc easily,
        # but we can look for heading levels in Markdown as a proxy.
        text = block.text.strip()
        
        # Is it a heading?
        if text.startswith('#'):
            block.signals['is_heading'] = 1.0
        else:
            block.signals['is_heading'] = 0.0
            
        # If original HTML is provided, we can look for structural tags
        if block.original_html:
            html = block.original_html.lower()
            if '<nav' in html or 'class="nav"' in html or 'class="sidebar"' in html:
                block.signals['html_nav_hint'] = 1.0
            if '<footer' in html or 'class="footer"' in html:
                block.signals['html_footer_hint'] = 1.0
            if '<aside' in html:
                block.signals['html_aside_hint'] = 1.0
