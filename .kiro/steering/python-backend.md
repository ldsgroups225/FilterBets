---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# Python Backend Standards

## Code Style

### Type Hints

Always use type hints for function parameters and return values:

```python
# Good
async def get_filter(filter_id: int, db: AsyncSession) -> Filter | None:
    ...

# Bad - missing types
async def get_filter(filter_id, db):
    ...
```

### Async/Await

All database operations must be async:

```python
# Good
async def get_fixtures(db: AsyncSession) -> list[Fixture]:
    result = await db.execute(select(Fixture))
    return list(result.scalars().all())

# Bad - blocking call
def get_fixtures(db: Session) -> list[Fixture]:
    return db.query(Fixture).all()
```

### Pydantic Schemas

Use Pydantic v2 syntax with `model_config`:

```python
from pydantic import BaseModel, Field

class FilterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rules: list[FilterRule] = Field(..., max_length=10)
    is_active: bool = True

    model_config = {"from_attributes": True}
```

## API Endpoints

### Route Structure

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.filter import Filter
from app.schemas.filter import FilterCreate, FilterResponse

router = APIRouter(prefix="/filters", tags=["filters"])

@router.post("", response_model=FilterResponse, status_code=201)
async def create_filter(
    filter_data: FilterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Filter:
    """Create a new filter strategy."""
    ...
```

### Error Handling

Use HTTPException with appropriate status codes:

```python
if not filter_obj:
    raise HTTPException(status_code=404, detail="Filter not found")

if filter_obj.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

## SQLAlchemy Models

### Model Definition

```python
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="filters")
```

## Services

### Service Pattern

Encapsulate business logic in service classes:

```python
class BacktestService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_backtest(
        self, filter_obj: Filter, request: BacktestRequest
    ) -> BacktestResponse:
        # Business logic here
        ...
```

## Testing

### Test Structure

```python
import pytest
from httpx import AsyncClient

class TestFilters:
    async def test_create_filter_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/filters",
            json={"name": "Test", "rules": [...]},
            headers=auth_headers,
        )
        assert response.status_code == 201
```

### Fixtures

Use pytest fixtures from `conftest.py`:

- `db_session` - Async database session with rollback
- `client` - Async HTTP test client
- `auth_headers` - JWT auth headers for authenticated requests
- `test_user` - Pre-created test user

## Common Patterns

### Pagination

```python
from app.utils.pagination import paginate

items, meta = await paginate(db, query, page, per_page)
return PaginatedResponse(items=items, meta=meta)
```

### Query Building

```python
query = select(Fixture).where(Fixture.status_id == 3)
if date_from:
    query = query.where(Fixture.match_date >= date_from)
query = query.order_by(Fixture.match_date.desc()).limit(limit)
```
