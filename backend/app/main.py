"""
BankOps FastAPI Application Factory.

Entry point: uvicorn app.main:app --reload
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from fastapi.exceptions import RequestValidationError
from app.exceptions import (
    BankOpsException,
    bankops_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("bankops")


def create_app() -> FastAPI:
    """Application factory pattern — creates and configures the FastAPI app."""

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Banking Operations & Database Monitoring System — "
            "educational demo project. All data is simulated."
        ),
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────────
    allowed_origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Trusted Host (prevent host header injection) ──────────
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1"],
        )

    # ── Exception Handlers ────────────────────────────────────
    app.add_exception_handler(BankOpsException, bankops_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # ── Routers ───────────────────────────────────────────────
    from app.routers import auth, users, dashboard

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(dashboard.router)

    @app.get("/api/health", tags=["System"])
    def health_check():
        """Liveness probe — returns app status."""
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": "1.0.0",
            "environment": settings.app_env,
        }

    logger.info("BankOps API initialized in %s mode", settings.app_env)
    return app


app = create_app()
