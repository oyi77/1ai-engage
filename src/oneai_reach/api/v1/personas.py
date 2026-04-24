"""Persona API endpoints — CRUD for personas and channel-persona assignments."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from oneai_reach.api.dependencies import verify_api_key
from oneai_reach.config.settings import get_settings
from oneai_reach.infrastructure.messaging.persona_service import PersonaService

router = APIRouter(
    prefix="/api/v1/personas",
    tags=["personas"],
    dependencies=[Depends(verify_api_key)],
)


def _get_service() -> PersonaService:
    settings = get_settings()
    return PersonaService(settings.database.db_file)


class CreatePersonaRequest(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    scope: str = Field(default="universal")
    system_prompt: str = Field(..., min_length=1)
    tone: str = Field(default="casual")
    language: str = Field(default="id")
    example_replies: Optional[List[str]] = None


class UpdatePersonaRequest(BaseModel):
    name: Optional[str] = None
    scope: Optional[str] = None
    system_prompt: Optional[str] = None
    tone: Optional[str] = None
    language: Optional[str] = None
    example_replies: Optional[List[str]] = None


class AssignPersonaRequest(BaseModel):
    channel_id: str
    mode: str
    persona_id: str


# ── Persona CRUD ───────────────────────────────────────────────

@router.get("/")
async def list_personas(scope: Optional[str] = Query(None)):
    svc = _get_service()
    return {"personas": svc.list_personas(scope=scope)}


@router.post("/")
async def create_persona(body: CreatePersonaRequest):
    svc = _get_service()
    try:
        p = svc.create_persona(
            id=body.id,
            name=body.name,
            scope=body.scope,
            system_prompt=body.system_prompt,
            tone=body.tone,
            language=body.language,
            example_replies=body.example_replies,
        )
        return {"status": "success", "data": p}
    except Exception as e:
        raise HTTPException(400, str(e))


# ── Assignment CRUD (must come BEFORE /{persona_id} to avoid route capture) ──

@router.get("/assignments")
async def list_assignments(channel_id: Optional[str] = Query(None)):
    svc = _get_service()
    return {"assignments": svc.list_assignments(channel_id=channel_id)}


@router.post("/assignments")
async def assign_persona(body: AssignPersonaRequest):
    svc = _get_service()
    try:
        assignment = svc.assign_persona(body.channel_id, body.mode, body.persona_id)
        return {"status": "success", "data": assignment}
    except Exception as e:
        raise HTTPException(400, str(e))


@router.delete("/assignments/{channel_id}/{mode}")
async def unassign_persona(channel_id: str, mode: str):
    svc = _get_service()
    deleted = svc.unassign_persona(channel_id, mode)
    if not deleted:
        raise HTTPException(404, f"No assignment found for channel {channel_id} mode {mode}")
    return {"status": "success", "deleted": True}


# ── Resolution ─────────────────────────────────────────────────

@router.get("/resolve/{channel_id}/{mode}")
async def resolve_persona(channel_id: str, mode: str):
    svc = _get_service()
    persona = svc.get_persona_for_channel(channel_id, mode)
    if not persona:
        raise HTTPException(404, f"No persona resolved for channel {channel_id} mode {mode}")
    source = persona.pop("_source", "unknown")
    return {"persona": persona, "resolution_source": source}


# ── Persona single-item CRUD (parameterized routes LAST) ───────

@router.get("/{persona_id}")
async def get_persona(persona_id: str):
    svc = _get_service()
    p = svc.get_persona(persona_id)
    if not p:
        raise HTTPException(404, f"Persona not found: {persona_id}")
    return {"status": "success", "data": p}


@router.patch("/{persona_id}")
async def update_persona(persona_id: str, body: UpdatePersonaRequest):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, "No fields to update")

    svc = _get_service()
    p = svc.update_persona(persona_id, **updates)
    if not p:
        raise HTTPException(404, f"Persona not found: {persona_id}")
    return {"status": "success", "data": p}


@router.delete("/{persona_id}")
async def delete_persona(persona_id: str):
    svc = _get_service()
    try:
        deleted = svc.delete_persona(persona_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not deleted:
        raise HTTPException(404, f"Persona not found: {persona_id}")
    return {"status": "success", "deleted": True}
