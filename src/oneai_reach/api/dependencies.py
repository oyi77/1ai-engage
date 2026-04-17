"""Dependency injection setup for FastAPI application.

Provides factory functions for creating and injecting dependencies into route handlers.
Uses FastAPI's Depends() pattern for clean, testable dependency management.
"""

from functools import lru_cache

from oneai_reach.config.settings import Settings, get_settings
from oneai_reach.infrastructure.external.brain_client import BrainClient


@lru_cache(maxsize=1)
def get_settings_dep() -> Settings:
    """Get singleton Settings instance."""
    return get_settings()


def get_brain_client(settings: Settings = None) -> BrainClient:
    """Get brain client for hub integration."""
    if settings is None:
        settings = get_settings_dep()

    return BrainClient(
        base_url=settings.hub.url,
        api_key=settings.hub.api_key,
    )
