import os
from pathlib import Path
import re

def get_latest_version(base_dir: str | Path) -> str:
    """Finds the latest version directory (v1, v2, etc) in base_dir."""
    base_dir = Path(base_dir)
    if not base_dir.exists():
        return "v0"
        
    versions = []
    for d in base_dir.iterdir():
        if d.is_dir() and re.match(r'^v\d+$', d.name):
            versions.append(int(d.name[1:]))
            
    if not versions:
        return "v0"
        
    return f"v{max(versions)}"

def get_next_version(base_dir: str | Path) -> str:
    """Returns the next version string (v1, v2, etc)."""
    latest = get_latest_version(base_dir)
    num = int(latest[1:])
    return f"v{num + 1}"
