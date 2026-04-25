"""CRM Phase C migration — adds email_templates, scheduled_messages, broadcast_lists, and broadcast_sends tables.

This migration builds on Phase B to enable full pipeline functionality:
- Email templates for reusable email content
- Scheduled messages for delayed/outbound messages  
- Broadcast lists for bulk messaging
- Broadcast sends for tracking bulk message delivery

Idempotent — safe to run multiple times."""

import sqlite3
from typing import Optional

from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

DEFAULT_EMAIL_TEMPLATES = [
    {
        "name": "Welcome Email",
        "subject": "Welcome to {{company}}!",
        "body": "Hi {{name}},\n\nWelcome to {{company}}! We're excited to have you on board.",
        "category": "onboarding",
    },
    {
        "name": "Follow Up",
        "subject": "Following up on our conversation",
        "body": "Hi {{name}},\n\nI wanted to follow up on our recent conversation about {{topic}}.",
        "category": "follow-up",
    },
    {
        "name": "Meeting Request",
        "subject": "Let's schedule a meeting",
        "body": "Hi {{name}},\n\nI'd love to schedule a meeting to discuss {{topic}}. When works for you?",
        "category": "meeting",
    },
]


def run_crm_migration(db_path: str) -> None:
    """Run CRM Phase C migration.

    Args:
        db_path: Path to SQLite database file
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        _create_tables(conn)
        _seed_templates(conn)
        conn.commit()
        logger.info("CRM Phase C migration complete")
    except Exception as e:
        conn.rollback()
        logger.error(f"CRM Phase C migration failed: {e}")
        raise
    finally:
        conn.close()


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create all CRM Phase C tables if they don't exist."""

    # email_templates — reusable email templates
    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wa_number_id TEXT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            variables TEXT,
            is_predefined INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE SET NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_email_templates_wa ON email_templates(wa_number_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_email_templates_category ON email_templates(category)"
    )

    # scheduled_messages — messages scheduled for future delivery
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            conversation_id INTEGER,
            wa_number_id TEXT,
            lead_id TEXT,
            channel TEXT NOT NULL DEFAULT 'email',  -- email, whatsapp, sms
            message_type TEXT NOT NULL DEFAULT 'text',  -- text, template, media
            content TEXT NOT NULL,
            subject TEXT,  -- for email
            template_id INTEGER,  -- reference to email_templates
            template_variables TEXT,  -- JSON object for template variables
            scheduled_at TEXT NOT NULL,
            timezone TEXT DEFAULT 'Asia/Jakarta',
            status TEXT DEFAULT 'pending',  -- pending, processing, sent, failed, cancelled
            sent_at TEXT,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
            FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE SET NULL,
            FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL,
            FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE SET NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scheduled_contact ON scheduled_messages(contact_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scheduled_conv ON scheduled_messages(conversation_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scheduled_status ON scheduled_messages(status)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_messages(scheduled_at)"
    )

    # broadcast_lists — lists for bulk messaging
    conn.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wa_number_id TEXT,
            name TEXT NOT NULL,
            description TEXT,
            filter_criteria TEXT,  -- JSON object for filter criteria
            total_recipients INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE SET NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_lists_wa ON broadcast_lists(wa_number_id)"
    )

    # broadcast_list_recipients — junction table for broadcast list members
    conn.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_list_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_list_id INTEGER NOT NULL,
            contact_id INTEGER,
            lead_id TEXT,
            phone TEXT,
            email TEXT,
            added_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (broadcast_list_id) REFERENCES broadcast_lists(id) ON DELETE CASCADE,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
            FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_list ON broadcast_list_recipients(broadcast_list_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_contact ON broadcast_list_recipients(contact_id)"
    )

    # broadcast_sends — tracking bulk message sends
    conn.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_sends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_list_id INTEGER NOT NULL,
            wa_number_id TEXT,
            name TEXT NOT NULL,
            subject TEXT,  -- for email
            content TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'email',
            total_recipients INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0,
            delivered_count INTEGER DEFAULT 0,
            opened_count INTEGER DEFAULT 0,
            clicked_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',  -- draft, scheduled, sending, completed, cancelled
            scheduled_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (broadcast_list_id) REFERENCES broadcast_lists(id) ON DELETE CASCADE,
            FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id) ON DELETE SET NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_sends_list ON broadcast_sends(broadcast_list_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_sends_status ON broadcast_sends(status)"
    )

    # broadcast_send_recipients — individual recipient tracking per broadcast
    conn.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_send_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_send_id INTEGER NOT NULL,
            contact_id INTEGER,
            lead_id TEXT,
            phone TEXT,
            email TEXT,
            status TEXT DEFAULT 'pending',  -- pending, sent, delivered, opened, clicked, failed
            sent_at TEXT,
            delivered_at TEXT,
            opened_at TEXT,
            clicked_at TEXT,
            error_message TEXT,
            FOREIGN KEY (broadcast_send_id) REFERENCES broadcast_sends(id) ON DELETE CASCADE,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
            FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_send_recipients_send ON broadcast_send_recipients(broadcast_send_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_broadcast_send_recipients_status ON broadcast_send_recipients(status)"
    )

    conn.commit()
    logger.info("CRM Phase C tables created/verified")


def _seed_templates(conn: sqlite3.Connection) -> None:
    """Seed default email templates if table is empty."""
    cur = conn.execute("SELECT COUNT(*) as cnt FROM email_templates WHERE is_predefined = 1")
    if cur.fetchone()["cnt"] > 0:
        return  # Already seeded

    for t in DEFAULT_EMAIL_TEMPLATES:
        variables = ["name", "company"]  # Default variables
        if "topic" in t["body"]:
            variables.append("topic")
        
        conn.execute(
            """
            INSERT INTO email_templates (name, subject, body, category, variables, is_predefined)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (t["name"], t["subject"], t["body"], t["category"], ",".join(variables)),
        )
    conn.commit()
    logger.info(f"Seeded {len(DEFAULT_EMAIL_TEMPLATES)} default email templates")


if __name__ == "__main__":
    import sys
    from oneai_reach.config.settings import get_settings

    settings = get_settings()
    run_crm_migration(settings.database.db_file)
    print(f"CRM Phase C migration complete: {settings.database.db_file}")
