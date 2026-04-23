"""Twitter/X DM sender using tweety-ns with cookie-based auth."""

import json
from datetime import datetime
from typing import Optional

from oneai_reach.infrastructure.logging import get_logger
from oneai_reach.infrastructure.messaging.channels.channel_config import ChannelConfig

logger = get_logger(__name__)

_TWITTER_CLIENTS: dict[str, object] = {}


def _get_client(wa_number_id: str) -> Optional["Twitter"]:
    from tweety import Twitter

    key = f"tw:{wa_number_id}"
    if key in _TWITTER_CLIENTS:
        return _TWITTER_CLIENTS[key]

    cfg = ChannelConfig("twitter", wa_number_id)
    cookies = cfg.get_cookies()
    if not cookies:
        return None

    auth_token = cookies.get("auth_token")
    ct0 = cookies.get("ct0")
    if not auth_token:
        return None

    try:
        session_path = cfg.dir / "twitter_session"
        app = Twitter(str(session_path))

        if ct0:
            from tweety.cookies import Cookies
            cookies_obj = Cookies()
            cookies_obj.set_cookies({
                "auth_token": auth_token,
                "ct0": ct0,
                "twid": cookies.get("twid", ""),
            })
            app._session.cookies.update(cookies_obj.get_dict())

        app.session.load_auth_token(auth_token)

        me = app.user
        if me:
            cfg.save_session({
                "valid": True,
                "username": me.username,
                "last_check": datetime.now().isoformat(),
            })
            _TWITTER_CLIENTS[key] = app
            logger.info(f"Twitter connected: @{me.username} for {wa_number_id}")
            return app
        else:
            raise Exception("Could not verify Twitter session")
    except Exception as e:
        logger.error(f"Twitter login failed for {wa_number_id}: {e}")
        cfg.save_session({"valid": False, "last_check": datetime.now().isoformat()})
        return None


class TwitterSender:
    def __init__(self, wa_number_id: str):
        self.wa_number_id = wa_number_id
        self.cfg = ChannelConfig("twitter", wa_number_id)

    def send(self, username: str, message: str) -> bool:
        client = _get_client(self.wa_number_id)
        if not client:
            logger.error(f"Twitter not connected for {self.wa_number_id}")
            return False

        try:
            user = client.get_user_info(username)
            client.send_message(user.id, message)
            logger.info(f"Twitter DM sent to @{username} for {self.wa_number_id}")
            return True
        except Exception as e:
            logger.error(f"Twitter DM failed to @{username}: {e}")
            _TWITTER_CLIENTS.pop(f"tw:{self.wa_number_id}", None)
            return False

    def get_dm_threads(self, limit: int = 20) -> list[dict]:
        client = _get_client(self.wa_number_id)
        if not client:
            return []

        try:
            dm_threads = client.get_dm_threads(limit=limit)
            result = []
            for thread in dm_threads:
                result.append({
                    "thread_id": str(thread.id),
                    "users": [u.username for u in thread.users] if hasattr(thread, 'users') else [],
                    "last_message": thread.messages[0].text if thread.messages else "",
                    "messages": [
                        {"id": str(m.id), "text": m.text, "sender": str(m.sender_id), "timestamp": str(m.created_at)}
                        for m in (thread.messages or [])[:5]
                    ],
                })
            return result
        except Exception as e:
            logger.error(f"Twitter get_dm_threads failed: {e}")
            return []

    def test_connection(self, auth_token: str, ct0: str = "", twid: str = "") -> dict:
        from tweety import Twitter

        try:
            session_path = self.cfg.dir / "twitter_test_session"
            app = Twitter(str(session_path))

            if ct0:
                from tweety.cookies import Cookies
                cookies_obj = Cookies()
                cookies_obj.set_cookies({
                    "auth_token": auth_token,
                    "ct0": ct0,
                    "twid": twid,
                })
                app._session.cookies.update(cookies_obj.get_dict())

            app.session.load_auth_token(auth_token)
            me = app.user

            if me:
                self.cfg.save_session({
                    "valid": True,
                    "username": me.username,
                    "last_check": datetime.now().isoformat(),
                })
                _TWITTER_CLIENTS[f"tw:{self.wa_number_id}"] = app
                return {"success": True, "username": me.username}
            else:
                raise Exception("Could not verify Twitter session")
        except Exception as e:
            self.cfg.save_session({"valid": False, "last_check": datetime.now().isoformat()})
            return {"success": False, "error": str(e)}
