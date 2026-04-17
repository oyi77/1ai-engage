import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

_root = Path(__file__).parent.parent.parent
_scripts = _root / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

sys.modules["cs_engine"] = Mock()
sys.modules["cs_engine"].handle_inbound_message = Mock(return_value="Test response")
sys.modules["state_manager"] = Mock()
sys.modules["state_manager"].get_wa_number_by_session = Mock(return_value="6281234567890")
sys.modules["state_manager"].add_conversation_message = Mock(return_value=None)
sys.modules["state_manager"].get_or_create_conversation = Mock(return_value=(1, False))
sys.modules["state_manager"].is_manual_mode = Mock(return_value=False)
sys.modules["capi_tracker"] = Mock()
sys.modules["conversation_tracker"] = Mock()
sys.modules["conversation_tracker"].get_active_conversations = Mock(return_value=[])
sys.modules["conversation_tracker"].stop_conversation = Mock(return_value=True)

from oneai_reach.api.main import create_app


def test_app_creation():
    app = create_app()
    assert app is not None
    assert app.title == "1ai-reach API"
    assert app.version == "1.0.0"


def test_health_endpoint_exists():
    app = create_app()
    routes = [route.path for route in app.routes]
    assert "/health" in routes
    assert "/api/v1/health" in routes


def test_admin_routes_exist():
    app = create_app()
    routes = [route.path for route in app.routes]
    assert "/api/v1/admin/status" in routes
    assert "/api/v1/admin/conversations" in routes
    assert "/api/v1/admin/pause" in routes
    assert "/api/v1/admin/resume" in routes


def test_webhook_routes_exist():
    app = create_app()
    routes = [route.path for route in app.routes]
    assert "/api/v1/webhooks/waha/message" in routes
    assert "/api/v1/webhooks/waha/status" in routes
    assert "/api/v1/webhooks/capi/lead" in routes


def test_agent_routes_exist():
    app = create_app()
    routes = [route.path for route in app.routes]
    agent_routes = [r for r in routes if "/api/v1/agents" in r]
    assert len(agent_routes) > 0


def test_mcp_routes_exist():
    app = create_app()
    routes = [route.path for route in app.routes]
    mcp_routes = [r for r in routes if "/api/v1/mcp" in r]
    assert len(mcp_routes) > 0


def test_exception_handlers_configured():
    app = create_app()
    assert len(app.exception_handlers) > 0
