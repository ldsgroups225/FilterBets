"""Fix team column lengths for actual data sizes

Revision ID: fix_team_cols
Revises: fix_abbrev_len
Create Date: 2026-01-15 12:00:00.000000+00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fix_team_cols'
down_revision: str | None = 'fix_abbrev_len'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Increase column lengths to accommodate actual data."""
    # abbreviation: max 31 chars in data, set to 50 for safety
    op.alter_column(
        'teams',
        'abbreviation',
        existing_type=sa.String(20),
        type_=sa.String(50),
        existing_nullable=True
    )
    # slug: max 42 chars in data, set to 100 for safety
    op.alter_column(
        'teams',
        'slug',
        existing_type=sa.String(100),
        type_=sa.String(150),
        existing_nullable=True
    )
    # location: max 37 chars in data, current is 100 - OK
    # name: max 37 chars in data, current is 100 - OK
    # displayName: max 37 chars in data, current is 150 - OK
    # shortDisplayName: max 31 chars in data, current is 100 - OK


def downgrade() -> None:
    """Revert column lengths."""
    op.alter_column(
        'teams',
        'abbreviation',
        existing_type=sa.String(50),
        type_=sa.String(20),
        existing_nullable=True
    )
    op.alter_column(
        'teams',
        'slug',
        existing_type=sa.String(150),
        type_=sa.String(100),
        existing_nullable=True
    )
