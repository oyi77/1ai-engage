"""Scheduled messages API for Phase C."""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlite3

from oneai_reach.api.dependencies import verify_api_key, get_db_connection, get_db_path

router = APIRouter(tags=["scheduled-messages"], dependencies=[Depends(verify_api_key)])

class ScheduledMessage(BaseModel):
    id: int
    contact_id: Optional[int] = None
    conversation_id: Optional[int] = None
    wa_number_id: Optional[str] = None
    lead_id: Optional[str] = None
    channel: str = "email"
    message_type: str = "text"
    content: str
    subject: Optional[str] = None
    template_id: Optional[int] = None
    template_variables: Optional[str] = None
    scheduled_at: str
    timezone: str = "Asia/Jakarta"
    status: str = "pending"
    sent_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ScheduledMessageCreate(BaseModel):
    contact_id: Optional[int] = None
    conversation_id: Optional[int] = None
    lead_id: Optional[str] = None
    channel: str = "email"
    message_type: str = "text"
    content: str
    subject: Optional[str] = None
    template_id: Optional[int] = None
    template_variables: Optional[dict] = None
    scheduled_at: str
    timezone: str = "Asia/Jakarta"
    created_by: Optional[str] = None

class ScheduledMessageUpdate(BaseModel):
    content: Optional[str] = None
    subject: Optional[str] = None
    scheduled_at: Optional[str] = None
    status: Optional[str] = None

class MessagesResponse(BaseModel):
    messages: List[ScheduledMessage]
    total: int

class MessageResponse(BaseModel):
    message: ScheduledMessage

@router.get("/api/v1/scheduled-messages", response_model=MessagesResponse)
async def list_scheduled_messages(
    contact_id: Optional[int] = None,
    status: Optional[str] = None,
    scheduled_before: Optional[str] = None,
    scheduled_after: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> MessagesResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        conditions = ["1=1"]
        params = []
    
        if contact_id:
            conditions.append("contact_id = ?")
            params.append(contact_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if scheduled_before:
            conditions.append("scheduled_at <= ?")
            params.append(scheduled_before)
        if scheduled_after:
            conditions.append("scheduled_at >= ?")
            params.append(scheduled_after)
    
        where_clause = " AND ".join(conditions)
    
        cursor.execute(f"""
            SELECT id, contact_id, conversation_id, wa_number_id, lead_id, channel, message_type,
                   content, subject, template_id, template_variables, scheduled_at, timezone, status,
                   sent_at, error_message, retry_count, max_retries, created_by, created_at, updated_at
            FROM scheduled_messages
            WHERE {where_clause}
            ORDER BY scheduled_at DESC
            LIMIT ? OFFSET ?
        """, [*params, limit, offset])
    
        rows = cursor.fetchall()
    
        cursor.execute(f"SELECT COUNT(*) FROM scheduled_messages WHERE {where_clause}", params)
        total = cursor.fetchone()[0]
    
        messages = [ScheduledMessage(**dict(row)) for row in rows]
        return MessagesResponse(messages=messages, total=total)

@router.post("/api/v1/scheduled-messages", response_model=MessageResponse)
async def create_scheduled_message(msg: ScheduledMessageCreate) -> MessageResponse:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
        # Get wa_number_id from conversation if provided
        wa_number_id = None
        if msg.conversation_id:
            cursor.execute("SELECT wa_number_id FROM conversations WHERE id = ?", (msg.conversation_id,))
            row = cursor.fetchone()
            if row:
                wa_number_id = row[0]
    
        template_vars_json = None
        if msg.template_variables:
            import json
            template_vars_json = json.dumps(msg.template_variables)
    
        cursor.execute("""
            INSERT INTO scheduled_messages (contact_id, conversation_id, wa_number_id, lead_id, channel,
                                           message_type, content, subject, template_id, template_variables,
                                           scheduled_at, timezone, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg.contact_id, msg.conversation_id, wa_number_id, msg.lead_id, msg.channel,
              msg.message_type, msg.content, msg.subject, msg.template_id, template_vars_json,
              msg.scheduled_at, msg.timezone, msg.created_by))
    
        msg_id = cursor.lastrowid
        conn.commit()
    
        return MessageResponse(message=ScheduledMessage(
            id=msg_id,
            contact_id=msg.contact_id,
            conversation_id=msg.conversation_id,
            wa_number_id=wa_number_id,
            lead_id=msg.lead_id,
            channel=msg.channel,
            message_type=msg.message_type,
            content=msg.content,
            subject=msg.subject,
            template_id=msg.template_id,
            scheduled_at=msg.scheduled_at,
            created_by=msg.created_by
        ))

@router.get("/api/v1/scheduled-messages/{message_id}", response_model=MessageResponse)
async def get_scheduled_message(message_id: int) -> MessageResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT id, contact_id, conversation_id, wa_number_id, lead_id, channel, message_type,
                   content, subject, template_id, template_variables, scheduled_at, timezone, status,
                   sent_at, error_message, retry_count, max_retries, created_by, created_at, updated_at
            FROM scheduled_messages WHERE id = ?
        """, (message_id,))
    
        row = cursor.fetchone()
    
        if not row:
            raise HTTPException(status_code=404, detail="Message not found")
    
        return MessageResponse(message=ScheduledMessage(**dict(row)))

@router.patch("/api/v1/scheduled-messages/{message_id}", response_model=MessageResponse)
async def update_scheduled_message(message_id: int, update: ScheduledMessageUpdate) -> MessageResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        cursor.execute("SELECT id FROM scheduled_messages WHERE id = ?", (message_id,))
        if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Message not found")
    
        fields = []
        params = []
    
        if update.content is not None:
            fields.append("content = ?")
            params.append(update.content)
        if update.subject is not None:
            fields.append("subject = ?")
            params.append(update.subject)
        if update.scheduled_at is not None:
            fields.append("scheduled_at = ?")
            params.append(update.scheduled_at)
        if update.status is not None:
            fields.append("status = ?")
            params.append(update.status)
    
        if not fields:
                raise HTTPException(status_code=400, detail="No fields to update")
    
        fields.append("updated_at = datetime('now')")
        params.append(message_id)
    
        cursor.execute(f"UPDATE scheduled_messages SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
    
        cursor.execute("""
            SELECT id, contact_id, conversation_id, wa_number_id, lead_id, channel, message_type,
                   content, subject, template_id, template_variables, scheduled_at, timezone, status,
                   sent_at, error_message, retry_count, max_retries, created_by, created_at, updated_at
            FROM scheduled_messages WHERE id = ?
        """, (message_id,))
    
        row = cursor.fetchone()
    
        return MessageResponse(message=ScheduledMessage(**dict(row)))

@router.delete("/api/v1/scheduled-messages/{message_id}")
async def delete_scheduled_message(message_id: int):
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
        cursor.execute("DELETE FROM scheduled_messages WHERE id = ? AND status IN ('pending', 'cancelled')", (message_id,))
    
        if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Message not found or cannot delete sent/processing message")
    
        conn.commit()
    
        return {"status": "deleted", "message_id": message_id}

@router.post("/api/v1/scheduled-messages/process")
async def process_due_messages() -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        now = datetime.now(timezone.utc).isoformat()
    
        cursor.execute("""
            SELECT id, channel, content, subject, contact_id, conversation_id
            FROM scheduled_messages
            WHERE status = 'pending' AND scheduled_at <= ?
        """, (now,))
    
        messages = cursor.fetchall()
        processed = 0
        failed = 0
    
        for msg in messages:
            try:
                cursor.execute("UPDATE scheduled_messages SET status = 'processing' WHERE id = ?", (msg["id"],))
                conn.commit()
            
                # Here would be the actual sending logic
                # For now, just mark as sent
                cursor.execute("""
                    UPDATE scheduled_messages 
                    SET status = 'sent', sent_at = ?
                    WHERE id = ?
                """, (now, msg["id"]))
                conn.commit()
                processed += 1
            except Exception as e:
                cursor.execute("""
                    UPDATE scheduled_messages 
                    SET status = 'failed', error_message = ?, retry_count = retry_count + 1
                    WHERE id = ?
                """, (str(e), msg["id"]))
                conn.commit()
                failed += 1
    
        return {"processed": processed, "failed": failed, "total": len(messages)}

@router.get("/api/v1/scheduled-messages/stats/overview")
async def get_scheduled_stats() -> dict:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing,
                COUNT(*) as total
            FROM scheduled_messages
        """)
    
        row = cursor.fetchone()
    
        return {
            "pending": row[0],
            "sent": row[1],
            "failed": row[2],
            "processing": row[3],
            "total": row[4]
        }
