"""Persona system migration — adds personas table, channel_persona_assignments,
and workspace default_persona_id. Seeds built-in personas and auto-assigns
existing channels. Idempotent — safe to run multiple times."""

import json
import sqlite3

from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

BUILTIN_PERSONAS = [
    {
        "id": "cs-friendly",
        "name": "Friendly CS Agent",
        "scope": "cs",
        "system_prompt": (
            "You are a friendly, helpful customer service agent for a health and beauty brand. "
            "You speak in warm, casual Bahasa Indonesia. You help customers with product questions, "
            "order status, and complaints. Always be empathetic and solution-oriented."
        ),
        "tone": "casual",
        "language": "id",
    },
    {
        "id": "cs-skincare",
        "name": "Skincare Expert",
        "scope": "cs",
        "system_prompt": (
            "You are a knowledgeable skincare and beauty consultant. You understand ingredients, "
            "skin types, and product benefits. You provide personalized recommendations in friendly "
            "Bahasa Indonesia. You are warm but professional."
        ),
        "tone": "casual",
        "language": "id",
    },
    {
        "id": "sales-aggressive",
        "name": "Aggressive Sales",
        "scope": "outreach",
        "system_prompt": (
            "You are a confident, results-driven sales agent. You focus on benefits, urgency, and "
            "closing deals. You write concise, punchy messages. You create FOMO and emphasize "
            "limited-time offers. Professional but direct."
        ),
        "tone": "professional",
        "language": "en",
    },
    {
        "id": "sales-consultative",
        "name": "Consultative Sales",
        "scope": "outreach",
        "system_prompt": (
            "You are a consultative sales professional. You ask questions to understand needs before "
            "recommending solutions. You build trust through expertise. You write thoughtful, "
            "personalized messages that focus on value."
        ),
        "tone": "formal",
        "language": "en",
    },
    {
        "id": "general-assistant",
        "name": "General Assistant",
        "scope": "universal",
        "system_prompt": (
            "You are a helpful general-purpose assistant. You are friendly, concise, and adapt your "
            "tone to the conversation. You can handle customer service, sales, and general inquiries."
        ),
        "tone": "casual",
        "language": "id",
    },
]


def run_persona_migration(db_path: str) -> None:
    """Run persona migration. Creates tables, seeds built-in personas,
    and auto-assigns existing channels."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        _create_tables(conn)
        _add_columns(conn)
        _seed_personas(conn)
        _auto_assign(conn)
        conn.commit()
        logger.info("Persona migration complete")
    except Exception as e:
        conn.rollback()
        logger.error(f"Persona migration failed: {e}")
        raise
    finally:
        conn.close()


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            scope TEXT NOT NULL DEFAULT 'universal',
            system_prompt TEXT NOT NULL,
            tone TEXT DEFAULT 'casual',
            language TEXT DEFAULT 'id',
            example_replies TEXT,
            is_builtin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS channel_persona_assignments (
            channel_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            persona_id TEXT NOT NULL,
            PRIMARY KEY (channel_id, mode),
            FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
            FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cpa_channel ON channel_persona_assignments(channel_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cpa_persona ON channel_persona_assignments(persona_id)"
    )
    conn.commit()
    logger.info("Persona tables created/verified")


def _add_columns(conn: sqlite3.Connection) -> None:
    try:
        conn.execute("ALTER TABLE workspaces ADD COLUMN default_persona_id TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()


def _seed_personas(conn: sqlite3.Connection) -> None:
    cur = conn.execute("SELECT COUNT(*) as cnt FROM personas")
    if cur.fetchone()["cnt"] > 0:
        return  # Already seeded

    for p in BUILTIN_PERSONAS:
        conn.execute(
            """INSERT INTO personas (id, name, scope, system_prompt, tone, language, is_builtin)
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (p["id"], p["name"], p["scope"], p["system_prompt"], p["tone"], p["language"]),
        )
    conn.commit()
    logger.info(f"Seeded {len(BUILTIN_PERSONAS)} built-in personas")


def _auto_assign(conn: sqlite3.Connection) -> None:
    """Auto-assign personas to existing channels based on mode."""
    cur = conn.execute("SELECT COUNT(*) as cnt FROM channel_persona_assignments")
    if cur.fetchone()["cnt"] > 0:
        return  # Already assigned

    channels = conn.execute("SELECT id, mode FROM channels").fetchall()
    mode_persona_map = {
        "cs": "cs-friendly",
        "coldcall": "sales-aggressive",
        "nurture": "sales-consultative",
        "support": "cs-friendly",
    }

    for ch in channels:
        persona_id = mode_persona_map.get(ch["mode"], "general-assistant")
        conn.execute(
            "INSERT OR IGNORE INTO channel_persona_assignments (channel_id, mode, persona_id) VALUES (?, ?, ?)",
            (ch["id"], ch["mode"], persona_id),
        )
    conn.commit()
    logger.info(f"Auto-assigned personas to {len(channels)} channels")
