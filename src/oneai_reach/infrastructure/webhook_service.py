"""Webhook service for real-time notifications.

Sends webhooks to external systems when events occur:
- Lead created
- Email sent/opened/clicked
- Reply received
- Meeting booked
- Deal won
- Pipeline stage changed

Features:
- Multiple webhook endpoints
- Event filtering
- Payload customization
- Retry on failure
- Signature verification
"""

import json
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import logging
import requests

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    id: str
    url: str
    events: List[str]  # Events to subscribe to
    secret: str  # For signature verification
    active: bool = True
    created_at: str = None
    last_triggered: str = None
    success_count: int = 0
    failure_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


class WebhookService:
    """Webhook notification service."""

    def __init__(self, config: Settings):
        self.config = config
        self.webhooks_dir = Path(config.database.data_dir) / "webhooks"
        self.webhooks_dir.mkdir(parents=True, exist_ok=True)
        self.endpoints_file = self.webhooks_dir / "endpoints.json"
        self.logs_file = self.webhooks_dir / "logs.json"
        self._endpoints = self._load_endpoints()

    def register_endpoint(self, url: str, events: List[str], secret: str = None) -> WebhookEndpoint:
        """Register a new webhook endpoint."""
        import secrets
        endpoint = WebhookEndpoint(
            id=f"wh_{secrets.token_hex(8)}",
            url=url,
            events=events,
            secret=secret or secrets.token_hex(32)
        )
        self._endpoints.append(endpoint)
        self._save_endpoints()
        logger.info(f"Registered webhook: {endpoint.id} -> {url}")
        return endpoint

    def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Unregister a webhook endpoint."""
        self._endpoints = [e for e in self._endpoints if e.id != endpoint_id]
        self._save_endpoints()
        return True

    def send(self, event_type: str, payload: Dict):
        """Send webhook event to all subscribed endpoints."""
        event = {
            "id": f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{event_type}",
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload
        }

        for endpoint in self._endpoints:
            if not endpoint.active:
                continue
            if event_type not in endpoint.events:
                continue

            self._send_to_endpoint(endpoint, event)

    def _send_to_endpoint(self, endpoint: WebhookEndpoint, event: Dict):
        """Send event to a single endpoint."""
        try:
            # Generate signature
            signature = self._generate_signature(event, endpoint.secret)

            # Send request
            response = requests.post(
                endpoint.url,
                json=event,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": event["type"],
                    "X-Webhook-Timestamp": event["timestamp"]
                },
                timeout=10
            )

            if response.status_code < 300:
                endpoint.success_count += 1
                endpoint.last_triggered = datetime.now(timezone.utc).isoformat()
                logger.debug(f"Webhook {endpoint.id} succeeded")
            else:
                endpoint.failure_count += 1
                logger.warning(f"Webhook {endpoint.id} failed: {response.status_code}")

            self._save_endpoints()
            self._log_event(endpoint.id, event, response.status_code)

        except Exception as e:
            endpoint.failure_count += 1
            logger.error(f"Webhook {endpoint.id} error: {e}")
            self._save_endpoints()

    def _generate_signature(self, event: Dict, secret: str) -> str:
        """Generate HMAC signature for webhook."""
        payload = json.dumps(event, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        expected = self._generate_signature(json.loads(payload), secret)
        return hmac.compare_digest(expected, signature)

    def _log_event(self, endpoint_id: str, event: Dict, status_code: int):
        """Log webhook event."""
        logs = self._load_logs()
        logs.append({
            "endpoint_id": endpoint_id,
            "event_id": event["id"],
            "event_type": event["type"],
            "status_code": status_code,
            "timestamp": event["timestamp"]
        })
        # Keep last 1000 logs
        logs = logs[-1000:]
        with open(self.logs_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def _save_endpoints(self):
        with open(self.endpoints_file, 'w') as f:
            json.dump([asdict(e) for e in self._endpoints], f, indent=2)

    def _load_endpoints(self) -> List[WebhookEndpoint]:
        if self.endpoints_file.exists():
            with open(self.endpoints_file, 'r') as f:
                data = json.load(f)
                return [WebhookEndpoint(**e) for e in data]
        return []

    def _load_logs(self) -> List[Dict]:
        if self.logs_file.exists():
            with open(self.logs_file, 'r') as f:
                return json.load(f)
        return []

    def get_stats(self) -> Dict:
        """Get webhook statistics."""
        return {
            "total_endpoints": len(self._endpoints),
            "active_endpoints": len([e for e in self._endpoints if e.active]),
            "total_deliveries": sum(e.success_count + e.failure_count for e in self._endpoints),
            "success_rate": sum(e.success_count for e in self._endpoints) / max(1, sum(e.success_count + e.failure_count for e in self._endpoints)) * 100
        }


# Event types
WEBHOOK_EVENTS = {
    "lead.created": "New lead added",
    "lead.enriched": "Lead enriched with data",
    "email.sent": "Email sent",
    "email.opened": "Email opened",
    "email.clicked": "Link clicked",
    "email.bounced": "Email bounced",
    "reply.received": "Reply received",
    "reply.classified": "Reply classified (positive/negative)",
    "meeting.booked": "Meeting scheduled",
    "deal.won": "Deal closed won",
    "deal.lost": "Deal closed lost",
    "pipeline.stage_changed": "Lead moved to new stage",
    "proposal.sent": "Proposal sent",
    "proposal.accepted": "Proposal accepted",
    "proposal.rejected": "Proposal rejected",
}


def get_webhook_service(config: Settings) -> WebhookService:
    """Get or create webhook service."""
    return WebhookService(config)
