"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import auth, backtest, filters, fixtures, leagues, teams

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(leagues.router)
api_router.include_router(teams.router)
api_router.include_router(fixtures.router)
api_router.include_router(filters.router)
api_router.include_router(backtest.router)
