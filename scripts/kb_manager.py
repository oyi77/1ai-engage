#!/usr/bin/env python3
"""
Backward compatibility shim for kb_manager.py
Maps old function names to new Clean Architecture implementation.
"""
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from oneai_reach.infrastructure.database.sqlite_knowledge_repository import (
    SQLiteKnowledgeRepository,
)
from oneai_reach.domain.models.knowledge import KnowledgeEntry, KnowledgeCategory

# Initialize repository
_db_path = _root / "data" / "1ai_reach.db"
_repo = SQLiteKnowledgeRepository(str(_db_path))


def add_entry(
    wa_number_id: str,
    category: str,
    question: str,
    answer: str,
    content: str = "",
    tags: str = "",
    priority: int = 0,
) -> int:
    """Add a new knowledge base entry."""
    entry = KnowledgeEntry(
        wa_number_id=wa_number_id,
        category=KnowledgeCategory(category) if category else None,
        question=question,
        answer=answer,
        content=content,
        tags=tags,
        priority=priority,
    )
    saved = _repo.add(entry)
    return saved.id


def update_entry(
    entry_id: int,
    category: Optional[str] = None,
    question: Optional[str] = None,
    answer: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[str] = None,
    priority: Optional[int] = None,
) -> bool:
    """Update an existing knowledge base entry."""
    entry = _repo.get_by_id(entry_id)
    if not entry:
        return False

    if category is not None:
        entry.category = KnowledgeCategory(category) if category else None
    if question is not None:
        entry.question = question
    if answer is not None:
        entry.answer = answer
    if content is not None:
        entry.content = content
    if tags is not None:
        entry.tags = tags
    if priority is not None:
        entry.priority = priority

    _repo.update(entry)
    return True


def get_kb_entries(wa_number_id: str) -> List[dict]:
    """Get all knowledge base entries for a WA number."""
    entries = _repo.get_all(wa_number_id)
    return [
        {
            "id": e.id,
            "wa_number_id": e.wa_number_id,
            "category": e.category.value if e.category else None,
            "question": e.question,
            "answer": e.answer,
            "content": e.content,
            "tags": e.tags,
            "priority": e.priority,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "updated_at": e.updated_at.isoformat() if e.updated_at else None,
        }
        for e in entries
    ]


def search(wa_number_id: str, query: str, limit: int = 5) -> List[dict]:
    """Search knowledge base entries."""
    entries = _repo.search(wa_number_id, query, limit)
    return [
        {
            "id": e.id,
            "wa_number_id": e.wa_number_id,
            "category": e.category.value if e.category else None,
            "question": e.question,
            "answer": e.answer,
            "content": e.content,
            "tags": e.tags,
            "priority": e.priority,
            "score": getattr(e, "score", 0.0),
        }
        for e in entries
    ]


def delete_entry(entry_id: int) -> bool:
    """Delete a knowledge base entry."""
    return _repo.delete(entry_id)


def import_entries(wa_number_id: str, entries: List[dict]) -> int:
    """Import knowledge base entries from list of dicts."""
    return _repo.import_entries(wa_number_id, entries)


def export_entries(wa_number_id: str) -> List[dict]:
    """Export knowledge base entries to list of dicts."""
    return _repo.export_entries(wa_number_id)
