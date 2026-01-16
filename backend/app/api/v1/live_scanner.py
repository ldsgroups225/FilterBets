"""Live scanner API endpoints for real-time match filtering."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.live_filter import (
    LiveFilterBacktestRequest,
    LiveFilterBacktestResponse,
    LiveFilterResultResponse,
    LiveMatchResponse,
    LiveOddsResponse,
    LiveScannerStatsResponse,
)
from app.services.live_filter_engine import LiveFilterEngine
from app.services.mock_live_data import MockLiveDataProvider

router = APIRouter(prefix="/live-scanner", tags=["live-scanner"])

# Global instances for mock data
mock_data_provider = MockLiveDataProvider()
live_filter_engine = LiveFilterEngine()


@router.get("/matches", response_model=list[LiveMatchResponse])
async def get_live_matches(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LiveMatchResponse]:
    """
    Get all currently live matches with stats.

    Returns mock live match data for demonstration.
    """
    live_matches = mock_data_provider.get_live_matches()

    # Convert to response format
    response_matches = []
    for match in live_matches:
        response_match = LiveMatchResponse(
            id=match["id"],
            fixture_id=match["fixture_id"],
            status=match["status"],
            minute=match["minute"],
            home_score=match["home_score"],
            away_score=match["away_score"],
            live_stats=match["live_stats"],
            home_team_state=match["team_state"].get("home"),
            away_team_state=match["team_state"].get("away"),
            momentum=match["team_state"].get("momentum"),
            ai_predictions=match.get("ai_predictions"),
            historical_stats=match.get("historical"),
            last_update=mock_data_provider.last_update,
        )
        response_matches.append(response_match)

    return response_matches


@router.get("/matches/{fixture_id}", response_model=LiveMatchResponse)
async def get_live_match(
    fixture_id: int,
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LiveMatchResponse:
    """Get a specific live match by fixture ID."""
    match = mock_data_provider.get_match_by_fixture_id(fixture_id)

    if not match:
        raise HTTPException(status_code=404, detail="Live match not found")

    return LiveMatchResponse(
        id=match["id"],
        fixture_id=match["fixture_id"],
        status=match["status"],
        minute=match["minute"],
        home_score=match["home_score"],
        away_score=match["away_score"],
        live_stats=match["live_stats"],
        home_team_state=match["team_state"].get("home"),
        away_team_state=match["team_state"].get("away"),
        momentum=match["team_state"].get("momentum"),
        ai_predictions=match.get("ai_predictions"),
        historical_stats=match.get("historical"),
        last_update=mock_data_provider.last_update,
    )


@router.get("/odds/{fixture_id}", response_model=list[LiveOddsResponse])
async def get_live_odds(
    fixture_id: int,
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LiveOddsResponse]:
    """Get live odds for a specific fixture."""
    odds_data = mock_data_provider.get_live_odds(fixture_id)

    response_odds = []
    for odds in odds_data:
        response_odds.append(LiveOddsResponse(**odds))

    return response_odds


@router.post("/scan")
async def trigger_scan(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Manually trigger live scan for user's filters.

    Returns scan results and statistics.
    """
    # Update mock data to simulate live changes
    mock_data_provider.update_match_data()

    # Get live matches
    live_matches = mock_data_provider.get_live_matches()

    # TODO: Get user's live filters and evaluate them
    # For now, return mock scan results

    scan_results = {
        "scan_id": f"scan_{mock_data_provider.last_update.strftime('%Y%m%d_%H%M%S')}",
        "matches_scanned": len(live_matches),
        "filters_matched": 0,  # TODO: Implement actual filter matching
        "alerts_generated": 0,  # TODO: Implement actual alert generation
        "scan_duration_ms": 150,  # Mock duration
        "timestamp": mock_data_provider.last_update.isoformat(),
    }

    return scan_results


@router.get("/stats", response_model=LiveScannerStatsResponse)
async def get_scanner_stats(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LiveScannerStatsResponse:
    """Get live scanner statistics."""
    live_matches = mock_data_provider.get_live_matches()

    # TODO: Get actual stats from database
    # For now, return mock statistics
    return LiveScannerStatsResponse(
        active_filters=5,  # TODO: Get from user's filters
        live_matches=len(live_matches),
        alerts_today=12,  # TODO: Get from database
        success_rate_24h=68.5,  # TODO: Calculate from results
        avg_odds_today=2.15,  # TODO: Calculate from results
    )


@router.post("/filters/test")
async def test_live_filter(
    filter_rules: list[dict[str, Any]],
    fixture_id: int = Query(..., description="Fixture ID to test against"),
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Test live filter rules against a specific match.

    Useful for filter validation before saving.
    """
    match = mock_data_provider.get_match_by_fixture_id(fixture_id)

    if not match:
        raise HTTPException(status_code=404, detail="Live match not found")

    # Evaluate filter against match
    matches = live_filter_engine.evaluate_live_match(match, filter_rules)

    # Return detailed evaluation
    evaluation_results = {
        "fixture_id": fixture_id,
        "filter_matches": matches,
        "match_data": {
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "score": f"{match['home_score']}-{match['away_score']}",
            "minute": match["minute"],
            "status": match["status"],
        },
        "rule_evaluations": [],  # TODO: Add detailed rule evaluation
        "timestamp": mock_data_provider.last_update.isoformat(),
    }

    return evaluation_results


@router.get("/results/{filter_id}", response_model=list[LiveFilterResultResponse])
async def get_filter_results(
    filter_id: int,
    _limit: int = Query(50, ge=1, le=100),
    _offset: int = Query(0, ge=0),
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LiveFilterResultResponse]:
    """
    Get live filter results with dual-stat comparison.

    Returns historical results for a specific live filter.
    """
    # TODO: Implement actual database query
    # For now, return mock results

    mock_results: list[dict[str, Any]] = [
        {
            "id": 1,
            "filter_id": filter_id,
            "fixture_id": 1001,
            "triggered_at": mock_data_provider.last_update,
            "triggered_minute": 67,
            "notification_value": {
                "score": "2-1",
                "corners": "5-3",
                "possession": "55-45",
                "status": "WINNING",
            },
            "final_value": {
                "score": "3-1",
                "corners": "7-4",
                "possession": "52-48",
                "status": "WIN",
            },
            "bet_result": "WIN",
            "resolved_at": mock_data_provider.last_update,
            "odds_at_trigger": {"1X2_HOME": 1.85},
        },
        # TODO: Add more mock results
    ]

    response_results = []
    for result in mock_results:
        response_results.append(LiveFilterResultResponse(**result))

    return response_results


@router.post("/backtest", response_model=LiveFilterBacktestResponse)
async def run_live_filter_backtest(
    request: LiveFilterBacktestRequest,
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> LiveFilterBacktestResponse:
    """
    Run backtest for live filter using historical data.

    Note: This uses mock data for demonstration. In production,
    this would use actual historical live match data.
    """
    # TODO: Implement actual backtest logic
    # For now, return mock backtest results

    return LiveFilterBacktestResponse(
        filter_id=request.filter_id,
        total_alerts=25,
        resolved_alerts=20,
        wins=14,
        losses=6,
        pushes=0,
        success_rate=70.0,
        avg_odds=2.15,
        roi=50.5,
        results=[],  # TODO: Add actual results
    )


@router.post("/mock/refresh")
async def refresh_mock_data(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Force update of mock live data.

    Useful for demonstration and testing purposes.
    """
    mock_data_provider.update_match_data()

    return {
        "message": "Mock live data refreshed",
        "matches_updated": len(mock_data_provider.get_live_matches()),
        "timestamp": mock_data_provider.last_update.isoformat(),
    }


@router.get("/mock/match-history/{fixture_id}")
async def get_match_history(
    fixture_id: int,
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get match history at different minute intervals.

    Useful for demonstrating dual-stat comparison feature.
    """
    match = mock_data_provider.get_match_by_fixture_id(fixture_id)

    if not match:
        raise HTTPException(status_code=404, detail="Live match not found")

    # Generate match snapshots at different minutes
    history_minutes = [15, 30, 45, 60, 75, 90]
    match_history = []

    for minute in history_minutes:
        if minute <= match["minute"]:
            snapshot = mock_data_provider.get_match_at_minute(fixture_id, minute)
            if snapshot:
                match_history.append({
                    "minute": minute,
                    "score": f"{snapshot['home_score']}-{snapshot['away_score']}",
                    "corners": f"{snapshot['live_stats']['corners']['home']}-{snapshot['live_stats']['corners']['away']}",
                    "possession": f"{snapshot['live_stats']['possession']['home']}-{snapshot['live_stats']['possession']['away']}",
                })

    return {
        "fixture_id": fixture_id,
        "match": {
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "current_score": f"{match['home_score']}-{match['away_score']}",
            "current_minute": match["minute"],
        },
        "history": match_history,
    }
