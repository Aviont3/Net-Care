"""add CACFP Phase 1 — meal_type, cacfp_enrolled, cacfp_eligibility table

Revision ID: b8c4d5e6f7a8
Revises: b8c4d5e6f7a1
Create Date: 2026-07-02 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8c4d5e6f7a8'
down_revision: Union[str, None] = 'b8c4d5e6f7a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add meal_type column to activities table
    op.add_column('activities', sa.Column('meal_type', sa.String(20), nullable=True))

    # 2. Add cacfp_enrolled column to children table
    op.add_column(
        'children',
        sa.Column('cacfp_enrolled', sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # 3. Create cacfp_eligibility table
    op.create_table(
        'cacfp_eligibility',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'child_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('children.id'),
            nullable=False,
            index=True,
        ),
        sa.Column('eligibility_tier', sa.String(20), nullable=False),
        sa.Column('determination_date', sa.Date(), nullable=False),
        sa.Column('expiration_date', sa.Date(), nullable=False),
        sa.Column('determination_method', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_cacfp_eligibility_child_id', 'cacfp_eligibility', ['child_id'])
    op.create_index('ix_cacfp_eligibility_eligibility_tier', 'cacfp_eligibility', ['eligibility_tier'])
    op.create_index('ix_cacfp_eligibility_is_active', 'cacfp_eligibility', ['is_active'])


def downgrade() -> None:
    # 3. Drop cacfp_eligibility table
    op.drop_index('ix_cacfp_eligibility_is_active', table_name='cacfp_eligibility')
    op.drop_index('ix_cacfp_eligibility_eligibility_tier', table_name='cacfp_eligibility')
    op.drop_index('ix_cacfp_eligibility_child_id', table_name='cacfp_eligibility')
    op.drop_table('cacfp_eligibility')

    # 2. Drop cacfp_enrolled column from children
    op.drop_column('children', 'cacfp_enrolled')

    # 1. Drop meal_type column from activities
    op.drop_column('activities', 'meal_type')
