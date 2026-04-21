#!/usr/bin/env python3
"""
Backward compatibility shim for cs_engine.py
Delegates to FastAPI application for message handling.
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import requests

_root = Path(__file__).resolve().parent.parent

FASTAPI_BASE_URL = "http://localhost:8000"


def handle_inbound_message(
    session_name: str,
    sender: str,
    message: str,
    message_type: str = "chat",
    media_url: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/v1/webhooks/waha/message",
            json={
                "event": "message",
                "session": session_name,
                "payload": {
                    "from": sender,
                    "body": message,
                    "type": message_type,
                    "fromMe": False,
                },
            },
            timeout=30,
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "response": data.get("response"),
                "conversation_id": data.get("conversation_id"),
            }
        else:
            return {
                "status": "error",
                "error": f"API returned {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def process_message(
    session_name: str,
    sender: str,
    message: str,
) -> Optional[str]:
    result = handle_inbound_message(session_name, sender, message)
    return result.get("response")
