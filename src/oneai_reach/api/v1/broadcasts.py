"""Broadcast API for Phase C."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
import json

from oneai_reach.api.dependencies import verify_api_key, get_db_connection, get_db_path

router = APIRouter(tags=["broadcasts"], dependencies=[Depends(verify_api_key)])

class BroadcastList(BaseModel):
    id: int
    wa_number_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    filter_criteria: Optional[str] = None
    total_recipients: int = 0
    is_active: bool = True
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BroadcastListCreate(BaseModel):
    name: str
    description: Optional[str] = None
    filter_criteria: Optional[dict] = None
    wa_number_id: Optional[str] = None
    created_by: Optional[str] = None

class BroadcastListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter_criteria: Optional[dict] = None
    is_active: Optional[bool] = None

class BroadcastRecipient(BaseModel):
    id: int
    broadcast_list_id: int
    contact_id: Optional[int] = None
    lead_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class BroadcastSend(BaseModel):
    id: int
    broadcast_list_id: int
    wa_number_id: Optional[str] = None
    name: str
    subject: Optional[str] = None
    content: str
    channel: str = "email"
    total_recipients: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    failed_count: int = 0
    status: str = "draft"
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BroadcastSendCreate(BaseModel):
    broadcast_list_id: int
    name: str
    subject: Optional[str] = None
    content: str
    channel: str = "email"
    scheduled_at: Optional[str] = None
    created_by: Optional[str] = None

class BroadcastListsResponse(BaseModel):
    lists: List[BroadcastList]
    total: int

class BroadcastSendsResponse(BaseModel):
    sends: List[BroadcastSend]
    total: int

class BroadcastRecipientsResponse(BaseModel):
    recipients: List[BroadcastRecipient]
    total: int

class BroadcastStats(BaseModel):
    total_lists: int
    total_sends: int
    total_recipients: int
    sends_by_status: dict

@router.get("/api/v1/broadcast-lists", response_model=BroadcastListsResponse)
async def list_broadcast_lists(
    wa_number_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> BroadcastListsResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    conditions = ["1=1"]
    params = []
    
    if wa_number_id:
        conditions.append("wa_number_id = ?")
        params.append(wa_number_id)
    if is_active is not None:
        conditions.append("is_active = ?")
        params.append(1 if is_active else 0)
    
    where_clause = " AND ".join(conditions)
    
    cursor.execute(f"""
        SELECT id, wa_number_id, name, description, filter_criteria, total_recipients,
               is_active, created_by, created_at, updated_at
        FROM broadcast_lists
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, [*params, limit, offset])
    
    rows = cursor.fetchall()
    
    cursor.execute(f"SELECT COUNT(*) FROM broadcast_lists WHERE {where_clause}", params)
    total = cursor.fetchone()[0]
    
    lists = [BroadcastList(**dict(row)) for row in rows]
    return BroadcastListsResponse(lists=lists, total=total)

@router.post("/api/v1/broadcast-lists", response_model=dict)
async def create_broadcast_list(list_data: BroadcastListCreate) -> dict:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    filter_criteria_json = json.dumps(list_data.filter_criteria) if list_data.filter_criteria else None
    
    cursor.execute("""
        INSERT INTO broadcast_lists (wa_number_id, name, description, filter_criteria, created_by)
        VALUES (?, ?, ?, ?, ?)
    """, (list_data.wa_number_id, list_data.name, list_data.description, filter_criteria_json, list_data.created_by))
    
    list_id = cursor.lastrowid
    conn.commit()
    
    return {"status": "created", "list_id": list_id}

@router.get("/api/v1/broadcast-lists/{list_id}/recipients", response_model=BroadcastRecipientsResponse)
async def get_broadcast_recipients(list_id: int) -> BroadcastRecipientsResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, broadcast_list_id, contact_id, lead_id, phone, email
        FROM broadcast_list_recipients
        WHERE broadcast_list_id = ?
    """, (list_id,))
    
    rows = cursor.fetchall()
    
    recipients = [BroadcastRecipient(**dict(row)) for row in rows]
    return BroadcastRecipientsResponse(recipients=recipients, total=len(recipients))

@router.post("/api/v1/broadcast-lists/{list_id}/recipients")
async def add_recipients_to_list(list_id: int, recipients: List[dict]) -> dict:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    added = 0
    for r in recipients:
        try:
            cursor.execute("""
                INSERT INTO broadcast_list_recipients (broadcast_list_id, contact_id, lead_id, phone, email)
                VALUES (?, ?, ?, ?, ?)
            """, (list_id, r.get("contact_id"), r.get("lead_id"), r.get("phone"), r.get("email")))
            added += 1
        except sqlite3.IntegrityError:
            pass
    
    cursor.execute("""
        UPDATE broadcast_lists SET total_recipients = (SELECT COUNT(*) FROM broadcast_list_recipients WHERE broadcast_list_id = ?)
        WHERE id = ?
    """, (list_id, list_id))
    
    conn.commit()
    
    return {"status": "added", "count": added}

@router.get("/api/v1/broadcast-sends", response_model=BroadcastSendsResponse)
async def list_broadcast_sends(
    broadcast_list_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> BroadcastSendsResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    conditions = ["1=1"]
    params = []
    
    if broadcast_list_id:
        conditions.append("broadcast_list_id = ?")
        params.append(broadcast_list_id)
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    where_clause = " AND ".join(conditions)
    
    cursor.execute(f"""
        SELECT id, broadcast_list_id, wa_number_id, name, subject, content, channel,
               total_recipients, sent_count, delivered_count, opened_count, clicked_count, failed_count,
               status, scheduled_at, started_at, completed_at, created_by, created_at, updated_at
        FROM broadcast_sends
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, [*params, limit, offset])
    
    rows = cursor.fetchall()
    
    cursor.execute(f"SELECT COUNT(*) FROM broadcast_sends WHERE {where_clause}", params)
    total = cursor.fetchone()[0]
    
    sends = [BroadcastSend(**dict(row)) for row in rows]
    return BroadcastSendsResponse(sends=sends, total=total)

@router.post("/api/v1/broadcast-sends", response_model=dict)
async def create_broadcast_send(send: BroadcastSendCreate) -> dict:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    # Get wa_number_id from broadcast list
    cursor.execute("SELECT wa_number_id FROM broadcast_lists WHERE id = ?", (send.broadcast_list_id,))
    row = cursor.fetchone()
    if not row:
            raise HTTPException(status_code=404, detail="Broadcast list not found")
    
    wa_number_id = row[0]
    
    # Get total recipients
    cursor.execute("SELECT COUNT(*) FROM broadcast_list_recipients WHERE broadcast_list_id = ?", (send.broadcast_list_id,))
    total_recipients = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT INTO broadcast_sends (broadcast_list_id, wa_number_id, name, subject, content,
                                      channel, total_recipients, scheduled_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (send.broadcast_list_id, wa_number_id, send.name, send.subject, send.content,
          send.channel, total_recipients, send.scheduled_at, send.created_by))
    
    send_id = cursor.lastrowid
    conn.commit()
    
    return {"status": "created", "send_id": send_id, "total_recipients": total_recipients}

@router.post("/api/v1/broadcast-sends/{send_id}/start")
async def start_broadcast(send_id: int) -> dict:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
        UPDATE broadcast_sends 
        SET status = 'sending', started_at = ?
        WHERE id = ? AND status = 'scheduled'
    """, (now, send_id))
    
    if cursor.rowcount == 0:
            raise HTTPException(status_code=400, detail="Broadcast not found or not in scheduled state")
    
    conn.commit()
    
    return {"status": "started", "send_id": send_id}

@router.get("/api/v1/broadcasts/stats/overview", response_model=BroadcastStats)
async def get_broadcast_stats() -> BroadcastStats:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM broadcast_lists")
    total_lists = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM broadcast_sends")
    total_sends = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM broadcast_list_recipients")
    total_recipients = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM broadcast_sends GROUP BY status")
    sends_by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    
    return BroadcastStats(
        total_lists=total_lists,
        total_sends=total_sends,
        total_recipients=total_recipients,
        sends_by_status=sends_by_status
    )
