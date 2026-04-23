"""Inbound DM polling for Instagram and Twitter.

Periodically checks for new DMs on enabled channels and routes them
into the CS engine. Tracks seen message IDs in a JSON file to avoid
re-processing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from oneai_reach.infrastructure.logging import get_logger
from oneai_reach.infrastructure.messaging.channels.channel_config import ChannelConfig
from oneai_reach.infrastructure.messaging.channels.instagram_sender import InstagramSender
from oneai_reach.infrastructure.messaging.channels.twitter_sender import TwitterSender

logger = get_logger(__name__)

_SEEN_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "channels" / "_seen"


def _load_seen(channel: str, wa_number_id: str) -> set[str]:
    path = _SEEN_DIR / channel / f"{wa_number_id}.json"
    if path.exists():
        try:
            return set(json.loads(path.read_text()).get("ids", []))
        except Exception:
            pass
    return set()


def _save_seen(channel: str, wa_number_id: str, ids: set[str]) -> None:
    path = _SEEN_DIR / channel / f"{wa_number_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    keep = list(ids)[-500:]
    path.write_text(json.dumps({"ids": keep, "updated": datetime.now().isoformat()}))


def poll_instagram(wa_number_id: str, limit: int = 20) -> list[dict]:
    cfg = ChannelConfig("instagram", wa_number_id)
    if not cfg.get_enabled():
        return []

    sender = InstagramSender(wa_number_id)
    threads = sender.get_threads(limit)
    if not threads:
        return []

    seen = _load_seen("instagram", wa_number_id)
    new_messages = []

    for thread in threads:
        for msg in thread.get("messages", []):
            msg_id = msg.get("id", "")
            if msg_id and msg_id not in seen:
                new_messages.append({
                    "channel": "instagram",
                    "wa_number_id": wa_number_id,
                    "thread_id": thread.get("thread_id", ""),
                    "sender_user_id": str(msg.get("sender", "")),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "msg_id": msg_id,
                    "users": thread.get("users", []),
                })
                seen.add(msg_id)

    if new_messages:
        _save_seen("instagram", wa_number_id, seen)
        logger.info(f"Instagram poll: {len(new_messages)} new DMs for {wa_number_id}")

    return new_messages


def poll_twitter(wa_number_id: str, limit: int = 20) -> list[dict]:
    cfg = ChannelConfig("twitter", wa_number_id)
    if not cfg.get_enabled():
        return []

    sender = TwitterSender(wa_number_id)
    threads = sender.get_dm_threads(limit)
    if not threads:
        return []

    seen = _load_seen("twitter", wa_number_id)
    new_messages = []

    for thread in threads:
        for msg in thread.get("messages", []):
            msg_id = msg.get("id", "")
            if msg_id and msg_id not in seen:
                new_messages.append({
                    "channel": "twitter",
                    "wa_number_id": wa_number_id,
                    "thread_id": thread.get("thread_id", ""),
                    "sender_user_id": str(msg.get("sender", "")),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "msg_id": msg_id,
                    "users": thread.get("users", []),
                })
                seen.add(msg_id)

    if new_messages:
        _save_seen("twitter", wa_number_id, seen)
        logger.info(f"Twitter poll: {len(new_messages)} new DMs for {wa_number_id}")

    return new_messages


def poll_all(wa_number_ids: list[str]) -> list[dict]:
    all_new = []
    for wa_id in wa_number_ids:
        all_new.extend(poll_instagram(wa_id))
        all_new.extend(poll_twitter(wa_id))
    return all_new
