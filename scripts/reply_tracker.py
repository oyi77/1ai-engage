#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated. Use `oneai-reach track-replies` instead.

Backward compatibility shim for reply_tracker.py
"""
import sys
import warnings
from pathlib import Path

# Show deprecation warning
warnings.warn(
    "scripts/reply_tracker.py is deprecated. Use 'oneai-reach track-replies' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Add src to path for imports
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# Import and call new CLI
from oneai_reach.cli.main import cli

if __name__ == "__main__":
    sys.exit(cli())
