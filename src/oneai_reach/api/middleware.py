"""Middleware for FastAPI application.

Includes CORS, request logging, correlation IDs, and global exception handling.
"""

import logging
import uuid
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from oneai_reach.domain.exceptions import OneAIReachException

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Add correlation ID to each request for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        logger.info(
            f"[{correlation_id}] {request.method} {request.url.path}",
            extra={"correlation_id": correlation_id},
        )

        response = await call_next(request)

        logger.info(
            f"[{correlation_id}] {request.method} {request.url.path} -> {response.status_code}",
            extra={"correlation_id": correlation_id},
        )

        return response


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI app."""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIDMiddleware)


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers."""

    @app.exception_handler(OneAIReachException)
    async def domain_exception_handler(request: Request, exc: OneAIReachException):
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        logger.error(
            f"[{correlation_id}] Domain exception: {exc}",
            extra={"correlation_id": correlation_id},
        )

        return JSONResponse(
            status_code=400,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "type": exc.__class__.__name__,
                "context": exc.context,
                "correlation_id": correlation_id,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        logger.error(
            f"[{correlation_id}] Unhandled exception: {exc}",
            extra={"correlation_id": correlation_id},
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "type": "Exception",
                "correlation_id": correlation_id,
            },
        )
