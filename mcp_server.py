"""MCP server for controlling 1ai-engage.

Usage:
  python3 mcp_server.py --transport stdio
  python3 mcp_server.py --transport http --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

import agent_control as control

mcp = FastMCP(
    "1ai-engage",
    instructions=(
        "Control plane for BerkahKarya 1ai-engage. Use read-only tools to inspect "
        "funnel/lead state first. Prefer dry-run operations before destructive actions. "
        "Use background jobs for long-running stages like autonomous_loop."
    ),
)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def get_system_config() -> dict[str, Any]:
    """Return core runtime config relevant to agent control."""
    return control.get_system_config()


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def get_funnel_summary() -> dict[str, Any]:
    """Return funnel counts across all stages."""
    return control.get_funnel_summary()


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def list_leads(
    status: str | None = Field(
        default=None, description="Optional funnel status filter"
    ),
    limit: int = Field(default=100, description="Maximum leads to return"),
) -> dict[str, Any]:
    """List current leads from SQLite state."""
    return control.list_leads(status=status, limit=limit)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def get_lead(
    lead_id: str = Field(description="Exact lead id from SQLite"),
) -> dict[str, Any]:
    """Get one lead plus recent event log entries."""
    return control.get_lead(lead_id)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def get_recent_events(
    limit: int = Field(default=100, description="Maximum event log rows to return"),
) -> dict[str, Any]:
    """Return recent event log entries from the pipeline database."""
    return control.get_recent_events(limit=limit)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def get_tool_audit(
    limit: int = Field(
        default=100, description="Maximum control-plane audit rows to return"
    ),
) -> dict[str, Any]:
    """Return control-plane tool audit history."""
    return control.get_tool_audit(limit=limit)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=True
    )
)
def inspect_integrations() -> dict[str, Any]:
    """Inspect hub brain and WAHA connectivity/session visibility."""
    return control.inspect_integrations()


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    )
)
def preview_autonomous_decision() -> dict[str, Any]:
    """Run one dry-run autonomous loop iteration and return the decision output."""
    return control.preview_autonomous_decision()


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
def run_stage(
    stage: str = Field(
        description="One of: strategy,enricher,researcher,generator,reviewer,blaster,reply_tracker,closer,followup,sheets_sync,orchestrator,autonomous_loop"
    ),
    dry_run: bool = Field(
        default=False, description="Enable safe dry-run when the stage supports it"
    ),
    query: str | None = Field(
        default=None, description="Required for orchestrator full/dry-run execution"
    ),
    lead_id: str | None = Field(
        default=None, description="Optional lead id for generator/closer"
    ),
    location: str | None = Field(
        default=None, description="Optional location for strategy stage"
    ),
    count: int | None = Field(
        default=None, description="Optional lead count for strategy stage"
    ),
    vertical: str | None = Field(
        default=None, description="Optional vertical override for strategy stage"
    ),
) -> dict[str, Any]:
    """Run a stage synchronously and return stdout/stderr/result."""
    return control.run_stage(
        stage,
        dry_run=dry_run,
        query=query,
        lead_id=lead_id,
        location=location,
        count=count,
        vertical=vertical,
    )


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    )
)
def start_background_stage(
    stage: str = Field(
        description="Stage to run in background; best for autonomous_loop or long-running stages"
    ),
    args: list[str] = Field(
        default_factory=list, description="Raw CLI args to pass to the script"
    ),
) -> dict[str, Any]:
    """Start a background job and return a job id plus log path."""
    return control.start_background_stage(stage, args=args)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def list_jobs() -> dict[str, Any]:
    """List background jobs started by the control plane."""
    return control.list_jobs()


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def get_job(
    job_id: str = Field(
        description="Background job id returned by start_background_stage"
    ),
    tail_lines: int = Field(
        default=100, description="Number of trailing log lines to include"
    ),
) -> dict[str, Any]:
    """Get one background job status plus tail of its log."""
    return control.get_job(job_id, tail_lines=tail_lines)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
        open_world_hint=False,
    )
)
def stop_job(
    job_id: str = Field(description="Background job id to terminate"),
) -> dict[str, Any]:
    """Stop a background job started by the control plane."""
    return control.stop_job(job_id)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
def send_test_email(
    to: str = Field(description="Recipient email address"),
    subject: str = Field(description="Email subject"),
    body: str = Field(description="Email body"),
) -> dict[str, Any]:
    """Send a real email using the repo's outbound chain."""
    return control.send_test_email(to=to, subject=subject, body=body)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
        open_world_hint=True,
    )
)
def send_test_whatsapp(
    phone: str = Field(description="Target phone number, Indonesian numbers supported"),
    message: str = Field(description="WhatsApp text body"),
) -> dict[str, Any]:
    """Send a real WhatsApp message using WAHA/wacli fallback."""
    return control.send_test_whatsapp(phone=phone, message=message)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
        open_world_hint=False,
    )
)
def set_lead_status(
    lead_id: str = Field(description="Exact lead id"),
    status: str = Field(description="New funnel status"),
    note: str = Field(
        default="", description="Optional operator note recorded in event_log"
    ),
) -> dict[str, Any]:
    """Update one lead's funnel status directly."""
    return control.set_lead_status(lead_id=lead_id, status=status, note=note)


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
        open_world_hint=False,
    )
)
def update_lead_fields(
    lead_id: str = Field(description="Exact lead id"),
    fields_json: str = Field(description="JSON object of fields to update"),
) -> dict[str, Any]:
    """Update arbitrary lead fields from a JSON payload."""
    return control.update_lead_fields(
        lead_id=lead_id, fields=__import__("json").loads(fields_json)
    )


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, idempotent_hint=True, open_world_hint=False
    )
)
def load_dataframe_snapshot(
    limit: int = Field(default=100, description="Maximum rows to include"),
) -> dict[str, Any]:
    """Return a tabular snapshot of current leads for agents that prefer dataframe-like data."""
    return control.load_dataframe_snapshot(limit=limit)


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP server for 1ai-engage")
    parser.add_argument(
        "--transport", choices=["stdio", "http", "sse"], default="stdio"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            streamable_http_path="/mcp",
            stateless_http=True,
        )


if __name__ == "__main__":
    main()
