"""Migration 002: Add test_mode column to conversations table.

This migration adds a test_mode BOOLEAN column to track conversations in test mode,
preventing infinite loops from auto-reply echoes.
"""

import sqlite3
import sys
from pathlib import Path


def upgrade(db_path: str, dry_run: bool = False) -> bool:
    """Add test_mode column to conversations table.

    Args:
        db_path: Path to SQLite database
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1] for row in cursor.fetchall()}

        if "test_mode" in columns:
            print("✓ test_mode column already exists")
            conn.close()
            return True

        if dry_run:
            print("[DRY RUN] Would add test_mode column to conversations table")
            print(
                "[DRY RUN] ALTER TABLE conversations ADD COLUMN test_mode INTEGER DEFAULT 0"
            )
            conn.close()
            return True

        # Add column with DEFAULT 0
        cursor.execute("""
            ALTER TABLE conversations 
            ADD COLUMN test_mode INTEGER DEFAULT 0
        """)

        conn.commit()

        # Verify column was added
        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1] for row in cursor.fetchall()}

        if "test_mode" not in columns:
            print("✗ Failed to add test_mode column")
            conn.close()
            return False

        # Verify all existing rows have test_mode = 0
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE test_mode = 0")
        count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversations")
        total = cursor.fetchone()[0]

        print(f"✓ test_mode column added successfully")
        print(f"✓ {count}/{total} conversations have test_mode = 0")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def rollback(db_path: str, dry_run: bool = False) -> bool:
    """Remove test_mode column from conversations table.

    Args:
        db_path: Path to SQLite database
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1] for row in cursor.fetchall()}

        if "test_mode" not in columns:
            print("✓ test_mode column does not exist (nothing to rollback)")
            conn.close()
            return True

        if dry_run:
            print("[DRY RUN] Would remove test_mode column from conversations table")
            print("[DRY RUN] Using SQLite column removal via table recreation")
            conn.close()
            return True

        cursor.execute("BEGIN TRANSACTION")

        cursor.execute("""
            CREATE TABLE conversations_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wa_number_id TEXT,
                contact_phone TEXT NOT NULL,
                contact_name TEXT,
                lead_id TEXT,
                engine_mode TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                last_message_at TEXT,
                message_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                manual_mode INTEGER DEFAULT 0,
                FOREIGN KEY (wa_number_id) REFERENCES wa_numbers(id)
            )
        """)

        cursor.execute("""
            INSERT INTO conversations_temp 
            SELECT id, wa_number_id, contact_phone, contact_name, lead_id, 
                   engine_mode, status, last_message_at, message_count, 
                   created_at, updated_at, manual_mode
            FROM conversations
        """)

        cursor.execute("DROP TABLE conversations")
        cursor.execute("ALTER TABLE conversations_temp RENAME TO conversations")

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_contact 
            ON conversations(contact_phone)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_wa_number 
            ON conversations(wa_number_id)
        """)

        conn.commit()

        cursor.execute("PRAGMA table_info(conversations)")
        columns = {row[1] for row in cursor.fetchall()}

        if "test_mode" in columns:
            print("✗ Failed to remove test_mode column")
            conn.close()
            return False

        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]

        print(f"✓ test_mode column removed successfully")
        print(f"✓ {count} conversations preserved")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python 002_add_test_mode.py <db_path> [upgrade|rollback] [--dry-run]"
        )
        sys.exit(1)

    db_path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "upgrade"
    dry_run = "--dry-run" in sys.argv

    if not Path(db_path).exists():
        print(f"✗ Database not found: {db_path}")
        sys.exit(1)

    if action == "upgrade":
        success = upgrade(db_path, dry_run=dry_run)
    elif action == "rollback":
        success = rollback(db_path, dry_run=dry_run)
    else:
        print(f"✗ Unknown action: {action}")
        sys.exit(1)

    sys.exit(0 if success else 1)
