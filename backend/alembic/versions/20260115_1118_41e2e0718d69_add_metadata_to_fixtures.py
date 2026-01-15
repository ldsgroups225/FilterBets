"""add_metadata_to_fixtures

Revision ID: 41e2e0718d69
Revises: 2a03b27e9206
Create Date: 2026-01-15 11:18:56.858428+00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '41e2e0718d69'
down_revision: str | None = '2a03b27e9206'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Add metadata JSONB column to fixtures table
    op.add_column('fixtures', sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Create GIN index for faster JSONB queries
    op.create_index(
        'ix_fixtures_metadata',
        'fixtures',
        ['metadata'],
        unique=False,
        postgresql_using='gin'
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop index first
    op.drop_index('ix_fixtures_metadata', table_name='fixtures')
    
    # Drop metadata column
    op.drop_column('fixtures', 'metadata')
