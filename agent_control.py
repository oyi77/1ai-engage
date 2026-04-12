"""Agent-facing control plane for 1ai-engage.

Provides structured operations for:
- querying funnel/lead state
- starting or previewing pipeline stages
- sending targeted outreach/closer actions
- inspecting runtime integrations (WAHA / brain)

This module is intentionally reusable from both a local CLI facade and an MCP
server so agents can control the system without scraping ad-hoc shell output.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import requests

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import brain_client  # noqa: E402
import state_manager  # noqa: E402
from config import (  # noqa: E402
    HUB_URL,
    LOOP_SLEEP_SECONDS,
    MIN_NEW_LEADS_THRESHOLD,
    WAHA_API_KEY,
    WAHA_SESSION,
    WAHA_URL,
)
from leads import FUNNEL_STAGES, load_leads  # noqa: E402
from senders import send_email, send_whatsapp  # noqa: E402

CONTROL_DIR = ROOT / ".agent-control"
LOGS_DIR = CONTROL_DIR / "logs"

_STAGE_TO_SCRIPT = {
    "strategy": "strategy_agent.py",
    "enricher": "enricher.py",
    "researcher": "researcher.py",
    "generator": "generator.py",
    "reviewer": "reviewer.py",
    "blaster": "blaster.py",
    "reply_tracker": "reply_tracker.py",
    "closer": "closer_agent.py",
    "followup": "followup.py",
    "sheets_sync": "sheets_sync.py",
    "orchestrator": "orchestrator.py",
    "autonomous_loop": "autonomous_loop.py",
}


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class JobRecord:
    job_id: str
    stage: str
    pid: int
    command: list[str]
    log_path: str
    created_at: str


def _ensure_control_dirs() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _is_pid_running(pid: int) -> bool:
    stat_path = Path(f"/proc/{pid}/stat")
    if stat_path.exists():
        try:
            state = stat_path.read_text().split()[2]
            return state != "Z"
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _run_script(script: str, args: list[str] | None = None) -> CommandResult:
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + (args or [])
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    return CommandResult(
        command=cmd,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def start_background_stage(stage: str, args: list[str] | None = None) -> dict[str, Any]:
    if stage not in _STAGE_TO_SCRIPT:
        raise ValueError(f"Unsupported stage: {stage}")
    _ensure_control_dirs()
    job_id = f"{stage}-{uuid4().hex[:12]}"
    log_path = LOGS_DIR / f"{job_id}.log"
    cmd = [sys.executable, str(SCRIPTS_DIR / _STAGE_TO_SCRIPT[stage])] + (args or [])

    if stage == "autonomous_loop":
        owner = job_id
        if not state_manager.acquire_control_lock("autonomous_loop", owner):
            raise ValueError("autonomous_loop is already owned by another running job")

    with open(log_path, "a", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    job = asdict(
        JobRecord(
            job_id=job_id,
            stage=stage,
            pid=proc.pid,
            command=cmd,
            log_path=str(log_path),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    state_manager.create_control_job(
        job_id=job_id,
        stage=stage,
        pid=proc.pid,
        command=json.dumps(cmd),
        status="running",
        log_path=str(log_path),
    )
    state_manager.add_tool_audit(
        "start_background_stage",
        f"stage={stage}",
        payload=json.dumps({"job_id": job_id, "args": args or []}),
    )
    return {**job, "running": True}


def list_jobs() -> dict[str, Any]:
    items = []
    for job in state_manager.list_control_jobs(limit=500):
        pid = int(job["pid"])
        running = _is_pid_running(pid)
        if not running and job.get("status") == "running":
            state_manager.update_control_job(
                job["job_id"],
                status="finished",
                finished_at=datetime.now(timezone.utc).isoformat(),
                exit_code=0 if job.get("exit_code") is None else job.get("exit_code"),
            )
            if job.get("stage") == "autonomous_loop":
                state_manager.release_control_lock("autonomous_loop", job["job_id"])
            job = state_manager.get_control_job(job["job_id"]) or job
        job["running"] = running
        items.append(job)
    return {"count": len(items), "items": items}


def get_job(job_id: str, tail_lines: int = 100) -> dict[str, Any]:
    job = state_manager.get_control_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")
    pid = int(job["pid"])
    running = _is_pid_running(pid)
    if not running and job.get("status") == "running":
        state_manager.update_control_job(
            job_id,
            status="finished",
            finished_at=datetime.now(timezone.utc).isoformat(),
            exit_code=0 if job.get("exit_code") is None else job.get("exit_code"),
        )
        if job.get("stage") == "autonomous_loop":
            state_manager.release_control_lock("autonomous_loop", job_id)
        job = state_manager.get_control_job(job_id) or job
    log_path = Path(job["log_path"])
    log_tail = ""
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        log_tail = "\n".join(lines[-tail_lines:])
    job["running"] = running
    job["log_tail"] = log_tail
    return job


def stop_job(job_id: str) -> dict[str, Any]:
    job = state_manager.get_control_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")
    pid = int(job["pid"])
    running = _is_pid_running(pid)
    if running:
        os.killpg(pid, 15)
    state_manager.update_control_job(
        job_id,
        status="stopped",
        finished_at=datetime.now(timezone.utc).isoformat(),
        exit_code=-15 if running else job.get("exit_code"),
    )
    if job.get("stage") == "autonomous_loop":
        state_manager.release_control_lock("autonomous_loop", job_id)
    state_manager.add_tool_audit(
        "stop_job", f"job_id={job_id}", payload=json.dumps({"pid": pid})
    )
    return {"job_id": job_id, "pid": pid, "was_running": running}


def get_system_config() -> dict[str, Any]:
    return {
        "root": str(ROOT),
        "scripts_dir": str(SCRIPTS_DIR),
        "loop_sleep_seconds": LOOP_SLEEP_SECONDS,
        "min_new_leads_threshold": MIN_NEW_LEADS_THRESHOLD,
        "waha_url": WAHA_URL,
        "waha_session_preference": WAHA_SESSION,
        "waha_api_key_configured": bool(WAHA_API_KEY),
        "hub_url": HUB_URL,
        "brain_online": brain_client.is_online(),
    }


def get_funnel_summary() -> dict[str, Any]:
    counts = state_manager.count_by_status()
    ordered = {stage: counts.get(stage, 0) for stage in FUNNEL_STAGES}
    return {
        "counts": ordered,
        "total": sum(ordered.values()),
        "raw_counts": counts,
    }


def list_leads(status: str | None = None, limit: int = 100) -> dict[str, Any]:
    if status:
        rows = state_manager.get_leads_by_status(status)
    else:
        rows = state_manager.get_all_leads()
    rows = rows[:limit]
    return {
        "count": len(rows),
        "items": rows,
    }


def get_lead(lead_id: str) -> dict[str, Any]:
    lead = state_manager.get_lead_by_id(lead_id)
    if not lead:
        raise ValueError(f"Lead not found: {lead_id}")
    return {
        "lead": lead,
        "events": state_manager.get_event_logs(lead_id=lead_id, limit=100),
    }


def get_recent_events(limit: int = 100) -> dict[str, Any]:
    return {"count": limit, "items": state_manager.get_event_logs(limit=limit)}


def run_stage(
    stage: str,
    *,
    dry_run: bool = False,
    query: str | None = None,
    lead_id: str | None = None,
    location: str | None = None,
    count: int | None = None,
    vertical: str | None = None,
) -> dict[str, Any]:
    if stage not in _STAGE_TO_SCRIPT:
        raise ValueError(f"Unsupported stage: {stage}")

    args: list[str] = []
    if stage == "orchestrator":
        if not query:
            raise ValueError("query is required for orchestrator stage")
        args.append(query)
        if dry_run:
            args.append("--dry-run")
    elif stage == "autonomous_loop":
        if dry_run:
            args.append("--dry-run")
        args.append("--run-once")
    else:
        if dry_run and stage in {"strategy", "generator", "closer"}:
            args.append("--dry-run")
        if lead_id and stage in {"generator", "closer"}:
            args.extend(["--lead-id", lead_id])
        if stage == "strategy":
            if vertical:
                args.extend(["--vertical", vertical])
            if location:
                args.extend(["--location", location])
            if count is not None:
                args.extend(["--count", str(count)])

    result = _run_script(_STAGE_TO_SCRIPT[stage], args)
    return asdict(result)


def preview_autonomous_decision() -> dict[str, Any]:
    result = _run_script("autonomous_loop.py", ["--dry-run", "--run-once"])
    return asdict(result)


def send_test_email(to: str, subject: str, body: str) -> dict[str, Any]:
    ok = send_email(to, subject, body)
    return {"ok": ok, "to": to, "subject": subject}


def send_test_whatsapp(phone: str, message: str) -> dict[str, Any]:
    ok = send_whatsapp(phone, message)
    return {"ok": ok, "phone": phone}


def set_lead_status(lead_id: str, status: str, note: str = "") -> dict[str, Any]:
    state_manager.update_lead_status(lead_id, status)
    if note:
        state_manager.add_event_log(lead_id, "agent_status_update", note)
    state_manager.add_tool_audit(
        "set_lead_status",
        f"lead_id={lead_id}",
        payload=json.dumps({"status": status, "note": note}, ensure_ascii=False),
    )
    return {"ok": True, "lead_id": lead_id, "status": status}


def update_lead_fields(lead_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    if not fields:
        raise ValueError("fields must not be empty")
    state_manager.update_lead(lead_id, **fields)
    state_manager.add_event_log(
        lead_id, "agent_field_update", json.dumps(fields, ensure_ascii=False)
    )
    state_manager.add_tool_audit(
        "update_lead_fields",
        f"lead_id={lead_id}",
        payload=json.dumps(fields, ensure_ascii=False),
    )
    return {"ok": True, "lead_id": lead_id, "updated_fields": sorted(fields.keys())}


def inspect_integrations() -> dict[str, Any]:
    result: dict[str, Any] = {
        "brain_online": brain_client.is_online(),
        "waha": {
            "url": WAHA_URL,
            "api_key_configured": bool(WAHA_API_KEY),
            "preferred_session": WAHA_SESSION,
        },
    }
    if WAHA_API_KEY:
        try:
            r = requests.get(
                f"{WAHA_URL.rstrip('/')}/api/sessions",
                params={"all": "true"},
                headers={"X-Api-Key": WAHA_API_KEY},
                timeout=10,
            )
            result["waha"]["status_code"] = r.status_code
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    result["waha"]["sessions"] = [
                        {
                            "name": item.get("name"),
                            "status": item.get("status"),
                        }
                        for item in data
                    ]
        except Exception as exc:
            result["waha"]["error"] = str(exc)
    return result


def load_dataframe_snapshot(limit: int = 100) -> dict[str, Any]:
    df = load_leads()
    if df is None:
        return {"count": 0, "items": []}
    return {
        "count": min(len(df), limit),
        "columns": list(df.columns),
        "items": df.head(limit).to_dict(orient="records"),
    }


def get_tool_audit(limit: int = 100) -> dict[str, Any]:
    return {"count": limit, "items": state_manager.get_tool_audit(limit=limit)}
