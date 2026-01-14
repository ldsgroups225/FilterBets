"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import get_settings
from app.database import check_database_connection

settings = get_settings()


# OpenAPI tags metadata for endpoint grouping
tags_metadata = [
    {
        "name": "Root",
        "description": "Root and health check endpoints",
    },
    {
        "name": "Health",
        "description": "Application health monitoring",
    },
    {
        "name": "auth",
        "description": "User authentication: registration, login, token refresh",
    },
    {
        "name": "telegram",
        "description": "Telegram account linking and notifications",
    },
    {
        "name": "leagues",
        "description": "Football leagues and competitions",
    },
    {
        "name": "teams",
        "description": "Team information, statistics, and form analysis",
    },
    {
        "name": "fixtures",
        "description": "Match fixtures with filtering and detailed information",
    },
    {
        "name": "filters",
        "description": "User-defined filter strategies for betting analysis",
    },
    {
        "name": "notifications",
        "description": "Notification history and management",
    },
    {
        "name": "scanner",
        "description": "Pre-match scanner status and control",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## FilterBets API

Football betting analytics platform with AI-powered predictions, backtesting, and strategy management.

### Features

* **Authentication** - Secure JWT-based user authentication
* **Leagues & Teams** - Browse football leagues and team information
* **Fixtures** - Access match data with filtering by date, league, and status
* **Filters** - Create custom filter strategies with multiple conditions
* **Backtesting** - Test filter strategies against historical data

### Authentication

Most endpoints require authentication. Use the `/api/v1/auth/login` endpoint to obtain a JWT token,
then include it in the `Authorization` header as `Bearer <token>`.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    contact={
        "name": "FilterBets Support",
        "email": "support@filterbets.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    """Root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    db_connected = await check_database_connection()
    return {
        "status": "healthy",
        "database": "connected" if db_connected else "disconnected",
    }
