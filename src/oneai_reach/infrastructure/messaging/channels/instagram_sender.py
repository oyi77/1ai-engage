"""Instagram DM sender using instagrapi with cookie-based session auth."""

import json
from datetime import datetime
from typing import Optional

from oneai_reach.infrastructure.logging import get_logger
from oneai_reach.infrastructure.messaging.channels.channel_config import ChannelConfig

logger = get_logger(__name__)

_CLIENTS: dict[str, object] = {}


def _get_client(wa_number_id: str) -> Optional["Client"]:
    from instagrapi import Client

    key = f"ig:{wa_number_id}"
    if key in _CLIENTS:
        return _CLIENTS[key]

    cfg = ChannelConfig("instagram", wa_number_id)
    cookies = cfg.get_cookies()
    if not cookies:
        return None

    sessionid = cookies.get("sessionid")
    if not sessionid:
        return None

    try:
        client = Client()
        session_data = cfg.load_session()
        if session_data.get("settings"):
            client.set_settings(session_data["settings"])

        client.login_by_sessionid(sessionid)

        settings = client.get_settings()
        username = client.username
        cfg.save_session({
            "valid": True,
            "username": username,
            "settings": settings,
            "last_check": datetime.now().isoformat(),
        })
        _CLIENTS[key] = client
        logger.info(f"Instagram connected: @{username} for {wa_number_id}")
        return client
    except Exception as e:
        logger.error(f"Instagram login failed for {wa_number_id}: {e}")
        cfg.save_session({"valid": False, "last_check": datetime.now().isoformat()})
        return None


class InstagramSender:
    def __init__(self, wa_number_id: str):
        self.wa_number_id = wa_number_id
        self.cfg = ChannelConfig("instagram", wa_number_id)

    def send(self, username: str, message: str) -> bool:
        client = _get_client(self.wa_number_id)
        if not client:
            logger.error(f"Instagram not connected for {self.wa_number_id}")
            return False

        try:
            user = client.user_info_by_username_v1(username)
            user_id = int(user.pk)
            client.direct_send(message, user_ids=[user_id])
            logger.info(f"Instagram DM sent to @{username} for {self.wa_number_id}")
            return True
        except Exception as e:
            logger.error(f"Instagram DM failed to @{username}: {e}")
            _CLIENTS.pop(f"ig:{self.wa_number_id}", None)
            return False

    def get_threads(self, limit: int = 20) -> list[dict]:
        client = _get_client(self.wa_number_id)
        if not client:
            return []

        try:
            threads = client.direct_threads(amount=limit)
            result = []
            for t in threads:
                msgs = client.direct_messages(t.id, amount=5)
                result.append({
                    "thread_id": t.id,
                    "users": [u.username for u in t.users],
                    "last_message": msgs[0].text if msgs else "",
                    "last_activity": str(t.last_activity_at) if t.last_activity_at else "",
                    "messages": [
                        {"id": m.id, "text": m.text, "sender": m.user_id, "timestamp": str(m.timestamp)}
                        for m in msgs
                    ],
                })
            return result
        except Exception as e:
            logger.error(f"Instagram get_threads failed: {e}")
            return []

    def test_connection(self, sessionid: str) -> dict:
        from instagrapi import Client

        try:
            client = Client()
            client.login_by_sessionid(sessionid)
            username = client.username
            settings = client.get_settings()
            self.cfg.save_session({
                "valid": True,
                "username": username,
                "settings": settings,
                "last_check": datetime.now().isoformat(),
            })
            _CLIENTS[f"ig:{self.wa_number_id}"] = client
            return {"success": True, "username": username}
        except Exception as e:
            self.cfg.save_session({"valid": False, "last_check": datetime.now().isoformat()})
            return {"success": False, "error": str(e)}
