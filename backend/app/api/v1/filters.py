"""Filter management endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.backtest_job import BacktestJob
from app.models.filter import Filter
from app.models.user import User
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.schemas.backtest_job import BacktestJobResponse
from app.schemas.common import PaginatedResponse
from app.schemas.filter import FilterCreate, FilterResponse, FilterUpdate
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
async def run_backtest(
    filter_id: int,
    request: BacktestRequest,
    async_mode: bool = Query(False, description="Run backtest asynchronously"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BacktestResponse | BacktestJobResponse:
    """Run a backtest on a filter against historical data.

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
    return await backtest_service.run_backtest(filter_obj, request)


@router.patch("/{filter_id}/alerts", response_model=FilterResponse, operation_id="toggle_filter_alerts")
async def toggle_filter_alerts(
    filter_id: int,
    alerts_enabled: bool = Query(..., description="Enable or disable alerts"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Filter:
    """Enable or disable Telegram alerts for a filter.

    Requires Telegram to be linked to the user account.
    Only the filter owner can modify alert settings.
    """
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

