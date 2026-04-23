"""Channel management API — configure Instagram/Twitter auth, test connections."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from oneai_reach.api.dependencies import verify_api_key
from oneai_reach.infrastructure.messaging.channels.channel_config import ChannelConfig

router = APIRouter(
    prefix="/api/v1/channels",
    tags=["channels"],
    dependencies=[Depends(verify_api_key)],
)

SUPPORTED_CHANNELS = {
    "instagram": "Instagram (covers Threads DMs)",
    "twitter": "Twitter / X",
}


class ChannelStatusResponse(BaseModel):
    channels: Dict[str, Dict[str, Any]]


class ChannelCookiesRequest(BaseModel):
    cookies: Dict[str, str] = Field(..., description="Platform-specific cookies")


class ChannelEnableRequest(BaseModel):
    enabled: bool


class ChannelTestResponse(BaseModel):
    success: bool
    username: str = ""
    error: str = ""


@router.get("/{wa_number_id}", response_model=ChannelStatusResponse)
async def get_channel_status(wa_number_id: str) -> ChannelStatusResponse:
    channels = {}
    for ch_name, ch_label in SUPPORTED_CHANNELS.items():
        cfg = ChannelConfig(ch_name, wa_number_id)
        channels[ch_name] = {**cfg.get_status(), "label": ch_label}
    return ChannelStatusResponse(channels=channels)


@router.post("/{wa_number_id}/{channel}/cookies")
async def set_channel_cookies(
    wa_number_id: str,
    channel: str,
    body: ChannelCookiesRequest,
):
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(400, f"Unsupported channel: {channel}")
    cfg = ChannelConfig(channel, wa_number_id)
    cfg.set_cookies(body.cookies)
    return {"status": "saved", "channel": channel}


@router.patch("/{wa_number_id}/{channel}/enable")
async def toggle_channel(
    wa_number_id: str,
    channel: str,
    body: ChannelEnableRequest,
):
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(400, f"Unsupported channel: {channel}")
    cfg = ChannelConfig(channel, wa_number_id)
    cfg.set_enabled(body.enabled)
    return {"status": "updated", "channel": channel, "enabled": body.enabled}


@router.post("/{wa_number_id}/{channel}/test", response_model=ChannelTestResponse)
async def test_channel_connection(
    wa_number_id: str,
    channel: str,
):
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(400, f"Unsupported channel: {channel}")

    cfg = ChannelConfig(channel, wa_number_id)
    cookies = cfg.get_cookies()

    if channel == "instagram":
        from oneai_reach.infrastructure.messaging.channels.instagram_sender import InstagramSender
        sessionid = cookies.get("sessionid", "")
        if not sessionid:
            return ChannelTestResponse(success=False, error="No sessionid cookie provided")
        sender = InstagramSender(wa_number_id)
        result = sender.test_connection(sessionid)
        return ChannelTestResponse(**result)

    elif channel == "twitter":
        from oneai_reach.infrastructure.messaging.channels.twitter_sender import TwitterSender
        auth_token = cookies.get("auth_token", "")
        if not auth_token:
            return ChannelTestResponse(success=False, error="No auth_token cookie provided")
        sender = TwitterSender(wa_number_id)
        result = sender.test_connection(
            auth_token=auth_token,
            ct0=cookies.get("ct0", ""),
            twid=cookies.get("twid", ""),
        )
        return ChannelTestResponse(**result)

    return ChannelTestResponse(success=False, error="Unknown channel")


@router.post("/{wa_number_id}/{channel}/send")
async def send_channel_dm(
    wa_number_id: str,
    channel: str,
    body: Dict[str, str],
):
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(400, f"Unsupported channel: {channel}")

    username = body.get("username", "")
    message = body.get("message", "")
    if not username or not message:
        raise HTTPException(400, "username and message required")

    if channel == "instagram":
        from oneai_reach.infrastructure.messaging.channels.instagram_sender import InstagramSender
        sender = InstagramSender(wa_number_id)
        ok = sender.send(username, message)
    elif channel == "twitter":
        from oneai_reach.infrastructure.messaging.channels.twitter_sender import TwitterSender
        sender = TwitterSender(wa_number_id)
        ok = sender.send(username, message)
    else:
        ok = False

    if ok:
        return {"status": "sent", "channel": channel, "username": username}
    raise HTTPException(500, f"Failed to send {channel} DM to {username}")


@router.get("/{wa_number_id}/{channel}/threads")
async def get_channel_threads(
    wa_number_id: str,
    channel: str,
    limit: int = 20,
):
    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(400, f"Unsupported channel: {channel}")

    if channel == "instagram":
        from oneai_reach.infrastructure.messaging.channels.instagram_sender import InstagramSender
        sender = InstagramSender(wa_number_id)
        return {"threads": sender.get_threads(limit)}
    elif channel == "twitter":
        from oneai_reach.infrastructure.messaging.channels.twitter_sender import TwitterSender
        sender = TwitterSender(wa_number_id)
        return {"threads": sender.get_dm_threads(limit)}

    return {"threads": []}


@router.get("/{wa_number_id}/poll")
async def poll_dms(wa_number_id: str):
    from oneai_reach.infrastructure.messaging.channels.dm_poller import poll_instagram, poll_twitter
    ig_new = poll_instagram(wa_number_id)
    tw_new = poll_twitter(wa_number_id)
    return {
        "wa_number_id": wa_number_id,
        "instagram": {"new_count": len(ig_new), "messages": ig_new[:10]},
        "twitter": {"new_count": len(tw_new), "messages": tw_new[:10]},
    }


@router.post("/poll-all")
async def poll_all_dms():
    import sys, os
    _project = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    _scripts = os.path.join(_project, "scripts")
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)
    from state_manager import get_wa_numbers
    numbers = get_wa_numbers()
    wa_ids = [n.get("id", "") or n.get("session_name", "") for n in numbers]
    from oneai_reach.infrastructure.messaging.channels.dm_poller import poll_all
    new_messages = poll_all(wa_ids)
    return {
        "polled_count": len(wa_ids),
        "new_count": len(new_messages),
        "messages": new_messages[:20],
    }
