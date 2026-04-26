"""Email templates API for Phase C."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlite3

from oneai_reach.api.dependencies import verify_api_key, get_db_connection, get_db_path

router = APIRouter(tags=["email-templates"], dependencies=[Depends(verify_api_key)])

class EmailTemplate(BaseModel):
    id: int
    wa_number_id: Optional[str] = None
    name: str
    subject: str
    body: str
    category: str = "general"
    variables: Optional[str] = None
    is_predefined: bool = False
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    category: str = "general"
    variables: Optional[str] = None

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    category: Optional[str] = None
    variables: Optional[str] = None
    is_active: Optional[bool] = None

class TemplatesResponse(BaseModel):
    templates: List[EmailTemplate]

class TemplateResponse(BaseModel):
    template: EmailTemplate

@router.get("/api/v1/email-templates", response_model=TemplatesResponse)
async def list_templates(
    wa_number_id: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> TemplatesResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    conditions = ["is_active = 1"]
    params = []
    
    if wa_number_id:
        conditions.append("(wa_number_id = ? OR wa_number_id IS NULL)")
        params.append(wa_number_id)
    if category:
        conditions.append("category = ?")
        params.append(category)
    if search:
        conditions.append("(name LIKE ? OR subject LIKE ? OR body LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term] * 3)
    
    where_clause = " AND ".join(conditions)
    
    cursor.execute(f"""
        SELECT id, wa_number_id, name, subject, body, category, variables,
               is_predefined, is_active, created_at, updated_at
        FROM email_templates
        WHERE {where_clause}
        ORDER BY is_predefined DESC, name
        LIMIT ? OFFSET ?
    """, [*params, limit, offset])
    
    rows = cursor.fetchall()
    
    templates = [EmailTemplate(**dict(row)) for row in rows]
    return TemplatesResponse(templates=templates)

@router.post("/api/v1/email-templates", response_model=TemplateResponse)
async def create_template(template: EmailTemplateCreate) -> TemplateResponse:
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO email_templates (name, subject, body, category, variables)
        VALUES (?, ?, ?, ?, ?)
    """, (template.name, template.subject, template.body, template.category, template.variables))
    
    template_id = cursor.lastrowid
    conn.commit()
    
    return TemplateResponse(template=EmailTemplate(
        id=template_id,
        name=template.name,
        subject=template.subject,
        body=template.body,
        category=template.category,
        variables=template.variables
    ))

@router.get("/api/v1/email-templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int) -> TemplateResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, wa_number_id, name, subject, body, category, variables,
               is_predefined, is_active, created_at, updated_at
        FROM email_templates WHERE id = ?
    """, (template_id,))
    
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse(template=EmailTemplate(**dict(row)))

@router.patch("/api/v1/email-templates/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: int, update: EmailTemplateUpdate) -> TemplateResponse:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM email_templates WHERE id = ?", (template_id,))
    if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Template not found")
    
    fields = []
    params = []
    
    if update.name is not None:
        fields.append("name = ?")
        params.append(update.name)
    if update.subject is not None:
        fields.append("subject = ?")
        params.append(update.subject)
    if update.body is not None:
        fields.append("body = ?")
        params.append(update.body)
    if update.category is not None:
        fields.append("category = ?")
        params.append(update.category)
    if update.variables is not None:
        fields.append("variables = ?")
        params.append(update.variables)
    if update.is_active is not None:
        fields.append("is_active = ?")
        params.append(1 if update.is_active else 0)
    
    if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
    
    fields.append("updated_at = datetime('now')")
    params.append(template_id)
    
    cursor.execute(f"UPDATE email_templates SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    
    cursor.execute("""
        SELECT id, wa_number_id, name, subject, body, category, variables,
               is_predefined, is_active, created_at, updated_at
        FROM email_templates WHERE id = ?
    """, (template_id,))
    
    row = cursor.fetchone()
    
    return TemplateResponse(template=EmailTemplate(**dict(row)))

@router.delete("/api/v1/email-templates/{template_id}")
async def delete_template(template_id: int):
    with get_db_connection(row_factory=False) as conn:
        cursor = conn.cursor()
    
    cursor.execute("DELETE FROM email_templates WHERE id = ? AND is_predefined = 0", (template_id,))
    
    if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Template not found or cannot delete predefined template")
    
    conn.commit()
    
    return {"status": "deleted", "template_id": template_id}

@router.post("/api/v1/email-templates/{template_id}/render")
async def render_template(template_id: int, variables: dict) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    cursor.execute("SELECT subject, body FROM email_templates WHERE id = ?", (template_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Template not found")
    
    subject = row["subject"]
    body = row["body"]
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))
    
    return {"subject": subject, "body": body}
