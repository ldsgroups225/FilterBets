"""Pagination utilities for API endpoints."""

import math
from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import PaginationMeta

T = TypeVar("T")


async def paginate(
    session: AsyncSession,
    query: Select[Any],
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Any], PaginationMeta]:
    """Paginate a SQLAlchemy query.

    Args:
        session: Database session
        query: SQLAlchemy select query
        page: Page number (1-indexed)
        per_page: Items per page

    Returns:
        Tuple of (items, pagination_meta)
    """
    # Ensure valid pagination parameters
    page = max(1, page)
    per_page = min(max(1, per_page), 100)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await session.execute(count_query)
    total_items = result.scalar() or 0

    # Calculate pagination values
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1

    # Apply pagination to query
    offset = (page - 1) * per_page
    paginated_query = query.offset(offset).limit(per_page)

    # Execute query
    result = await session.execute(paginated_query)
    items = list(result.scalars().all())

    # Create metadata
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return items, meta
