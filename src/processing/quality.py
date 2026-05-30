import re
from typing import Dict, Any, List, Tuple

class Processor:
    """
    Advanced document quality enhancements:
    1. Heading hierarchy extraction
    2. Table normalization
    3. Structural metadata generation
    """
    
    def __init__(self):
        pass
        
    def process(self, content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process document content for Phase 3.
        Returns the normalized content and extracted metadata.
        """
        metrics = self._count_structural_elements(content)
        
        # 1. Normalize Tables
        normalized_content = self._normalize_tables(content)
        
        # 2. Extract Headings
        heading_paths = self._extract_heading_paths(normalized_content)
        
        # 3. Post-process metrics
        post_metrics = self._count_structural_elements(normalized_content)
        
        metadata = {
            "contains_table": post_metrics['tables'] > 0,
            "contains_code": post_metrics['code_blocks'] > 0,
            "heading_paths": heading_paths,
            "section_count": len(heading_paths),
            "structural_elements": post_metrics
        }
        
        return normalized_content, metadata
        
    def _count_structural_elements(self, content: str) -> Dict[str, int]:
        """Count headings, lists, tables, and code blocks for metrics."""
        lines = content.split('\n')
        metrics = {
            "headings": 0,
            "lists": 0,
            "tables": 0,
            "code_blocks": 0
        }
        
        in_code_block = False
        in_table = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Code blocks
            if line_stripped.startswith("```"):
                if not in_code_block:
                    metrics["code_blocks"] += 1
                in_code_block = not in_code_block
                continue
                
            if in_code_block:
                continue
                
            # Headings
            if re.match(r'^#{1,6}\s', line):
                metrics["headings"] += 1
                continue
                
            # Lists
            if re.match(r'^(\s*[\*\-\+]|\s*\d+\.)\s+', line):
                metrics["lists"] += 1
                continue
                
            # Tables (heuristic: starts and ends with |)
            if line_stripped.startswith("|") and line_stripped.endswith("|"):
                if not in_table:
                    metrics["tables"] += 1
                    in_table = True
            else:
                if line_stripped != "":
                    in_table = False
                    
        return metrics

    def _extract_heading_paths(self, content: str) -> List[List[str]]:
        """
        Extract hierarchical paths of headings.
        Returns a list of paths, where each path is a list of heading names from H1 down.
        """
        lines = content.split('\n')
        paths = []
        current_path = []
        
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
                
            if in_code_block:
                continue
                
            match = re.match(r'^(#{1,6})\s+(.*)$', line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                
                # Clean up heading text
                text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # remove link formatting
                text = text.replace('*', '').replace('`', '').strip()
                
                if not text:
                    continue
                    
                # Adjust current path based on level
                if level <= len(current_path):
                    current_path = current_path[:level-1]
                
                # If we skipped levels (e.g. H1 directly to H3), pad with empty or just append
                # It's safer to just append to current path so we might have shorter paths than level implies
                current_path.append(text)
                paths.append(list(current_path))
                
        return paths

    def _normalize_tables(self, content: str) -> str:
        """
        Fix broken markdown tables where rows might wrap incorrectly.
        This is a basic heuristic approach to merge wrapped lines back into table rows.
        """
        lines = content.split('\n')
        normalized_lines = []
        in_table = False
        
        for line in lines:
            stripped = line.strip()
            
            # Start of a table line
            if stripped.startswith("|"):
                in_table = True
                
                # If the previous line in the table didn't end with a pipe, and it wasn't empty, 
                # maybe the previous line wrapped. But typically markdown tables have a | at the end.
                if not stripped.endswith("|") and stripped.count("|") > 0:
                    # Malformed line that lacks ending pipe, just append a pipe to make it valid markdown
                    normalized_lines.append(line + " |")
                else:
                    normalized_lines.append(line)
            else:
                # If we were in a table, and we hit a non-empty line that doesn't start with |
                # It might be a wrapped line of the previous table row.
                if in_table and stripped != "" and not stripped.startswith("#") and not stripped.startswith("```"):
                    # Append it to the previous line
                    if len(normalized_lines) > 0:
                        # Add a space and the text, ensuring it stays inside the cell
                        prev_line = normalized_lines[-1]
                        if prev_line.endswith("|"):
                            # Inject text before the last pipe
                            normalized_lines[-1] = prev_line[:-1].rstrip() + " " + stripped + " |"
                        else:
                            normalized_lines[-1] = prev_line + " " + stripped
                else:
                    in_table = False
                    normalized_lines.append(line)
                    
        return '\n'.join(normalized_lines)
