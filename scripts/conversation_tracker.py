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

from oneai_reach.infrastructure.database.sqlite_conversation_repository import (
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
