"""Filter management endpoints."""

from datetime import date
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.backtest_job import BacktestJob
from app.models.filter import Filter
from app.models.fixture import Fixture
from app.models.user import User
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.schemas.backtest_job import BacktestJobResponse
from app.schemas.common import PaginatedResponse
from app.schemas.filter import (
    FilterAlertsToggle,
    FilterCondition,
    FilterCreate,
    FilterResponse,
    FilterUpdate,
    POST_MATCH_FIELDS,
    PRE_MATCH_ONLY_FIELDS,
)
from app.schemas.fixture import FixtureResponse
from app.services.backtest import BacktestService
from app.services.filter_engine import FilterEngine
from app.tasks.backtest_tasks import run_async_backtest
from app.utils.pagination import paginate

router = APIRouter(prefix="/filters", tags=["filters"])


@router.post("", response_model=FilterResponse, status_code=201, operation_id="create_filter")
async def create_filter(
    filter_data: FilterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Filter:
    """Create a new filter strategy.

    Create a filter with multiple conditions to identify betting opportunities.
    Supports operators: =, !=, >, <, >=, <=, in, between.

    Maximum 10 conditions per filter.
    """
    # Convert rules to dict format for JSONB storage
    rules_dict = [rule.model_dump() for rule in filter_data.rules]

    filter_obj = Filter(
        user_id=current_user.id,
        name=filter_data.name,
        description=filter_data.description,
        rules=rules_dict,
        is_active=filter_data.is_active,
    )

    db.add(filter_obj)
    await db.commit()
    await db.refresh(filter_obj)

    return filter_obj


@router.get("", response_model=PaginatedResponse[FilterResponse], operation_id="list_filters")
async def list_filters(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[FilterResponse]:
    """List all filters for the current user.

    Returns paginated list of user's filter strategies.
    Optionally filter by active status.
    """
    query = select(Filter).where(Filter.user_id == current_user.id)

    if is_active is not None:
        query = query.where(Filter.is_active == is_active)

    query = query.order_by(Filter.created_at.desc())

    items, meta = await paginate(db, query, page, per_page)
    return PaginatedResponse(items=items, meta=meta)


@router.get("/{filter_id}", response_model=FilterResponse, operation_id="get_filter")
async def get_filter(
    filter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Filter:
    """Get a specific filter by ID.

    Only the filter owner can access their filters.
    """
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    return filter_obj


@router.put("/{filter_id}", response_model=FilterResponse, operation_id="update_filter")
async def update_filter(
    filter_id: int,
    filter_data: FilterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Filter:
    """Update a filter strategy.

    Update filter name, description, rules, or active status.
    Only the filter owner can update their filters.
    """
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Update fields
    if filter_data.name is not None:
        filter_obj.name = filter_data.name
    if filter_data.description is not None:
        filter_obj.description = filter_data.description
    if filter_data.rules is not None:
        # Type ignore needed due to SQLAlchemy JSONB column type complexity
        filter_obj.rules = [rule.model_dump() for rule in filter_data.rules]  # type: ignore[assignment]
    if filter_data.is_active is not None:
        filter_obj.is_active = filter_data.is_active

    await db.commit()
    await db.refresh(filter_obj)

    return filter_obj


@router.delete("/{filter_id}", status_code=204, operation_id="delete_filter")
async def delete_filter(
    filter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a filter strategy.

    Permanently removes the filter and all associated backtest results.
    Only the filter owner can delete their filters.
    """
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    await db.delete(filter_obj)
    await db.commit()


@router.get("/{filter_id}/matches", response_model=list[FixtureResponse], operation_id="get_filter_matches")
async def get_filter_matches(
    filter_id: int,
    date_from: date | None = Query(None, description="Start date for filtering"),
    date_to: date | None = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FixtureResponse]:
    """Get fixtures matching the filter criteria.

    Apply the filter rules to find matching fixtures.
    Optionally filter by date range.
    """
    # Get filter
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Use filter engine to find matches
    engine = FilterEngine(db)
    fixtures = await engine.find_matching_fixtures(
        rules=filter_obj.rules, date_from=date_from, date_to=date_to, limit=limit  # type: ignore[arg-type]
    )

    # Return fixtures directly - FixtureResponse has from_attributes=True
    return fixtures  # type: ignore[return-value]


@router.post("/{filter_id}/backtest", response_model=BacktestResponse | BacktestJobResponse, operation_id="run_filter_backtest")
async def run_filter_backtest(
    filter_id: int,
    request: BacktestRequest,
    async_mode: bool = Query(False, description="Run asynchronously via Celery"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BacktestResponse | BacktestJobResponse:
    """Run a pre-match backtest on a filter against historical data.

    Evaluates the filter's performance by applying it to historical matches
    and calculating win rate, ROI, and other metrics.

    **Bet Types:**
    - `home_win`: Home team wins
    - `away_win`: Away team wins
    - `draw`: Match ends in draw
    - `over_2_5`: Total goals over 2.5
    - `under_2_5`: Total goals under 2.5

    **Modes:**
    - `async_mode=False` (default): Synchronous execution, returns results immediately
    - `async_mode=True`: Asynchronous execution via Celery, returns job ID for status tracking

    Results are cached for 24 hours.
    """
    # Get filter
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # If async mode, create job and dispatch to Celery
    if async_mode:
        from uuid import uuid4

        # Create backtest job
        job = BacktestJob(
            job_id=uuid4(),
            user_id=current_user.id,
            filter_id=filter_id,
            status="pending",
            progress=0,
            bet_type=request.bet_type.value,
            seasons=",".join(str(s) for s in request.seasons),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # Dispatch to Celery
        run_async_backtest.delay(
            job_id=str(job.job_id),
            filter_id=filter_id,
            bet_type=request.bet_type.value,
            seasons=request.seasons,
            stake=request.stake,
        )

        return BacktestJobResponse.model_validate(job)

    # Synchronous execution
    backtest_service = BacktestService(db)
    response = await backtest_service.run_backtest(filter_obj, request)

    # Trigger notification even for sync/cached runs
    from app.tasks.notification_tasks import send_backtest_report_manual
    send_backtest_report_manual.delay(
        user_id=current_user.id,
        filter_id=filter_id,
        bet_type=request.bet_type.value,
        seasons=request.seasons,
        result_data=response.model_dump(mode="json"),
    )

    return response


@router.patch("/{filter_id}/alerts", response_model=FilterResponse, operation_id="toggle_filter_alerts")
async def toggle_filter_alerts(
    filter_id: int,
    toggle_data: FilterAlertsToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Filter:
    """Enable or disable Telegram alerts for a filter.

    Requires Telegram to be linked to the user account.
    Only the filter owner can modify alert settings.
    """
    alerts_enabled = toggle_data.alerts_enabled
    # Check if user has Telegram linked
    if alerts_enabled and not current_user.telegram_verified:
        raise HTTPException(
            status_code=400,
            detail="Telegram account must be linked before enabling alerts",
        )

    # Get filter
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Update alerts_enabled
    filter_obj.alerts_enabled = alerts_enabled
    await db.commit()
    await db.refresh(filter_obj)

    return filter_obj


@router.post("/{filter_id}/backtest/pre-match", response_model=BacktestResponse, operation_id="run_pre_match_backtest")
async def run_pre_match_backtest(
    filter_id: int,
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BacktestResponse:
    """Run enhanced pre-match backtest with detailed analytics.

    This endpoint is specifically designed for pre-match filters and provides:
    - Detailed performance metrics by league, season, and bet type
    - Risk analysis and confidence intervals
    - Comparison with baseline performance
    - Trend analysis over time
    - Recommended stake sizes based on historical performance

    **Enhanced Features:**
    - League-specific performance breakdown
    - Season-over-season trend analysis
    - Confidence intervals for success rate
    - Risk-adjusted ROI calculations
    - Optimal stake size recommendations
    - Performance vs. baseline comparison

    **Filter Requirements:**
    Only supports pre-match filter fields (historical stats, form data, etc.).
    Live filter fields will be ignored for this backtest.

    Args:
        filter_id: Filter ID to backtest
        request: Backtest configuration parameters
        db: Database session
        current_user: Current authenticated user

    Returns:
        Enhanced backtest results with detailed analytics

    Raises:
        HTTPException: 404 if filter not found, 400 if filter contains live rules
    """
    # Get filter
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Check if filter contains live rules (not allowed for pre-match backtest)
    live_rule_categories = ["live_stats", "team_state", "odds", "timing"]
    filter_rules = cast(list[dict[str, Any]], filter_obj.rules or [])

    for rule_data in filter_rules:
        rule_category = rule_data.get("category")
        if rule_category in live_rule_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Pre-match backtest cannot contain live rules. Found rule category: {rule_category}. "
                f"Use live scanner backtest endpoint for live filters."
            )

    # Run enhanced pre-match backtest
    backtest_service = BacktestService(db)
    enhanced_results = await backtest_service.run_enhanced_pre_match_backtest(
        filter_obj=filter_obj,
        bet_type=request.bet_type,
        seasons=request.seasons,
        include_analytics=True,
    )

    return enhanced_results


@router.get("/{filter_id}/analytics/pre-match", operation_id="get_pre_match_analytics")
async def get_pre_match_analytics(
    filter_id: int,
    seasons: list[int] = Query([], description="Seasons to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get pre-match analytics for a filter without running full backtest.

    Returns quick analytics including:
    - Recent performance trends
    - League-specific insights
    - Risk metrics
    - Recommended settings

    Args:
        filter_id: Filter ID to analyze
        seasons: Optional seasons to focus on
        db: Database session
        current_user: Current authenticated user

    Returns:
        Quick analytics data

    Raises:
        HTTPException: 404 if filter not found
    """
    # Get filter
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Get quick analytics
    backtest_service = BacktestService(db)
    analytics = await backtest_service.get_quick_pre_match_analytics(
        filter_obj=filter_obj,
        seasons=seasons or None,
    )

    return analytics


class FilterValidationResponse(BaseModel):
    """Response for filter validation."""

    is_valid: bool = Field(..., description="Whether the filter is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    estimated_matches: int = Field(..., description="Estimated number of matching fixtures")
    match_percentage: float = Field(
        ..., description="Percentage of total fixtures that would match"
    )
    seasons_available: list[int] = Field(
        ..., description="Seasons with data available for this filter"
    )


class FilterValidationRequest(BaseModel):
    """Request for filter validation without saving."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    rules: list[FilterCondition] = Field(..., min_length=1, max_length=10)
    is_active: bool = Field(default=True)


@router.post("/validate", response_model=FilterValidationResponse, operation_id="validate_filter")
async def validate_filter(
    filter_data: FilterValidationRequest,
    date_from: date | None = Query(None, description="Start date for match estimation"),
    date_to: date | None = Query(None, description="End date for match estimation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FilterValidationResponse:
    """Validate a filter without saving it.

    Checks filter rules for errors, counts estimated matches, and provides warnings.
    This is useful for testing filters before creating them.

    Returns:
        FilterValidationResponse with validation results and match estimates
    """
    errors: list[str] = []
    warnings: list[str] = []
    rules_dict = [rule.model_dump() for rule in filter_data.rules]

    for i, rule in enumerate(rules_dict):
        field = rule.get("field")
        operator = rule.get("operator")
        value = rule.get("value")

        if not field:
            errors.append(f"Rule {i+1}: Missing field name")
            continue

        if not operator:
            errors.append(f"Rule {i+1}: Missing operator")
            continue

        if value is None:
            errors.append(f"Rule {i+1}: Missing value for field '{field}'")
            continue

        if field in PRE_MATCH_ONLY_FIELDS:
            warnings.append(
                f"Field '{field}' uses pre-match data only. "
                "Results may differ from live scanner."
            )

        if field in POST_MATCH_FIELDS:
            errors.append(
                f"Field '{field}' is post-match only and cannot be used for pre-match validation. "
                f"Use pre-match alternatives: {PRE_MATCH_ONLY_FIELDS.get(field, 'See documentation')}"
            )

        if operator == "between" and not isinstance(value, list | tuple):
            errors.append(f"Rule {i+1}: 'between' operator requires a list [min, max]")

        if operator == "in" and not isinstance(value, list):
            errors.append(f"Rule {i+1}: 'in' operator requires a list of values")

    if len(filter_data.rules) > 10:
        warnings.append("More than 10 rules may result in very few matches")

    engine = FilterEngine(db)
    fixtures = await engine.find_matching_fixtures(
        rules=rules_dict, date_from=date_from, date_to=date_to, limit=10000
    )

    total_fixtures_query = select(Fixture.id)
    if date_from:
        total_fixtures_query = total_fixtures_query.where(Fixture.match_date >= date_from)
    if date_to:
        total_fixtures_query = total_fixtures_query.where(Fixture.match_date <= date_to)

    total_result = await db.execute(total_fixtures_query)
    total_count = len(total_result.all())

    estimated_matches = len(fixtures)
    match_percentage = (estimated_matches / total_count * 100) if total_count > 0 else 0.0

    if estimated_matches == 0:
        warnings.append("Filter matches no fixtures. Consider relaxing the rules.")

    if estimated_matches > 1000:
        warnings.append(
            f"Filter matches {estimated_matches} fixtures. "
            "Consider adding more conditions to narrow results."
        )

    seasons_query = select(Fixture.season_type).distinct()
    seasons_result = await db.execute(seasons_query)
    seasons_available = [s[0] for s in seasons_result.all()]

    return FilterValidationResponse(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        estimated_matches=estimated_matches,
        match_percentage=round(match_percentage, 2),
        seasons_available=seasons_available,
    )

