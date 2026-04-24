"""Channels V2 migration — adds workspaces and channels tables.

Decouples channels from WhatsApp numbers. Each WA number gets migrated
into a workspace with a whatsapp channel. Idempotent — safe to run multiple times.
"""

import json
import re
import sqlite3
from datetime import datetime

from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)


def _slugify(text: str) -> str:
    """Convert label to URL-safe slug for workspace IDs."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "workspace"


def run_migration(db_path: str) -> None:
    """Run V2 migration. Creates tables and backfills from wa_numbers.

    Args:
        db_path: Path to SQLite database file (e.g. 'data/leads.db')
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        _create_tables(conn)
        _add_columns(conn)
        _backfill(conn)
        conn.commit()
        logger.info("V2 migration complete")
    except Exception as e:
        conn.rollback()
        logger.error(f"V2 migration failed: {e}")
        raise
    finally:
        conn.close()


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create workspaces and channels tables if they don't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workspaces (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            label TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'cs',
            enabled INTEGER DEFAULT 1,
            connected INTEGER DEFAULT 0,
            username TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            config TEXT DEFAULT '{}',
            session_data TEXT DEFAULT '{}',
            last_check TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_channels_workspace ON channels(workspace_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_channels_platform ON channels(platform)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_channels_mode ON channels(mode)")
    conn.commit()
    logger.info("V2 tables created/verified")


def _add_columns(conn: sqlite3.Connection) -> None:
    """Add workspace_id and channel_id columns to existing tables (idempotent)."""
    alter_statements = [
        ("wa_numbers", "workspace_id", "TEXT"),
        ("wa_numbers", "channel_id", "TEXT"),
        ("conversations", "workspace_id", "TEXT"),
        ("conversations", "channel_id", "TEXT"),
        ("knowledge_base", "workspace_id", "TEXT"),
        ("products", "workspace_id", "TEXT"),
        ("sales_stages", "workspace_id", "TEXT"),
        ("conversation_messages", "channel_id", "TEXT"),
    ]
    for table, column, col_type in alter_statements:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()


def _backfill(conn: sqlite3.Connection) -> None:
    """Backfill workspaces/channels from existing wa_numbers rows."""
    # Check if backfill already done
    cur = conn.execute("SELECT COUNT(*) as cnt FROM workspaces")
    if cur.fetchone()["cnt"] > 0:
        return  # Already backfilled

    rows = conn.execute("SELECT * FROM wa_numbers").fetchall()
    if not rows:
        # Create a default workspace if no wa_numbers
        _create_default_workspace(conn)
        return

    for row in rows:
        data = dict(row)
        wa_id = data["id"]
        label = data.get("label", wa_id)
        mode = data.get("mode", "cs")
        phone = data.get("phone", "")
        session_name = data.get("session_name", "")

        # Create workspace
        ws_id = _slugify(label)
        # Ensure unique workspace ID
        existing = conn.execute("SELECT id FROM workspaces WHERE id = ?", (ws_id,)).fetchone()
        if existing:
            ws_id = f"{ws_id}-{wa_id}"

        conn.execute(
            "INSERT OR IGNORE INTO workspaces (id, name, description) VALUES (?, ?, ?)",
            (ws_id, label, f"Migrated from WA number {wa_id}"),
        )

        # Create whatsapp channel
        ch_id = f"ch-{wa_id}-whatsapp"
        config = json.dumps({
            "session_name": session_name,
            "phone": phone,
            "wa_number_id": wa_id,
        })

        conn.execute(
            """INSERT OR IGNORE INTO channels
               (id, workspace_id, platform, label, mode, enabled, connected, phone, config)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ch_id, ws_id, "whatsapp", f"WhatsApp - {label}", mode, 1, 1, phone, config),
        )

        # Backfill workspace_id on related tables
        conn.execute("UPDATE wa_numbers SET workspace_id = ?, channel_id = ? WHERE id = ?",
                     (ws_id, ch_id, wa_id))
        conn.execute("UPDATE conversations SET workspace_id = ?, channel_id = ? WHERE wa_number_id = ?",
                     (ws_id, ch_id, wa_id))
        conn.execute("UPDATE knowledge_base SET workspace_id = ? WHERE wa_number_id = ?",
                     (ws_id, wa_id))
        conn.execute("UPDATE products SET workspace_id = ? WHERE wa_number_id = ?",
                     (ws_id, wa_id))
        conn.execute("UPDATE sales_stages SET workspace_id = ? WHERE wa_number_id = ?",
                     (ws_id, wa_id))
        conn.execute("UPDATE conversation_messages SET channel_id = ? WHERE conversation_id IN (SELECT id FROM conversations WHERE wa_number_id = ?)",
                     (ch_id, wa_id))

    conn.commit()
    logger.info(f"Backfilled {len(rows)} WA numbers into workspaces/channels")


def _create_default_workspace(conn: sqlite3.Connection) -> None:
    """Create a default workspace when no WA numbers exist."""
    conn.execute(
        "INSERT OR IGNORE INTO workspaces (id, name, description) VALUES (?, ?, ?)",
        ("default", "Default Workspace", "Default workspace created by migration"),
    )
    conn.commit()
