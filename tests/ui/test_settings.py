"""
Unit tests for ui/components/settings.py

Tests the read_env() and write_env() helper functions directly,
using pytest's tmp_path and monkeypatch fixtures (no Playwright needed).
"""

import sys
from pathlib import Path

# Ensure repo root is on path so ui package can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import ui.components.settings as settings_mod


def test_read_env_missing_file_returns_empty(tmp_path, monkeypatch):
    """read_env() returns {} when .env file does not exist."""
    monkeypatch.setattr(settings_mod, "ENV_PATH", tmp_path / "nonexistent.env")
    result = settings_mod.read_env()
    assert result == {}


def test_read_env_empty_file_returns_empty(tmp_path, monkeypatch):
    """read_env() returns {} for an empty .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    result = settings_mod.read_env()
    assert result == {}


def test_read_env_parses_values(tmp_path, monkeypatch):
    """read_env() correctly parses key=value pairs."""
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    result = settings_mod.read_env()
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_read_env_skips_comments(tmp_path, monkeypatch):
    """read_env() does not include comment lines in the result."""
    env_file = tmp_path / ".env"
    env_file.write_text("# This is a comment\nKEY=value\n# Another comment\n")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    result = settings_mod.read_env()
    assert result == {"KEY": "value"}
    assert len(result) == 1


def test_read_env_strips_quotes(tmp_path, monkeypatch):
    """read_env() strips surrounding single/double quotes from values."""
    env_file = tmp_path / ".env"
    env_file.write_text("A=\"quoted\"\nB='single'\nC=plain\n")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    result = settings_mod.read_env()
    assert result["A"] == "quoted"
    assert result["B"] == "single"
    assert result["C"] == "plain"


def test_write_env_updates_existing_key(tmp_path, monkeypatch):
    """write_env() updates the value of an existing key in .env."""
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=oldval\n")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    settings_mod.write_env({"KEY": "newval"})
    content = env_file.read_text()
    assert "KEY=newval" in content
    assert "oldval" not in content


def test_write_env_adds_new_key(tmp_path, monkeypatch):
    """write_env() appends a new key=value when the key doesn't exist yet."""
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=yes\n")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    settings_mod.write_env({"NEW_KEY": "newval"})
    content = env_file.read_text()
    assert "EXISTING=yes" in content
    assert "NEW_KEY=newval" in content


def test_write_env_preserves_comments(tmp_path, monkeypatch):
    """write_env() preserves comment lines in the .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("# My config comment\nKEY=old\n")
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    settings_mod.write_env({"KEY": "new"})
    content = env_file.read_text()
    assert "# My config comment" in content
    assert "KEY=new" in content


def test_write_env_creates_file_if_missing(tmp_path, monkeypatch):
    """write_env() creates the .env file if it does not exist."""
    env_file = tmp_path / ".env"
    monkeypatch.setattr(settings_mod, "ENV_PATH", env_file)
    settings_mod.write_env({"FRESH_KEY": "freshval"})
    assert env_file.exists()
    assert "FRESH_KEY=freshval" in env_file.read_text()
