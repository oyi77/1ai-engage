"""Telegram DM sender using Telethon (MTProto user account).

Auth via session string stored in channel config.
Supports sending, polling inbound, and connection testing.
"""

import asyncio
from typing import Optional

from oneai_reach.infrastructure.logging import get_logger

logger = get_logger(__name__)

_CLIENTS: dict[str, object] = {}


def _run_async(coro):
    """Run async coroutine in sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an async context — create a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


async def _get_client(channel_id: str, config: dict):
    """Get or create a Telethon client for the channel."""
    from telethon import TelegramClient

    key = f"tg:{channel_id}"
    if key in _CLIENTS:
        client = _CLIENTS[key]
        if client.is_connected():
            return client
        # Stale client, remove
        _CLIENTS.pop(key, None)

    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    session_string = config.get("session_string")

    if not api_id or not api_hash or not session_string:
        raise ValueError("Telegram config requires api_id, api_hash, and session_string")

    client = TelegramClient(
        StringSession(session_string),
        int(api_id),
        api_hash,
    )
    await client.connect()

    if not await client.is_user_authorized():
        raise ValueError("Telegram session expired — re-authentication required")

    _CLIENTS[key] = client
    return client


class TelegramSender:
    """Send Telegram DMs via Telethon."""

    def __init__(self, channel_id: str, config: dict):
        self.channel_id = channel_id
        self.config = config

    async def _send_async(self, username_or_phone: str, message: str) -> bool:
        client = await _get_client(self.channel_id, self.config)
        try:
            entity = await client.get_entity(username_or_phone)
            await client.send_message(entity, message)
            logger.info(f"Telegram DM sent to {username_or_phone} via {self.channel_id}")
            return True
        except Exception as e:
            logger.error(f"Telegram DM failed to {username_or_phone}: {e}")
            _CLIENTS.pop(f"tg:{self.channel_id}", None)
            return False

    def send(self, username_or_phone: str, message: str) -> bool:
        return _run_async(self._send_async(username_or_phone, message))

    def test_connection(self) -> dict:
        async def _test():
            try:
                client = await _get_client(self.channel_id, self.config)
                me = await client.get_me()
                return {"success": True, "username": me.username or str(me.id)}
            except Exception as e:
                return {"success": False, "error": str(e)}
        return _run_async(_test())

    def get_threads(self, limit: int = 20) -> list[dict]:
        async def _get():
            try:
                client = await _get_client(self.channel_id, self.config)
                dialogs = await client.get_dialogs(limit=limit)
                result = []
                for d in dialogs:
                    if d.is_user and not d.entity.bot:
                        messages = await client.get_messages(d.entity, limit=5)
                        result.append({
                            "thread_id": str(d.entity.id),
                            "users": [d.name],
                            "last_message": messages[0].text if messages else "",
                            "messages": [
                                {"id": str(m.id), "text": m.text or "", "sender": str(m.sender_id), "timestamp": str(m.date)}
                                for m in messages
                            ],
                        })
                return result
            except Exception as e:
                logger.error(f"Telegram get_threads failed: {e}")
                return []
        return _run_async(_get())

    def poll_inbound(self, limit: int = 20) -> list[dict]:
        """Poll for recent inbound DMs."""
        async def _poll():
            try:
                client = await _get_client(self.channel_id, self.config)
                me = await client.get_me()
                dialogs = await client.get_dialogs(limit=50)
                messages = []
                for d in dialogs:
                    if d.is_user and not d.entity.bot:
                        msgs = await client.get_messages(d.entity, limit=limit)
                        for m in msgs:
                            if m.sender_id != me.id and m.text:
                                messages.append({
                                    "channel": "telegram",
                                    "channel_id": self.channel_id,
                                    "thread_id": str(d.entity.id),
                                    "sender_user_id": str(m.sender_id),
                                    "text": m.text,
                                    "timestamp": str(m.date),
                                    "msg_id": str(m.id),
                                    "users": [d.name],
                                })
                return messages[:limit]
            except Exception as e:
                logger.error(f"Telegram poll failed: {e}")
                return []
        return _run_async(_poll())

    def disconnect(self):
        async def _disconnect():
            client = _CLIENTS.pop(f"tg:{self.channel_id}", None)
            if client:
                await client.disconnect()
        try:
            _run_async(_disconnect())
        except Exception:
            pass


# Telethon StringSession for storing session as string
try:
    from telethon.sessions import StringSession
except ImportError:
    pass
