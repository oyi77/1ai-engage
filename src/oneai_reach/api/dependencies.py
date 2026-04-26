"""Dependency injection setup for FastAPI application.

Provides factory functions for creating and injecting dependencies into route handlers.
Uses FastAPI's Depends() pattern for clean, testable dependency management.
"""

from contextlib import contextmanager
from functools import lru_cache

from fastapi import Depends, Header, HTTPException, status

from oneai_reach.config.settings import Settings, get_settings
from oneai_reach.infrastructure.external.brain_client import BrainClient

import sqlite3


def get_db_path() -> str:
    """Return the SQLite database file path from settings."""
    return get_settings().database.db_file


@contextmanager
def get_db_connection(row_factory=True):
    """Context manager for SQLite connections with guaranteed cleanup.

    Usage:
        with get_db_connection() as conn:
            conn.execute("SELECT ...")

    Yields: sqlite3.Connection (with row_factory=sqlite3.Row by default)
    """
    conn = sqlite3.connect(get_db_path())
    if row_factory:
        conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@lru_cache(maxsize=1)
def get_settings_dep() -> Settings:
    """Get singleton Settings instance."""
    return get_settings()


def get_brain_client(settings: Settings = Depends(get_settings_dep)) -> BrainClient:
    """Get brain client for hub integration."""
    return BrainClient(
        base_url=settings.hub.url,
        api_key=settings.hub.api_key,
    )


async def verify_api_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings_dep),
) -> str:
    """Verify API key from X-API-Key header."""
    valid_keys = settings.api.get_valid_keys()

    if not valid_keys:
        return "dev_mode"

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key
