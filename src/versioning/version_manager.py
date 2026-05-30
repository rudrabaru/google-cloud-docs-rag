"""
Version manager for processed documents pipeline.

Handles versioning of processed_docs across iterations:
- v1: Phase 1 cleaning (footer removal, language selectors)
- v2: Phase 2 cleaning (main content detection, sidebar removal)
- v3+: Future phases
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VersionManager:
    """Manages versioned directories for processed documents."""
    
    def __init__(self, base_dir: str = "processed_docs"):
        """
        Initialize version manager.
        
        Args:
            base_dir: Base directory for all versions (default: processed_docs)
        """
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest version directory name (e.g., 'v1', 'v2').
        
        Returns:
            Version name or None if no versions exist
        """
        versions = sorted([d.name for d in self.base_path.glob("v*") if d.is_dir()])
        return versions[-1] if versions else None
    
    def get_next_version(self) -> str:
        """
        Get next version name.
        
        Returns:
            Next version (e.g., 'v1' if no versions, 'v2' if v1 exists)
        """
        latest = self.get_latest_version()
        
        if latest is None:
            return "v1"
        
        # Extract number and increment
        version_num = int(latest[1:])  # Remove 'v', convert to int
        return f"v{version_num + 1}"
    
    def create_version(
        self,
        phase: str,
        enhancements: list,
        metrics: Dict
    ) -> Path:
        """
        Create new version directory with manifest.
        
        Args:
            phase: Phase name (e.g., "Phase 1", "Phase 2")
            enhancements: List of improvements in this version
            metrics: Dict of processing metrics
        
        Returns:
            Path to new version directory
        """
        version = self.get_next_version()
        version_path = self.base_path / version
        version_path.mkdir(exist_ok=True)
        
        # Create documents subdirectory
        docs_dir = version_path / "documents"
        docs_dir.mkdir(exist_ok=True)
        
        # Create version manifest
        manifest = {
            "version": version,
            "phase": phase,
            "created": datetime.utcnow().isoformat(),
            "enhancements": enhancements,
            "metrics": metrics
        }
        
        manifest_file = version_path / "version_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Created version directory: {version_path}")
        logger.info(f"Manifest saved: {manifest_file}")
        
        return version_path
    
    def get_version_path(self, version: Optional[str] = None) -> Path:
        """
        Get path to version directory.
        
        Args:
            version: Version name (e.g., 'v1'). If None, returns latest.
        
        Returns:
            Path to version directory
        """
        if version is None:
            version = self.get_latest_version()
            if version is None:
                raise ValueError("No versions found in processed_docs/")
        
        version_path = self.base_path / version
        
        if not version_path.exists():
            raise FileNotFoundError(f"Version not found: {version_path}")
        
        return version_path
    
    def get_documents_dir(self, version: Optional[str] = None) -> Path:
        """
        Get path to documents subdirectory for a version.
        
        Args:
            version: Version name. If None, returns latest.
        
        Returns:
            Path to documents directory
        """
        version_path = self.get_version_path(version)
        docs_dir = version_path / "documents"
        
        if not docs_dir.exists():
            docs_dir.mkdir(exist_ok=True)
        
        return docs_dir
    
    def list_versions(self) -> list:
        """
        List all versions with their metadata.
        
        Returns:
            List of dicts with version info
        """
        versions = []
        
        for version_dir in sorted(self.base_path.glob("v*")):
            if not version_dir.is_dir():
                continue
            
            manifest_file = version_dir / "version_manifest.json"
            
            if manifest_file.exists():
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # Count documents
                docs_dir = version_dir / "documents"
                doc_count = len(list(docs_dir.glob("*.md"))) if docs_dir.exists() else 0
                
                versions.append({
                    "version": manifest.get("version"),
                    "phase": manifest.get("phase"),
                    "created": manifest.get("created"),
                    "enhancements": manifest.get("enhancements", []),
                    "documents": doc_count,
                    "metrics": manifest.get("metrics", {})
                })
        
        return versions
    
    def export_version_history(self) -> str:
        """
        Generate markdown version history.
        
        Returns:
            Markdown version history string
        """
        versions = self.list_versions()
        if not versions:
            return "# Document Quality Versions\n\nNo versions yet.\n"
        
        lines = ["# Document Quality Versions\n"]
        for v in versions:
            date_str = v["created"].split("T")[0] if v.get("created") else "unknown"
            lines.extend([
                f"## {v.get('version', 'unknown')} ({date_str})",
                f"**Phase:** {v.get('phase', 'unknown')}\n",
                "**Enhancements:**"
            ])
            lines.extend(f"- ✅ {e}" for e in v.get("enhancements", []))
            lines.extend([
                "\n**Metrics:**",
                f"- Documents: {v.get('documents', 0)}"
            ])
            lines.extend(f"- {k}: {val}" for k, val in v.get("metrics", {}).items())
            lines.append("\n---\n")
        
        return "\n".join(lines)
    
    def save_version_history(self, filepath: Optional[str] = None) -> Path:
        """
        Save version history to markdown file.
        
        Args:
            filepath: Output file path. If None, saves to VERSION_HISTORY.md
        
        Returns:
            Path to saved file
        """
        if filepath is None:
            filepath = self.base_path / "VERSION_HISTORY.md"
        else:
            filepath = Path(filepath)
        
        history = self.export_version_history()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(history)
        
        logger.info(f"Version history saved: {filepath}")
        
        return filepath
