"""add CACFP Phase 2 — food_components, cacfp_compliant, compliance_notes, cacfp_food_items

Revision ID: c1e2f3a4b5d6
Revises: b8c4d5e6f7a8
Create Date: 2026-07-02 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c1e2f3a4b5d6'
down_revision: Union[str, None] = 'b8c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add CACFP meal-tracking columns to activities table
    op.add_column('activities', sa.Column('food_components', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('activities', sa.Column('cacfp_compliant', sa.Boolean(), nullable=True))
    op.add_column('activities', sa.Column('compliance_notes', sa.Text(), nullable=True))

    # 2. Create cacfp_food_items table
    op.create_table(
        'cacfp_food_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('component_category', sa.String(50), nullable=False),
        sa.Column('sub_category', sa.String(50), nullable=True),
        sa.Column('serving_description', sa.String(200), nullable=True),
        sa.Column('is_whole_grain_rich', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_cacfp_food_items_name', 'cacfp_food_items', ['name'])
    op.create_index('ix_cacfp_food_items_component_category', 'cacfp_food_items', ['component_category'])


def downgrade() -> None:
    # 2. Drop cacfp_food_items table
    op.drop_index('ix_cacfp_food_items_component_category', table_name='cacfp_food_items')
    op.drop_index('ix_cacfp_food_items_name', table_name='cacfp_food_items')
    op.drop_table('cacfp_food_items')

    # 1. Drop CACFP columns from activities
    op.drop_column('activities', 'compliance_notes')
    op.drop_column('activities', 'cacfp_compliant')
    op.drop_column('activities', 'food_components')
