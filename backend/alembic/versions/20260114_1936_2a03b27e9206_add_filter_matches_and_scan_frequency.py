"""add_filter_matches_and_scan_frequency

Revision ID: 2a03b27e9206
Revises: 2aaaf9e8fd7f
Create Date: 2026-01-14 19:36:46.682583+00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2a03b27e9206'
down_revision: str | None = '2aaaf9e8fd7f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create filter_matches table
    op.create_table('filter_matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filter_id', sa.Integer(), nullable=False),
    sa.Column('fixture_id', sa.Integer(), nullable=False),
    sa.Column('matched_at', sa.DateTime(), nullable=False),
    sa.Column('notification_sent', sa.Boolean(), nullable=False),
    sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
    sa.Column('notification_error', sa.String(length=500), nullable=True),
    sa.Column('bet_result', sa.Enum('PENDING', 'WIN', 'LOSS', 'PUSH', name='betresult', native_enum=False, length=20), nullable=False),
    sa.ForeignKeyConstraint(['filter_id'], ['filters.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['fixture_id'], ['fixtures.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('filter_id', 'fixture_id', name='uq_filter_fixture')
    )
    op.create_index(op.f('ix_filter_matches_filter_id'), 'filter_matches', ['filter_id'], unique=False)
    op.create_index(op.f('ix_filter_matches_fixture_id'), 'filter_matches', ['fixture_id'], unique=False)
    op.create_index(op.f('ix_filter_matches_id'), 'filter_matches', ['id'], unique=False)
    
    # Add scan_frequency to users
    op.add_column('users', sa.Column('scan_frequency', sa.Enum('2x', '4x', '6x', name='scanfrequency', native_enum=False, length=5), nullable=False, server_default='2x'))


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('users', 'scan_frequency')
    op.drop_index(op.f('ix_filter_matches_id'), table_name='filter_matches')
    op.drop_index(op.f('ix_filter_matches_fixture_id'), table_name='filter_matches')
    op.drop_index(op.f('ix_filter_matches_filter_id'), table_name='filter_matches')
    op.drop_table('filter_matches')
