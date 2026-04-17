"""Pytest configuration for integration tests."""

import os
import pytest


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_api_key")
    monkeypatch.setenv("HUB_URL", "http://localhost:9099")
    monkeypatch.setenv("WAHA_URL", "http://localhost:3000")
    monkeypatch.setenv("WAHA_API_KEY", "test_waha_key")

    from oneai_reach.config.settings import Settings

    return Settings()
