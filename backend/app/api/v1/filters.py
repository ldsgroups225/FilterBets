"""Filter management endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.filter import Filter
from app.models.user import User
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.schemas.common import PaginatedResponse
from app.schemas.filter import FilterCreate, FilterResponse, FilterUpdate
from app.schemas.fixture import FixtureResponse
from app.services.backtest import BacktestService
from app.services.filter_engine import FilterEngine
from app.utils.pagination import paginate

router = APIRouter(prefix="/filters", tags=["filters"])


@router.post("", response_model=FilterResponse, status_code=201)
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


@router.get("", response_model=PaginatedResponse[FilterResponse])
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


@router.get("/{filter_id}", response_model=FilterResponse)
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


@router.put("/{filter_id}", response_model=FilterResponse)
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
        filter_obj.rules = [rule.model_dump() for rule in filter_data.rules]  # type: ignore[misc]
    if filter_data.is_active is not None:
        filter_obj.is_active = filter_data.is_active

    await db.commit()
    await db.refresh(filter_obj)

    return filter_obj


@router.delete("/{filter_id}", status_code=204)
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


@router.get("/{filter_id}/matches", response_model=list[FixtureResponse])
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


@router.post("/{filter_id}/backtest", response_model=BacktestResponse)
async def run_backtest(
    filter_id: int,
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BacktestResponse:
    """Run a backtest on a filter against historical data.

    Evaluates the filter's performance by applying it to historical matches
    and calculating win rate, ROI, and other metrics.

    **Bet Types:**
    - `home_win`: Home team wins
    - `away_win`: Away team wins
    - `draw`: Match ends in draw
    - `over_2_5`: Total goals over 2.5
    - `under_2_5`: Total goals under 2.5

    Results are cached for 24 hours.
    """
    # Get filter
    result = await db.execute(
        select(Filter).where(Filter.id == filter_id, Filter.user_id == current_user.id)
    )
    filter_obj = result.scalar_one_or_none()

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    # Run backtest
    backtest_service = BacktestService(db)
    return await backtest_service.run_backtest(filter_obj, request)
