"""add parent invite_code and user_id fields

Revision ID: a7f3b2c1d4e5
Revises: 3c22baf615ad
Create Date: 2026-06-08 02:38:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a7f3b2c1d4e5'
down_revision: Union[str, None] = '3c22baf615ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add invite_code column to parents table
    op.add_column('parents', sa.Column('invite_code', sa.String(64), nullable=True))
    op.create_index('ix_parents_invite_code', 'parents', ['invite_code'], unique=True)

    # Add user_id column to parents table (links to users table)
    op.add_column('parents', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_parents_user_id', 'parents', ['user_id'])
    op.create_foreign_key('fk_parents_user_id', 'parents', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_parents_user_id', 'parents', type_='foreignkey')
    op.drop_index('ix_parents_user_id', table_name='parents')
    op.drop_column('parents', 'user_id')
    op.drop_index('ix_parents_invite_code', table_name='parents')
    op.drop_column('parents', 'invite_code')
