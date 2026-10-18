"""Pytest bootstrap: ensure src/ and app/ are on sys.path before any test imports."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for sub in ("src", "app"):
    p = ROOT / sub
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))