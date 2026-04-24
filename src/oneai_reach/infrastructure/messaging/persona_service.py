"""DB-backed CRUD for personas and channel-persona assignments."""

import json
import sqlite3
from datetime import datetime
from typing import Any, Optional

from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)


class PersonaService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        data = dict(row)
        if "example_replies" in data and isinstance(data["example_replies"], str):
            try:
                data["example_replies"] = json.loads(data["example_replies"])
            except (json.JSONDecodeError, TypeError):
                data["example_replies"] = []
        return data

    # ── Persona CRUD ───────────────────────────────────────────────

    def list_personas(self, scope: Optional[str] = None) -> list[dict]:
        conn = self._connect()
        try:
            if scope:
                rows = conn.execute(
                    "SELECT * FROM personas WHERE scope = ? OR scope = 'universal' ORDER BY name",
                    (scope,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM personas ORDER BY name").fetchall()
            return [self._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    def get_persona(self, persona_id: str) -> Optional[dict]:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM personas WHERE id = ?", (persona_id,)).fetchone()
            return self._row_to_dict(row) if row else None
        finally:
            conn.close()

    def create_persona(
        self,
        id: str,
        name: str,
        scope: str,
        system_prompt: str,
        tone: str = "casual",
        language: str = "id",
        example_replies: Optional[list[str]] = None,
    ) -> dict:
        now = datetime.now().isoformat()
        replies_json = json.dumps(example_replies or [])
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """INSERT INTO personas (id, name, scope, system_prompt, tone, language, example_replies, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (id, name, scope, system_prompt, tone, language, replies_json, now, now),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM personas WHERE id = ?", (id,)).fetchone()
            return self._row_to_dict(row)
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_persona(self, persona_id: str, **kwargs) -> Optional[dict]:
        allowed = {"name", "scope", "system_prompt", "tone", "language", "example_replies"}
        updates = {}
        for key, value in kwargs.items():
            if key in allowed:
                if key == "example_replies" and isinstance(value, list):
                    value = json.dumps(value)
                updates[key] = value

        if not updates:
            return self.get_persona(persona_id)

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [persona_id]

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(f"UPDATE personas SET {set_clause} WHERE id = ?", values)
            conn.commit()
            row = conn.execute("SELECT * FROM personas WHERE id = ?", (persona_id,)).fetchone()
            return self._row_to_dict(row) if row else None
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_persona(self, persona_id: str) -> bool:
        p = self.get_persona(persona_id)
        if p and p.get("is_builtin"):
            raise ValueError("Cannot delete built-in personas")

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Assignment CRUD ────────────────────────────────────────────

    def assign_persona(self, channel_id: str, mode: str, persona_id: str) -> dict:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """INSERT INTO channel_persona_assignments (channel_id, mode, persona_id)
                   VALUES (?, ?, ?)
                   ON CONFLICT(channel_id, mode) DO UPDATE SET persona_id = excluded.persona_id""",
                (channel_id, mode, persona_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM channel_persona_assignments WHERE channel_id = ? AND mode = ?",
                (channel_id, mode),
            ).fetchone()
            return dict(row) if row else {}
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def unassign_persona(self, channel_id: str, mode: str) -> bool:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute(
                "DELETE FROM channel_persona_assignments WHERE channel_id = ? AND mode = ?",
                (channel_id, mode),
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def list_assignments(self, channel_id: Optional[str] = None) -> list[dict]:
        conn = self._connect()
        try:
            if channel_id:
                rows = conn.execute(
                    """SELECT cpa.*, p.name as persona_name
                       FROM channel_persona_assignments cpa
                       JOIN personas p ON p.id = cpa.persona_id
                       WHERE cpa.channel_id = ?""",
                    (channel_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT cpa.*, p.name as persona_name
                       FROM channel_persona_assignments cpa
                       JOIN personas p ON p.id = cpa.persona_id"""
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── Resolution ─────────────────────────────────────────────────

    def get_persona_for_channel(self, channel_id: str, mode: str) -> Optional[dict]:
        conn = self._connect()
        try:
            # 1. Direct assignment
            row = conn.execute(
                """SELECT p.* FROM channel_persona_assignments cpa
                   JOIN personas p ON p.id = cpa.persona_id
                   WHERE cpa.channel_id = ? AND cpa.mode = ?""",
                (channel_id, mode),
            ).fetchone()
            if row:
                result = self._row_to_dict(row)
                result["_source"] = "assignment"
                return result

            # 2. Workspace default
            ch = conn.execute("SELECT workspace_id FROM channels WHERE id = ?", (channel_id,)).fetchone()
            if ch:
                ws = conn.execute(
                    "SELECT default_persona_id FROM workspaces WHERE id = ?", (ch["workspace_id"],)
                ).fetchone()
                if ws and ws["default_persona_id"]:
                    persona = conn.execute(
                        "SELECT * FROM personas WHERE id = ?", (ws["default_persona_id"],)
                    ).fetchone()
                    if persona:
                        result = self._row_to_dict(persona)
                        result["_source"] = "workspace_default"
                        return result

            # 3. System default
            default = conn.execute("SELECT * FROM personas WHERE id = 'general-assistant'").fetchone()
            if default:
                result = self._row_to_dict(default)
                result["_source"] = "system_default"
                return result

            return None
        finally:
            conn.close()

    def resolve_persona(self, channel_id: str, mode: str) -> str:
        persona = self.get_persona_for_channel(channel_id, mode)
        if persona:
            return persona.get("system_prompt", "")
        return "You are a helpful assistant."
