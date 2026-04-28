"""Revenue attribution tracking."""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from oneai_reach.config.settings import Settings
from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

class AttributionModel(Enum):
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"

@dataclass
class RevenueEvent:
    id: str
    lead_id: str
    amount_cents: int
    currency: str
    event_type: str
    campaign_id: Optional[str]
    channel: str
    timestamp: str

@dataclass
class Touchpoint:
    id: str
    lead_id: str
    channel: str
    campaign_id: str
    timestamp: str
    interaction_type: str
    weight: float = 0.0

class RevenueAttribution:
    def __init__(self, config: Settings):
        self.config = config
        self.revenue_dir = Path(config.database.data_dir) / "revenue"
        self.revenue_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.revenue_dir / "events.json"
        self.touchpoints_file = self.revenue_dir / "touchpoints.json"

    def record_revenue(self, lead_id: str, amount_cents: int, currency: str, event_type: str, campaign_id: str = None, channel: str = "email") -> RevenueEvent:
        event = RevenueEvent(id=f"rev_{datetime.now().strftime('%Y%m%d%H%M%S')}_{lead_id}", lead_id=lead_id, amount_cents=amount_cents, currency=currency, event_type=event_type, campaign_id=campaign_id, channel=channel, timestamp=datetime.now(timezone.utc).isoformat())
        self._save_event(event)
        logger.info(f"Recorded revenue: ${amount_cents/100:.2f} from {lead_id}")
        return event

    def record_touchpoint(self, lead_id: str, channel: str, campaign_id: str, interaction_type: str):
        tp = Touchpoint(id=f"tp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{lead_id}", lead_id=lead_id, channel=channel, campaign_id=campaign_id, timestamp=datetime.now(timezone.utc).isoformat(), interaction_type=interaction_type)
        self._save_touchpoint(tp)

    def get_campaign_roi(self, campaign_id: str) -> Dict:
        events = [RevenueEvent(**e) for e in self._load_events() if e.get("campaign_id") == campaign_id]
        touchpoints = [Touchpoint(**t) for t in self._load_touchpoints() if t.get("campaign_id") == campaign_id]
        total_revenue = sum(e.amount_cents for e in events)
        total_cost = len(touchpoints) * 100
        roi = ((total_revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        return {"campaign_id": campaign_id, "total_revenue_cents": total_revenue, "roi_percent": roi, "touchpoints": len(touchpoints), "conversions": len(events)}

    def get_channel_performance(self, days: int = 30) -> Dict:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        events = [RevenueEvent(**e) for e in self._load_events() if datetime.fromisoformat(e.timestamp) > cutoff]
        touchpoints = [Touchpoint(**t) for t in self._load_touchpoints() if datetime.fromisoformat(t.timestamp) > cutoff]
        stats = {}
        for e in events:
            if e.channel not in stats: stats[e.channel] = {"revenue": 0, "conversions": 0, "touchpoints": 0}
            stats[e.channel]["revenue"] += e.amount_cents
            stats[e.channel]["conversions"] += 1
        for t in touchpoints:
            if t.channel not in stats: stats[t.channel] = {"revenue": 0, "conversions": 0, "touchpoints": 0}
            stats[t.channel]["touchpoints"] += 1
        for ch in stats:
            cost = stats[ch]["touchpoints"] * 100
            stats[ch]["roi"] = ((stats[ch]["revenue"] - cost) / cost) * 100 if cost > 0 else 0
        return stats

    def _save_event(self, event: RevenueEvent):
        events = self._load_events()
        events.append(asdict(event))
        with open(self.events_file, 'w') as f: json.dump(events, f, indent=2)

    def _save_touchpoint(self, tp: Touchpoint):
        tps = self._load_touchpoints()
        tps.append(asdict(tp))
        with open(self.touchpoints_file, 'w') as f: json.dump(tps, f, indent=2)

    def _load_events(self) -> List[Dict]:
        return json.load(open(self.events_file)) if self.events_file.exists() else []

    def _load_touchpoints(self) -> List[Dict]:
        return json.load(open(self.touchpoints_file)) if self.touchpoints_file.exists() else []

def get_revenue_attribution(config: Settings) -> RevenueAttribution:
    return RevenueAttribution(config)
