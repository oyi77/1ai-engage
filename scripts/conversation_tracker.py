#!/usr/bin/env python3
"""
Backward compatibility shim for conversation_tracker.py
Maps old function names to new Clean Architecture implementation.
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from oneai_reach.infrastructure.database.sqlite_conversation_repository import (  # noqa: E402
    SQLiteConversationRepository,
)

_db_path = _root / "data" / "leads.db"
_repo = SQLiteConversationRepository(str(_db_path))


def get_active_conversations() -> List[Dict[str, Any]]:
    conversations = _repo.get_all()
    
    result = []
    for conv in conversations:
        if conv.status != "resolved":
            result.append({
                "id": conv.id,
                "wa_number_id": conv.wa_number_id or "unknown",
                "contact_phone": conv.contact_phone or "",
                "message_count": len(conv.messages) if hasattr(conv, 'messages') else 0,
                "last_message_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "status": conv.status,
                "engine_mode": conv.engine_mode or "cs",
            })
    
    return result


def update_status(conversation_id: int, status: str) -> bool:
    try:
        conv = _repo.get_by_id(conversation_id)
        if not conv:
            return False
        
        conv.status = status
        _repo.update(conv)
        return True
    except Exception:
        return False


def _connect():
    import sqlite3
    import config

    conn = sqlite3.connect(str(config.DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def get_or_create_conversation(
    wa_number_id: str,
    contact_phone: str,
    engine_mode: str = "cs",
    contact_name: str = "",
    lead_id: str | None = None,
) -> dict:
    conn = _connect()
    try:
        row = conn.execute(
            """SELECT * FROM conversations
                WHERE wa_number_id = ? AND contact_phone = ? AND status = 'active'""",
            (wa_number_id, contact_phone),
        ).fetchone()
        if row:
            return dict(row)

        columns = {row[1] for row in conn.execute("PRAGMA table_info(conversations)")}
        if "stage" in columns:
            cursor = conn.execute(
                """INSERT INTO conversations
                    (wa_number_id, contact_phone, engine_mode, stage, status, message_count)
                    VALUES (?, ?, ?, 'awareness', 'active', 0)""",
                (wa_number_id, contact_phone, engine_mode),
            )
        else:
            cursor = conn.execute(
                """INSERT INTO conversations
                    (wa_number_id, contact_phone, contact_name, lead_id, engine_mode, status, message_count)
                    VALUES (?, ?, ?, ?, ?, 'active', 0)""",
                (wa_number_id, contact_phone, contact_name, lead_id, engine_mode),
            )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM conversations WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


def add_message(conversation_id: int, direction: str, message_text: str) -> int:
    conn = _connect()
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "messages" in tables:
            cursor = conn.execute(
                """INSERT INTO messages
                    (conversation_id, direction, message_text, created_at)
                    VALUES (?, ?, ?, datetime('now'))""",
                (conversation_id, direction, message_text),
            )
        else:
            cursor = conn.execute(
                """INSERT INTO conversation_messages
                    (conversation_id, direction, message_text, timestamp)
                    VALUES (?, ?, ?, datetime('now'))""",
                (conversation_id, direction, message_text),
            )
        conn.execute(
            """UPDATE conversations
                SET message_count = COALESCE(message_count, 0) + 1,
                    updated_at = datetime('now')
                WHERE id = ?""",
            (conversation_id,),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
