"""Fix team abbreviation column length

Revision ID: fix_abbrev_len
Revises: 41e2e0718d69
Create Date: 2026-01-15 11:35:00.000000+00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fix_abbrev_len'
down_revision: str | None = '41e2e0718d69'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Increase abbreviation column length from 10 to 20."""
    op.alter_column(
        'teams',
        'abbreviation',
        existing_type=sa.String(10),
        type_=sa.String(20),
        existing_nullable=True
    )


def downgrade() -> None:
    """Revert abbreviation column length to 10."""
    op.alter_column(
        'teams',
        'abbreviation',
        existing_type=sa.String(20),
        type_=sa.String(10),
        existing_nullable=True
    )
