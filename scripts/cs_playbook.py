#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated. Use `oneai-reach cs-playbook` instead.

Backward compatibility shim for cs_playbook.py
"""
import sys
import warnings
from importlib import import_module
from pathlib import Path

# Show deprecation warning
warnings.warn(
    "scripts/cs_playbook.py is deprecated. Use 'oneai-reach cs-playbook' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Add src to path for imports
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

CSPlaybook = import_module(
    "oneai_reach.application.customer_service.playbook_service"
).PlaybookService

if __name__ == "__main__":
    cli = import_module("oneai_reach.cli.main").cli
    sys.exit(cli())
