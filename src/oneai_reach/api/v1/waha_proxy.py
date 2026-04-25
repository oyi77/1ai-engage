"""WAHA API proxy endpoints — pure forwarding layer to WAHA Plus server.

Proxies requests to WAHA for messages, media, presence, and labels.
No business logic here — that goes in feature-specific endpoints.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from oneai_reach.api.dependencies import verify_api_key
from oneai_reach.config.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/waha",
    tags=["waha-proxy"],
    dependencies=[Depends(verify_api_key)],
)

_client: httpx.AsyncClient | None = None


async def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client


async def _proxy(
    method: str,
    session: str,
    path: str,
    request: Request | None = None,
    params: dict | None = None,
) -> dict | list | str:
    settings = get_settings()
    waha_base = settings.waha.url.rstrip("/")
    url = f"{waha_base}/api/{session}/{path}" if path else f"{waha_base}/api/{session}"
    headers = {"X-Api-Key": settings.waha.api_key}

    client = await _get_client()
    body = await request.body() if request else None
    content_type = request.headers.get("content-type") if request else None

    try:
        req_headers = {**headers}
        if content_type:
            req_headers["Content-Type"] = content_type
        response = await client.request(
            method=method,
            url=url,
            headers=req_headers,
            content=body,
            params=params,
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={"error": "Session not found", "session": session},
            )
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text
    except httpx.ConnectError:
        raise HTTPException(
            status_code=502,
            detail={"error": "WAHA service unavailable"},
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )


# --- Messages ---

@router.get("/{session}/chats/{chat_id}/messages")
async def proxy_messages(
    session: str,
    chat_id: str,
    limit: int = 50,
    offset: int = 0,
    sort: str = "desc",
    downloadMedia: int = 0,
):
    params = {"limit": limit, "offset": offset, "sort": sort, "downloadMedia": downloadMedia}
    return await _proxy("GET", session, f"chats/{chat_id}/messages", params=params)


# --- Media Sending ---

@router.post("/{session}/sendImage")
async def proxy_send_image(session: str, request: Request):
    return await _proxy("POST", session, "sendImage", request=request)


@router.post("/{session}/sendFile")
async def proxy_send_file(session: str, request: Request):
    return await _proxy("POST", session, "sendFile", request=request)


@router.post("/{session}/sendVideo")
async def proxy_send_video(session: str, request: Request):
    return await _proxy("POST", session, "sendVideo", request=request)


@router.post("/{session}/sendVoice")
async def proxy_send_voice(session: str, request: Request):
    return await _proxy("POST", session, "sendVoice", request=request)


# --- Presence ---

@router.get("/{session}/presence")
async def proxy_get_presence(session: str):
    return await _proxy("GET", session, "presence")


@router.post("/{session}/presence")
async def proxy_subscribe_presence(session: str, request: Request):
    return await _proxy("POST", session, "presence", request=request)


# --- Labels ---

@router.get("/{session}/labels")
async def proxy_get_labels(session: str):
    return await _proxy("GET", session, "labels")


@router.post("/{session}/labels")
async def proxy_create_label(session: str, request: Request):
    return await _proxy("POST", session, "labels", request=request)


@router.put("/{session}/labels/{label_id}")
async def proxy_update_label(session: str, label_id: str, request: Request):
    return await _proxy("PUT", session, f"labels/{label_id}", request=request)


@router.delete("/{session}/labels/{label_id}")
async def proxy_delete_label(session: str, label_id: str):
    return await _proxy("DELETE", session, f"labels/{label_id}")