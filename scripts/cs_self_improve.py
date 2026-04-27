#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated. Use `oneai-reach cs-self-improve` instead.

Backward compatibility shim for cs_self_improve.py
"""
import sys
import warnings
from importlib import import_module
from pathlib import Path

# Show deprecation warning
warnings.warn(
    "scripts/cs_self_improve.py is deprecated. Use 'oneai-reach cs-self-improve' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Add src to path for imports
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

def _connect():
    from config import DB_FILE
    import sqlite3

    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


class SelfImprovementEngine:
    def __init__(self, wa_number_id: str = "default"):
        from oneai_reach.config.settings import get_settings
        from oneai_reach.application.customer_service.self_improve_service import SelfImproveService

        self.wa_number_id = wa_number_id
        self._service = SelfImproveService(
            get_settings(),
            _connect,
            analytics_service=None,
            outcomes_service=import_module("cs_outcomes")._outcomes_service(),
        )

    def analyze_conversation(self, conversation_id: int) -> dict:
        return self._service.analyze_conversation(conversation_id)

    def extract_winning_patterns(self, days: int = 7, min_score: float = 0.7) -> list[dict]:
        return self._service.extract_winning_patterns(days=days, min_score=min_score)

    def _get_admin_feedback_summary(self) -> dict:
        return self._service._get_admin_feedback_summary()

    def apply_learnings(self, dry_run: bool = True) -> dict:
        return self._service.apply_learnings(dry_run=dry_run)

if __name__ == "__main__":
    cli = import_module("oneai_reach.cli.main").cli
    sys.exit(cli())
