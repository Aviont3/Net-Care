"""add photo_url to activities table

Revision ID: b8c4d5e6f7a1
Revises: a7f3b2c1d4e5
Create Date: 2026-06-10 11:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8c4d5e6f7a1'
down_revision: Union[str, None] = 'a7f3b2c1d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('activities', sa.Column('photo_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('activities', 'photo_url')
