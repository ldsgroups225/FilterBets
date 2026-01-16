"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    backtest,
    filters,
    fixtures,
    leagues,
    live_scanner,
    notifications,
    scanner,
    teams,
    telegram,
)

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(telegram.router, prefix="/auth", tags=["telegram"])
api_router.include_router(leagues.router)
api_router.include_router(teams.router)
api_router.include_router(fixtures.router)
api_router.include_router(filters.router)
api_router.include_router(backtest.router)
api_router.include_router(notifications.router)
api_router.include_router(scanner.router)
api_router.include_router(live_scanner.router)
