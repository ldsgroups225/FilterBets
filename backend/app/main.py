"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Annotated

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mcp import FastApiMCP  # type: ignore[import-untyped]
from fastapi_mcp.types import AuthConfig
from jose import JWTError

from app.api.v1 import api_router
from app.config import get_settings
from app.database import check_database_connection
from app.utils.security import decode_token

settings = get_settings()

security = HTTPBearer()


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
    {
        "name": "backtest",
        "description": "Backtest job status and management",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
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


async def authenticate_mcp_request(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> bool:
    """Authentication dependency for MCP endpoints.

    Validates JWT bearer tokens for MCP access.

    Args:
        request: The incoming request
        credentials: HTTP authorization credentials

    Returns:
        True if authentication successful

    Raises:
        HTTPException: 401 if authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: int | None = payload.get("user_id")
        token_type: str | None = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


# Create and mount the MCP server
# Best practices from official docs:
# - Use descriptive name and description for LLM context
# - Exclude dangerous operations (PUT/DELETE) for safety
# - Include full response schemas for better LLM understanding
# - Use HTTP transport (recommended over SSE)
# - Add JWT authentication via auth_config

mcp = FastApiMCP(
    app,
    name="FilterBets API",
    description=(
        "Football betting analytics API with filters, backtesting, and match data. "
        "Use this to query fixtures, leagues, teams, and test filter strategies."
    ),
    # Include full JSON schema in tool descriptions for better LLM understanding
    describe_full_response_schema=True,
    describe_all_responses=True,
    # Exclude dangerous write/delete operations for safety (LLMs are non-deterministic)
    exclude_tags=["auth", "telegram"],
    # Exclude specific destructive operations
    exclude_operations=[
        "delete_filter",
        "update_filter",
        "toggle_filter_alerts",
    ],
    # JWT authentication configuration
    auth_config=AuthConfig(
        dependencies=[Depends(authenticate_mcp_request)],
    ),
)
mcp.mount_http()


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
