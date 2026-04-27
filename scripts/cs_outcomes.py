#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated. Use `oneai-reach cs-outcomes` instead.

Backward compatibility shim for cs_outcomes.py
"""
import sys
import warnings
from importlib import import_module
from pathlib import Path

# Show deprecation warning
warnings.warn(
    "scripts/cs_outcomes.py is deprecated. Use 'oneai-reach cs-outcomes' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Add src to path for imports
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

def init_outcomes_db() -> None:
    from config import DB_FILE

    import sqlite3

    conn = sqlite3.connect(str(DB_FILE))
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS conversation_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER UNIQUE NOT NULL,
                wa_number_id TEXT,
                contact_phone TEXT,
                final_status TEXT DEFAULT 'engaged',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                total_messages INTEGER DEFAULT 0,
                total_value REAL DEFAULT 0,
                escalation_reason TEXT,
                converted_to_purchase INTEGER DEFAULT 0,
                duration_seconds INTEGER,
                outcome_value REAL DEFAULT 0
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS response_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                wa_number_id TEXT,
                response_hash TEXT NOT NULL,
                response_text TEXT NOT NULL,
                kb_entry_ids TEXT DEFAULT '[]',
                pattern_used TEXT,
                user_type TEXT DEFAULT 'normal',
                sales_stage TEXT DEFAULT 'ENTRY',
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_replied INTEGER DEFAULT 0,
                reply_text TEXT,
                reply_sentiment TEXT,
                time_to_reply_seconds INTEGER,
                was_effective INTEGER DEFAULT 0,
                outcome_score REAL DEFAULT 0,
                next_user_action TEXT,
                reply_time_seconds INTEGER
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS user_journey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                wa_number_id TEXT,
                step_name TEXT NOT NULL,
                step_order INTEGER NOT NULL,
                reached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS learning_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                winning_responses TEXT NOT NULL,
                scenario_type TEXT DEFAULT 'general',
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS pattern_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                pattern_text TEXT NOT NULL,
                scenario TEXT NOT NULL,
                times_used INTEGER DEFAULT 0,
                times_successful INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0,
                last_used TIMESTAMP,
                UNIQUE(pattern_id, scenario)
            )"""
        )
        conn.commit()
    finally:
        conn.close()


def _outcomes_service():
    from config import DB_FILE
    import sqlite3
    from oneai_reach.config.settings import get_settings
    from oneai_reach.application.customer_service.outcomes_service import OutcomesService

    def connect():
        conn = sqlite3.connect(str(DB_FILE))
        conn.row_factory = sqlite3.Row
        return conn

    init_outcomes_db()
    return OutcomesService(get_settings(), connect)


def record_conversation_start(conversation_id: int, wa_number_id: str, contact_phone: str) -> None:
    _outcomes_service().record_conversation_start(conversation_id, wa_number_id, contact_phone)


def record_response_sent(
    conversation_id: int,
    response_text: str,
    kb_entry_ids: list[int] = None,
    pattern_used: str = None,
    user_type: str = "normal",
    sales_stage: str = "ENTRY",
    wa_number_id: str = None,
) -> int:
    return _outcomes_service().record_response_sent(
        conversation_id,
        response_text,
        kb_entry_ids=kb_entry_ids,
        pattern_used=pattern_used,
        user_type=user_type,
        sales_stage=sales_stage,
        wa_number_id=wa_number_id,
    )


def record_user_reply(
    conversation_id: int,
    response_text: str,
    user_reply: str,
    time_to_reply_seconds: int = None,
) -> None:
    _outcomes_service().record_user_reply(
        conversation_id,
        response_text,
        user_reply,
        time_to_reply_seconds=time_to_reply_seconds,
    )


def record_final_outcome(conversation_id: int, status: str, total_value: float = 0) -> None:
    _outcomes_service().record_final_outcome(
        conversation_id,
        status,
        total_value=total_value,
    )


def get_conversation_metrics(conversation_id: int) -> dict:
    return _outcomes_service().get_conversation_metrics(conversation_id)

if __name__ == "__main__":
    cli = import_module("oneai_reach.cli.main").cli
    sys.exit(cli())
