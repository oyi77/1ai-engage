"""Compliance API endpoints - GDPR, bounces, unsubscribes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from oneai_reach.config.settings import get_settings
from oneai_reach.application.compliance.gdpr_tools import get_gdpr_tools
from oneai_reach.application.compliance.bounce_handler import get_bounce_handler
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/compliance", tags=["compliance"])
config = get_settings()


class ComplianceOverviewResponse(BaseModel):
    total_consents: int
    active_consents: int
    withdrawn_consents: int
    dnc_count: int
    suppression_count: int
    bounce_stats: Dict[str, int]
    list_health_score: int
    list_health_status: str


@router.get("/overview", response_model=Dict[str, ComplianceOverviewResponse])
def get_compliance_overview():
    """Get compliance dashboard overview."""
    gdpr = get_gdpr_tools(config)
    bounce = get_bounce_handler(config)
    
    gdpr_report = gdpr.get_report()
    health = bounce.get_list_health_score()
    
    return {
        "data": ComplianceOverviewResponse(
            total_consents=gdpr_report.get("total_consents", 0),
            active_consents=gdpr_report.get("active", 0),
            withdrawn_consents=gdpr_report.get("withdrawn_consents", 0),
            dnc_count=gdpr_report.get("dnc_count", 0),
            suppression_count=health.get("suppression_list_size", 0),
            bounce_stats={
                "hard_bounces": health.get("hard_bounces", 0),
                "soft_bounces": health.get("soft_bounces", 0),
                "spam_complaints": health.get("spam_complaints", 0),
            },
            list_health_score=int(health.get("score", 0)),
            list_health_status=health.get("status", "unknown")
        )
    }


@router.get("/consents", response_model=List[Dict[str, Any]])
def get_consents(limit: int = 100):
    """Get recent consent records."""
    import json
    from pathlib import Path
    consent_file = Path(config.database.data_dir) / "compliance" / "consents.json"
    
    if not consent_file.exists():
        return []
    
    with open(consent_file) as f:
        consents = json.load(f)
    
    return consents[-limit:]


@router.get("/bounces", response_model=List[Dict[str, Any]])
def get_bounces(limit: int = 100):
    """Get recent bounce records."""
    import json
    from pathlib import Path
    bounce_file = Path(config.database.data_dir) / "compliance" / "bounces.json"
    
    if not bounce_file.exists():
        return []
    
    with open(bounce_file) as f:
        bounces = json.load(f)
    
    return bounces[-limit:]


@router.get("/unsubscribes", response_model=List[Dict[str, Any]])
def get_unsubscribes(limit: int = 100):
    """Get recent unsubscribe records."""
    import json
    from pathlib import Path
    unsub_file = Path(config.database.data_dir) / "compliance" / "unsubscribes.json"
    
    if not unsub_file.exists():
        return []
    
    with open(unsub_file) as f:
        unsubscribes = json.load(f)
    
    return unsubscribes[-limit:]


@router.post("/unsubscribe/{email}")
def unsubscribe_email(email: str, reason: str = "Manual request"):
    """Manually unsubscribe an email address."""
    bounce = get_bounce_handler(config)
    bounce.add_to_suppression(email, f"manual_unsubscribe: {reason}")
    return {"status": "success", "message": f"{email} unsubscribed"}


@router.get("/audit-log", response_model=List[Dict[str, Any]])
def get_audit_log(limit: int = 100):
    """Get recent audit log entries."""
    import json
    from pathlib import Path
    audit_file = Path(config.database.data_dir) / "compliance" / "audit_log.json"
    
    if not audit_file.exists():
        return []
    
    with open(audit_file) as f:
        logs = json.load(f)
    
    return logs[-limit:]
