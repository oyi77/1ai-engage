import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts"))

from oneai_reach.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_agent_control():
    with patch("oneai_reach.cli.main.agent_control") as mock:
        yield mock


class TestCLIBasics:
    def test_cli_help(self, runner):
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "1ai-reach" in result.output
        assert "funnel" in result.output
        assert "stages" in result.output

    def test_cli_version(self, runner):
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestFunnelCommands:
    def test_funnel_help(self, runner):
        result = runner.invoke(cli, ["funnel", "--help"])

        assert result.exit_code == 0
        assert "Manage funnel and leads" in result.output

    def test_funnel_summary(self, runner, mock_agent_control):
        mock_agent_control.get_funnel_summary.return_value = {
            "total_leads": 100,
            "by_status": {"new": 50, "contacted": 30},
        }

        result = runner.invoke(cli, ["funnel", "summary"])

        assert result.exit_code == 0
        assert "total_leads" in result.output
        assert "100" in result.output

    def test_funnel_summary_error(self, runner, mock_agent_control):
        mock_agent_control.get_funnel_summary.side_effect = Exception("DB error")

        result = runner.invoke(cli, ["funnel", "summary"])

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_funnel_leads_default(self, runner, mock_agent_control):
        mock_agent_control.list_leads.return_value = {
            "leads": [{"lead_id": "1", "status": "new", "company": "Acme"}]
        }

        result = runner.invoke(cli, ["funnel", "leads"])

        assert result.exit_code == 0
        assert "lead_id" in result.output
        mock_agent_control.list_leads.assert_called_once_with(status=None, limit=100)

    def test_funnel_leads_with_filters(self, runner, mock_agent_control):
        mock_agent_control.list_leads.return_value = {"leads": []}

        result = runner.invoke(
            cli, ["funnel", "leads", "--status", "new", "--limit", "50"]
        )

        assert result.exit_code == 0
        mock_agent_control.list_leads.assert_called_once_with(status="new", limit=50)

    def test_funnel_lead_detail(self, runner, mock_agent_control):
        mock_agent_control.get_lead.return_value = {
            "lead_id": "123",
            "status": "new",
            "company": "Acme Corp",
        }

        result = runner.invoke(cli, ["funnel", "lead", "123"])

        assert result.exit_code == 0
        assert "123" in result.output
        assert "Acme Corp" in result.output

    def test_funnel_set_status(self, runner, mock_agent_control):
        mock_agent_control.set_lead_status.return_value = {
            "lead_id": "123",
            "status": "qualified",
        }

        result = runner.invoke(
            cli, ["funnel", "set-status", "123", "qualified", "--note", "Good fit"]
        )

        assert result.exit_code == 0
        mock_agent_control.set_lead_status.assert_called_once_with(
            "123", status="qualified", note="Good fit"
        )


class TestStagesCommands:
    def test_stages_help(self, runner):
        result = runner.invoke(cli, ["stages", "--help"])

        assert result.exit_code == 0
        assert "Execute pipeline stages" in result.output

    def test_stages_list(self, runner):
        result = runner.invoke(cli, ["stages", "list"])

        assert result.exit_code == 0
        assert "enricher" in result.output
        assert "generator" in result.output
        assert "blaster" in result.output

    def test_stages_run(self, runner, mock_agent_control):
        mock_agent_control.run_stage.return_value = {
            "stage": "enricher",
            "status": "completed",
        }

        result = runner.invoke(cli, ["stages", "run", "enricher"])

        assert result.exit_code == 0
        assert "completed" in result.output
        mock_agent_control.run_stage.assert_called_once_with(
            "enricher", args=[], dry_run=False
        )

    def test_stages_run_with_args(self, runner, mock_agent_control):
        mock_agent_control.run_stage.return_value = {"status": "completed"}

        result = runner.invoke(
            cli,
            [
                "stages",
                "run",
                "enricher",
                "--args",
                "arg1",
                "--args",
                "arg2",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        mock_agent_control.run_stage.assert_called_once_with(
            "enricher", args=["arg1", "arg2"], dry_run=True
        )

    def test_stages_start(self, runner, mock_agent_control):
        mock_agent_control.start_background_stage.return_value = {
            "job_id": "job_123",
            "stage": "enricher",
        }

        result = runner.invoke(cli, ["stages", "start", "enricher"])

        assert result.exit_code == 0
        assert "job_123" in result.output


class TestJobsCommands:
    def test_jobs_help(self, runner):
        result = runner.invoke(cli, ["jobs", "--help"])

        assert result.exit_code == 0
        assert "Manage background jobs" in result.output

    def test_jobs_list(self, runner, mock_agent_control):
        mock_agent_control.list_jobs.return_value = {
            "jobs": [{"job_id": "job_123", "stage": "enricher", "status": "running"}]
        }

        result = runner.invoke(cli, ["jobs", "list"])

        assert result.exit_code == 0
        assert "job_123" in result.output
        assert "enricher" in result.output

    def test_jobs_logs(self, runner, mock_agent_control):
        mock_agent_control.get_job.return_value = {
            "job_id": "job_123",
            "logs": ["Starting enricher", "Processing leads"],
        }

        result = runner.invoke(cli, ["jobs", "logs", "job_123"])

        assert result.exit_code == 0
        assert "job_123" in result.output
        mock_agent_control.get_job.assert_called_once_with("job_123", tail_lines=100)

    def test_jobs_logs_with_tail(self, runner, mock_agent_control):
        mock_agent_control.get_job.return_value = {"job_id": "job_123", "logs": []}

        result = runner.invoke(cli, ["jobs", "logs", "job_123", "--tail", "50"])

        assert result.exit_code == 0
        mock_agent_control.get_job.assert_called_once_with("job_123", tail_lines=50)

    def test_jobs_stop(self, runner, mock_agent_control):
        mock_agent_control.stop_job.return_value = {
            "job_id": "job_123",
            "status": "stopped",
        }

        result = runner.invoke(cli, ["jobs", "stop", "job_123"])

        assert result.exit_code == 0
        assert "stopped" in result.output


class TestWhatsAppCommands:
    def test_wa_help(self, runner):
        result = runner.invoke(cli, ["wa", "--help"])

        assert result.exit_code == 0
        assert "Manage WhatsApp sessions" in result.output

    def test_wa_sessions(self, runner, mock_agent_control):
        mock_agent_control.list_wa_sessions.return_value = {
            "sessions": [{"name": "default", "status": "WORKING"}]
        }

        result = runner.invoke(cli, ["wa", "sessions"])

        assert result.exit_code == 0
        assert "default" in result.output

    def test_wa_create(self, runner, mock_agent_control):
        mock_agent_control.create_wa_session.return_value = {
            "session_name": "test_session",
            "status": "created",
        }

        result = runner.invoke(cli, ["wa", "create", "test_session"])

        assert result.exit_code == 0
        assert "test_session" in result.output

    def test_wa_create_with_phone(self, runner, mock_agent_control):
        mock_agent_control.create_wa_session.return_value = {"status": "created"}

        result = runner.invoke(
            cli, ["wa", "create", "test_session", "--phone", "6281234567890"]
        )

        assert result.exit_code == 0
        mock_agent_control.create_wa_session.assert_called_once_with(
            session_name="test_session", phone_number="6281234567890"
        )

    def test_wa_delete(self, runner, mock_agent_control):
        mock_agent_control.delete_wa_session.return_value = {"status": "deleted"}

        result = runner.invoke(cli, ["wa", "delete", "test_session"])

        assert result.exit_code == 0

    def test_wa_status(self, runner, mock_agent_control):
        mock_agent_control.get_wa_session_status.return_value = {
            "session": "default",
            "status": "WORKING",
        }

        result = runner.invoke(cli, ["wa", "status", "default"])

        assert result.exit_code == 0
        assert "WORKING" in result.output

    def test_wa_qr(self, runner, mock_agent_control):
        mock_agent_control.get_wa_qr_code.return_value = {
            "qr_code": "data:image/png;base64,..."
        }

        result = runner.invoke(cli, ["wa", "qr", "default"])

        assert result.exit_code == 0
        assert "qr_code" in result.output


class TestTestCommands:
    def test_test_help(self, runner):
        result = runner.invoke(cli, ["test", "--help"])

        assert result.exit_code == 0
        assert "Send test messages" in result.output

    def test_test_email(self, runner, mock_agent_control):
        mock_agent_control.send_test_email.return_value = {
            "status": "sent",
            "to": "test@example.com",
        }

        result = runner.invoke(
            cli, ["test", "email", "test@example.com", "Test Subject", "Test Body"]
        )

        assert result.exit_code == 0
        assert "sent" in result.output
        mock_agent_control.send_test_email.assert_called_once_with(
            to="test@example.com", subject="Test Subject", body="Test Body"
        )

    def test_test_whatsapp(self, runner, mock_agent_control):
        mock_agent_control.send_test_whatsapp.return_value = {
            "status": "sent",
            "phone": "6281234567890",
        }

        result = runner.invoke(
            cli, ["test", "whatsapp", "6281234567890", "Hello from CLI"]
        )

        assert result.exit_code == 0
        assert "sent" in result.output


class TestSystemCommands:
    def test_system_help(self, runner):
        result = runner.invoke(cli, ["system", "--help"])

        assert result.exit_code == 0
        assert "System status and configuration" in result.output

    def test_system_config(self, runner, mock_agent_control):
        mock_agent_control.get_system_config.return_value = {
            "environment": "production",
            "version": "1.0.0",
        }

        result = runner.invoke(cli, ["system", "config"])

        assert result.exit_code == 0
        assert "environment" in result.output

    def test_system_integrations(self, runner, mock_agent_control):
        mock_agent_control.inspect_integrations.return_value = {
            "waha": {"status": "connected"},
            "brain": {"status": "connected"},
        }

        result = runner.invoke(cli, ["system", "integrations"])

        assert result.exit_code == 0
        assert "waha" in result.output

    def test_system_events(self, runner, mock_agent_control):
        mock_agent_control.get_recent_events.return_value = {
            "events": [{"type": "lead_created", "timestamp": "2026-04-17T20:00:00"}]
        }

        result = runner.invoke(cli, ["system", "events"])

        assert result.exit_code == 0
        mock_agent_control.get_recent_events.assert_called_once_with(limit=100)

    def test_system_events_with_limit(self, runner, mock_agent_control):
        mock_agent_control.get_recent_events.return_value = {"events": []}

        result = runner.invoke(cli, ["system", "events", "--limit", "50"])

        assert result.exit_code == 0
        mock_agent_control.get_recent_events.assert_called_once_with(limit=50)

    def test_system_snapshot(self, runner, mock_agent_control):
        mock_agent_control.load_dataframe_snapshot.return_value = {
            "records": [{"id": 1, "name": "Lead 1"}]
        }

        result = runner.invoke(cli, ["system", "snapshot"])

        assert result.exit_code == 0

    def test_system_audit(self, runner, mock_agent_control):
        mock_agent_control.get_tool_audit.return_value = {
            "audit_entries": [{"tool": "enricher", "timestamp": "2026-04-17"}]
        }

        result = runner.invoke(cli, ["system", "audit"])

        assert result.exit_code == 0

    def test_system_preview(self, runner, mock_agent_control):
        mock_agent_control.preview_autonomous_decision.return_value = {
            "next_action": "enrich_leads",
            "confidence": 0.95,
        }

        result = runner.invoke(cli, ["system", "preview"])

        assert result.exit_code == 0
        assert "next_action" in result.output


class TestKnowledgeBaseCommands:
    def test_kb_help(self, runner):
        result = runner.invoke(cli, ["kb", "--help"])

        assert result.exit_code == 0
        assert "Manage knowledge base" in result.output

    def test_kb_list(self, runner, mock_agent_control):
        mock_agent_control.list_kb_entries.return_value = {
            "entries": [{"id": 1, "category": "faq", "content": "What is pricing?"}]
        }

        result = runner.invoke(cli, ["kb", "list", "6281234567890"])

        assert result.exit_code == 0
        assert "faq" in result.output

    def test_kb_list_with_category(self, runner, mock_agent_control):
        mock_agent_control.list_kb_entries.return_value = {"entries": []}

        result = runner.invoke(
            cli, ["kb", "list", "6281234567890", "--category", "faq"]
        )

        assert result.exit_code == 0
        mock_agent_control.list_kb_entries.assert_called_once_with(
            "6281234567890", category="faq"
        )

    def test_kb_add(self, runner, mock_agent_control):
        mock_agent_control.add_kb_entry.return_value = {
            "id": 1,
            "category": "faq",
            "content": "New entry",
        }

        result = runner.invoke(cli, ["kb", "add", "faq", "New entry"])

        assert result.exit_code == 0
        mock_agent_control.add_kb_entry.assert_called_once_with(
            category="faq", content="New entry", tags=[]
        )

    def test_kb_add_with_tags(self, runner, mock_agent_control):
        mock_agent_control.add_kb_entry.return_value = {"id": 1}

        result = runner.invoke(
            cli,
            ["kb", "add", "faq", "New entry", "--tags", "pricing", "--tags", "general"],
        )

        assert result.exit_code == 0
        mock_agent_control.add_kb_entry.assert_called_once_with(
            category="faq", content="New entry", tags=["pricing", "general"]
        )


class TestErrorHandling:
    def test_command_not_found(self, runner):
        result = runner.invoke(cli, ["nonexistent"])

        assert result.exit_code != 0

    def test_missing_required_argument(self, runner):
        result = runner.invoke(cli, ["funnel", "lead"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output
