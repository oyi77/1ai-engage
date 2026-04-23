"""Channel configuration storage for multi-platform auth cookies."""

import json
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "channels"


class ChannelConfig:
    def __init__(self, channel: str, wa_number_id: str):
        self.channel = channel
        self.wa_number_id = wa_number_id
        self.dir = _ROOT / channel / wa_number_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.session_path = self.dir / "session.json"

    def load_config(self) -> dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {}

    def save_config(self, config: dict) -> None:
        self.config_path.write_text(json.dumps(config, indent=2))

    def load_session(self) -> dict:
        if self.session_path.exists():
            return json.loads(self.session_path.read_text())
        return {}

    def save_session(self, session: dict) -> None:
        self.session_path.write_text(json.dumps(session, indent=2))

    def get_enabled(self) -> bool:
        return self.load_config().get("enabled", False)

    def set_enabled(self, enabled: bool) -> None:
        cfg = self.load_config()
        cfg["enabled"] = enabled
        self.save_config(cfg)

    def get_cookies(self) -> dict:
        return self.load_config().get("cookies", {})

    def set_cookies(self, cookies: dict) -> None:
        cfg = self.load_config()
        cfg["cookies"] = cookies
        self.save_config(cfg)

    def get_status(self) -> dict:
        cfg = self.load_config()
        session = self.load_session()
        return {
            "channel": self.channel,
            "wa_number_id": self.wa_number_id,
            "enabled": cfg.get("enabled", False),
            "connected": bool(session.get("valid", False)),
            "username": session.get("username", ""),
            "last_check": session.get("last_check", ""),
        }

    def list_all_channels(wa_number_id: str) -> dict:
        result = {}
        for channel_dir in _ROOT.iterdir():
            if channel_dir.is_dir():
                cfg = ChannelConfig(channel_dir.name, wa_number_id)
                result[channel_dir.name] = cfg.get_status()
        for ch in ["instagram", "twitter"]:
            if ch not in result:
                cfg = ChannelConfig(ch, wa_number_id)
                result[ch] = cfg.get_status()
        return result
