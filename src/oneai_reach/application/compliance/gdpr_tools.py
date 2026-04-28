"""GDPR compliance tools."""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

@dataclass
class ConsentRecord:
    lead_id: str
    email: str
    consent_type: str
    consent_given: bool
    consent_date: str
    consent_method: str
    ip_address: str = None
    withdrawn_date: str = None

class GDPRTools:
    def __init__(self, config: Settings):
        self.config = config
        self.compliance_dir = Path(config.database.data_dir) / "compliance"
        self.compliance_dir.mkdir(parents=True, exist_ok=True)
        self.consent_file = self.compliance_dir / "consents.json"
        self.dnc_file = self.compliance_dir / "do_not_contact.json"
        self.audit_file = self.compliance_dir / "audit_log.json"

    def record_consent(self, lead_id: str, email: str, consent_type: str, given: bool, method: str) -> ConsentRecord:
        consent = ConsentRecord(lead_id=lead_id, email=email, consent_type=consent_type, consent_given=given, consent_date=datetime.now(timezone.utc).isoformat(), consent_method=method)
        consents = self._load_consents()
        consents.append(asdict(consent))
        with open(self.consent_file, 'w') as f: json.dump(consents, f, indent=2)
        self._audit("consent", lead_id, {"type": consent_type, "given": given})
        return consent

    def withdraw_consent(self, lead_id: str, consent_type: str) -> bool:
        consents = self._load_consents()
        for c in consents:
            if c["lead_id"] == lead_id and c["consent_type"] == consent_type and c["consent_given"]:
                c["consent_given"] = False
                c["withdrawn_date"] = datetime.now(timezone.utc).isoformat()
                with open(self.consent_file, 'w') as f: json.dump(consents, f, indent=2)
                self._audit("withdraw", lead_id, {"type": consent_type})
                return True
        return False

    def has_consent(self, lead_id: str, consent_type: str) -> bool:
        return any(c["lead_id"] == lead_id and c["consent_type"] == consent_type and c["consent_given"] and not c.get("withdrawn_date") for c in self._load_consents())

    def add_to_dnc(self, email: str, reason: str = "User request"):
        dnc = self._load_dnc()
        dnc[email] = {"email": email, "reason": reason, "added_date": datetime.now(timezone.utc).isoformat()}
        with open(self.dnc_file, 'w') as f: json.dump(dnc, f, indent=2)
        self._audit("dnc_add", email, {"reason": reason})

    def is_in_dnc(self, email: str) -> bool:
        return email in self._load_dnc()

    def export_data(self, lead_id: str, data: Dict) -> str:
        export = {"lead_id": lead_id, "export_date": datetime.now(timezone.utc).isoformat(), "data": data}
        path = self.compliance_dir / f"export_{lead_id}.json"
        with open(path, 'w') as f: json.dump(export, f, indent=2)
        self._audit("export", lead_id, {})
        return str(path)

    def delete_data(self, lead_id: str, email: str):
        consents = [c for c in self._load_consents() if c["lead_id"] != lead_id]
        with open(self.consent_file, 'w') as f: json.dump(consents, f, indent=2)
        if email: self.add_to_dnc(email, "GDPR deletion")
        self._audit("delete", lead_id, {})

    def get_report(self) -> Dict:
        consents = self._load_consents()
        return {"total_consents": len(consents), "active": len([c for c in consents if c["consent_given"] and not c.get("withdrawn_date")]), "dnc_count": len(self._load_dnc())}

    def _load_consents(self) -> List[Dict]:
        return json.load(open(self.consent_file)) if self.consent_file.exists() else []

    def _load_dnc(self) -> Dict:
        return json.load(open(self.dnc_file)) if self.dnc_file.exists() else {}

    def _audit(self, action: str, subject: str, details: Dict):
        logs = json.load(open(self.audit_file)) if self.audit_file.exists() else []
        logs.append({"timestamp": datetime.now(timezone.utc).isoformat(), "action": action, "subject": subject, "details": details})
        with open(self.audit_file, 'w') as f: json.dump(logs[-10000:], f, indent=2)

def get_gdpr_tools(config: Settings) -> GDPRTools:
    return GDPRTools(config)
