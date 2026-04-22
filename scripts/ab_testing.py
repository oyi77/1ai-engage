import json
import os
import random
from pathlib import Path
from typing import Optional

from config import DATA_DIR

_EXPERIMENTS_DIR = Path(DATA_DIR) / "experiments"


class ProposalABTest:
    def __init__(self, experiments_dir: str = None):
        self.base_dir = Path(experiments_dir) if experiments_dir else _EXPERIMENTS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _stats_path(self, service: str, variant_type: str) -> Path:
        d = self.base_dir / service
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{variant_type}.json"

    def _load_stats(self, service: str, variant_type: str) -> dict:
        path = self._stats_path(service, variant_type)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}

    def _save_stats(self, service: str, variant_type: str, stats: dict):
        path = self._stats_path(service, variant_type)
        with open(path, "w") as f:
            json.dump(stats, f, indent=2)

    def select_variant(self, service: str, variant_type: str, vertical: str = "") -> str:
        """Select a variant using Thompson Sampling (beta distribution approximation)."""
        stats = self._load_stats(service, variant_type)
        variants = list(stats.keys()) if stats else []

        if not variants:
            return f"{variant_type}_default"

        best_variant = None
        best_sample = -1
        for v in variants:
            s = stats[v]
            sent = s.get("sent", 0)
            replied = s.get("replied", 0)
            alpha = replied + 1
            beta_param = sent - replied + 1
            sample = random.betavariate(alpha, beta_param)
            if sample > best_sample:
                best_sample = sample
                best_variant = v

        return best_variant or f"{variant_type}_default"

    def record_outcome(self, service: str, variant_type: str, variant: str, outcome: str):
        """Record an outcome (sent, replied, won, lost) for a variant."""
        stats = self._load_stats(service, variant_type)
        if variant not in stats:
            stats[variant] = {"sent": 0, "replied": 0, "won": 0, "lost": 0}

        if outcome == "sent":
            stats[variant]["sent"] += 1
        elif outcome == "replied":
            stats[variant]["replied"] += 1
        elif outcome == "won":
            stats[variant]["won"] += 1
        elif outcome == "lost":
            stats[variant]["lost"] += 1

        self._save_stats(service, variant_type, stats)

    def get_winner(self, service: str, variant_type: str, min_sends: int = 50) -> Optional[str]:
        """Get the winning variant if statistical significance is reached."""
        stats = self._load_stats(service, variant_type)
        if not stats:
            return None

        qualified = {v: s for v, s in stats.items() if s.get("sent", 0) >= min_sends}
        if len(qualified) < 2:
            return None

        best = max(qualified.items(), key=lambda x: x[1].get("replied", 0) / max(x[1].get("sent", 1), 1))
        return best[0]
