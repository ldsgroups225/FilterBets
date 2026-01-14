---
inclusion: manual
---

# Database Standards

Use this guide when working with database models, migrations, and queries.

## Database Configuration

- **Engine:** PostgreSQL 15+
- **Port:** 5433 (non-default)
- **Credentials:** user=filterbets, password=filterbets, db=filterbets
- **ORM:** SQLAlchemy 2.0 with async support
- **Migrations:** Alembic

## SQLAlchemy Models

### Model Template

```python
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Filter(Base):
    """User-defined filter strategy."""

    __tablename__ = "filters"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Required fields
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional fields
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSONB for flexible data
    rules: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Decimal for precise calculations
    stake: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))

    # Boolean with default
    is_active: Mapped[bool] = mapped_column(default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="filters")
    backtest_jobs: Mapped[list["BacktestJob"]] = relationship(
        "BacktestJob", back_populates="filter", cascade="all, delete-orphan"
    )
```

### Relationship Patterns

```python
# One-to-Many (User has many Filters)
class User(Base):
    filters: Mapped[list["Filter"]] = relationship(
        "Filter", back_populates="user", cascade="all, delete-orphan"
    )

class Filter(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="filters")

# Many-to-Many (through association table)
team_leagues = Table(
    "team_leagues",
    Base.metadata,
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
    Column("league_id", ForeignKey("leagues.id"), primary_key=True),
)
```

## Alembic Migrations

### Creating Migrations

```bash
cd backend

# Auto-generate migration from model changes
poetry run alembic revision --autogenerate -m "add backtest_jobs table"

# Create empty migration for manual changes
poetry run alembic revision -m "add custom index"
```

### Running Migrations

```bash
# Apply all pending migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# Show current revision
poetry run alembic current

# Show migration history
poetry run alembic history
```

### Migration Best Practices

1. Always review auto-generated migrations before applying
2. Test migrations on a copy of production data
3. Include both `upgrade()` and `downgrade()` functions
4. Use descriptive migration messages

### Migration Template

```python
"""Add backtest_jobs table.

Revision ID: abc123
Revises: def456
Create Date: 2024-01-15 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "abc123"
down_revision = "def456"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "backtest_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_backtest_jobs_job_id", "backtest_jobs", ["job_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_backtest_jobs_job_id")
    op.drop_table("backtest_jobs")
```

## Async Query Patterns

### Basic Queries

```python
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

# Select all
result = await db.execute(select(Filter))
filters = list(result.scalars().all())

# Select one
result = await db.execute(select(Filter).where(Filter.id == filter_id))
filter_obj = result.scalar_one_or_none()

# Select with conditions
result = await db.execute(
    select(Filter).where(
        and_(
            Filter.user_id == user_id,
            Filter.is_active == True,
        )
    )
)
```

### Joins and Relationships

```python
# Eager loading
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Filter)
    .options(selectinload(Filter.backtest_jobs))
    .where(Filter.id == filter_id)
)

# Explicit join
result = await db.execute(
    select(Fixture, Team)
    .join(Team, Fixture.home_team_id == Team.team_id)
    .where(Fixture.league_id == league_id)
)
```

### Aggregations

```python
from sqlalchemy import func

# Count
result = await db.execute(
    select(func.count()).select_from(Filter).where(Filter.user_id == user_id)
)
count = result.scalar()

# Sum, Avg
result = await db.execute(
    select(
        func.sum(Fixture.home_team_score).label("total_goals"),
        func.avg(Fixture.home_team_score).label("avg_goals"),
    ).where(Fixture.home_team_id == team_id)
)
```

### Insert/Update/Delete

```python
# Insert
filter_obj = Filter(user_id=user_id, name="New Filter", rules=[])
db.add(filter_obj)
await db.commit()
await db.refresh(filter_obj)

# Update
filter_obj.name = "Updated Name"
await db.commit()

# Delete
await db.delete(filter_obj)
await db.commit()

# Bulk delete
await db.execute(delete(BacktestJob).where(BacktestJob.filter_id == filter_id))
await db.commit()
```

## Indexing Strategy

Add indexes for:

- Foreign keys (automatic in most cases)
- Frequently filtered columns
- Columns used in ORDER BY
- Unique constraints

```python
# In model
class Fixture(Base):
    __table_args__ = (
        Index("ix_fixture_match_date", "match_date"),
        Index("ix_fixture_league_season", "league_id", "season_type"),
    )
```
