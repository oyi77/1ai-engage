"""Pydantic request/response models for FastAPI endpoints.

Common models used across API endpoints for validation and serialization.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status (healthy/degraded/unhealthy)")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error_code: str = Field(..., description="Programmatic error identifier")
    message: str = Field(..., description="Human-readable error message")
    type: str = Field(..., description="Exception class name")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error context"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Number of items to return"
    )


class LeadResponse(BaseModel):
    """Lead response model."""

    id: str = Field(..., description="Lead ID")
    name: str = Field(..., description="Lead name")
    email: Optional[str] = Field(default=None, description="Lead email")
    phone: Optional[str] = Field(default=None, description="Lead phone")
    status: str = Field(..., description="Lead funnel status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ConversationResponse(BaseModel):
    """Conversation response model."""

    id: str = Field(..., description="Conversation ID")
    lead_id: str = Field(..., description="Associated lead ID")
    channel: str = Field(..., description="Communication channel (email/whatsapp)")
    status: str = Field(..., description="Conversation status")
    message_count: int = Field(default=0, description="Number of messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
