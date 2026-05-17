from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """Return a path that works in source runs and PyInstaller bundles."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base_path / relative_path
