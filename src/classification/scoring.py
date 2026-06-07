from .blocks import ContentBlock

class ScoringEngine:
    """Combines extracted signals into high-level composite scores."""
    
    def compute_scores(self, block: ContentBlock) -> None:
        # Defaults
        nav_score = 0.0
        content_score = 0.0
        boilerplate_score = 0.0
        
        sig = block.signals
        
        # Content Score: unique content, has lists, code, tables, explanations
        if sig.get('has_code', 0) > 0 or sig.get('has_table', 0) > 0:
            content_score += 0.5
            
        content_score += sig.get('info_density', 0) * 0.5
        content_score += sig.get('word_count', 0) * 0.3
        
        if sig.get('is_heading', 0) > 0:
            content_score += 0.4
            
        # Cap at 1.0
        block.signals['composite_content_score'] = min(content_score, 1.0)
        
        # Navigation Score: high link density, low info density, html hints
        if sig.get('link_density', 0) > 0.5 and sig.get('info_density', 0) < 0.3:
            nav_score += 0.6
            
        if sig.get('link_count_raw', 0) > 3 and sig.get('word_count', 0) < 0.1: # very few words
            nav_score += 0.4
            
        if sig.get('html_nav_hint', 0) > 0 or sig.get('html_aside_hint', 0) > 0:
            nav_score += 0.8
            
        block.signals['composite_nav_score'] = min(nav_score, 1.0)
        
        # Boilerplate/Footer Score
        if sig.get('html_footer_hint', 0) > 0:
            boilerplate_score += 0.9
            
        block.signals['composite_noise_score'] = min(max(nav_score, boilerplate_score), 1.0)
