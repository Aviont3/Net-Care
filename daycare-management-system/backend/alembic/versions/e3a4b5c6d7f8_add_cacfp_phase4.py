"""add CACFP Phase 4 — cacfp_audit_log table

Revision ID: e3a4b5c6d7f8
Revises: d2f3a4b5c6e7
Create Date: 2026-07-02 17:22:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e3a4b5c6d7f8'
down_revision: Union[str, None] = 'd2f3a4b5c6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cacfp_audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        # What happened
        sa.Column('action',       sa.String(50),  nullable=False),
        sa.Column('entity_type',  sa.String(50),  nullable=False),
        sa.Column('entity_id',    postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_changed', sa.String(100), nullable=True),
        sa.Column('old_value',    sa.Text(),       nullable=True),
        sa.Column('new_value',    sa.Text(),       nullable=True),
        sa.Column('reason',       sa.Text(),       nullable=True),
        # Who did it
        sa.Column(
            'performed_by',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id'),
            nullable=False,
        ),
        # Timestamps (no updated_at — rows are immutable)
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_cacfp_audit_log_action',       'cacfp_audit_log', ['action'])
    op.create_index('ix_cacfp_audit_log_entity_type',  'cacfp_audit_log', ['entity_type'])
    op.create_index('ix_cacfp_audit_log_entity_id',    'cacfp_audit_log', ['entity_id'])
    op.create_index('ix_cacfp_audit_log_performed_by', 'cacfp_audit_log', ['performed_by'])
    # Composite index for the common query pattern: all events for an entity
    op.create_index(
        'ix_cacfp_audit_log_entity_type_id',
        'cacfp_audit_log',
        ['entity_type', 'entity_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_cacfp_audit_log_entity_type_id', table_name='cacfp_audit_log')
    op.drop_index('ix_cacfp_audit_log_performed_by',   table_name='cacfp_audit_log')
    op.drop_index('ix_cacfp_audit_log_entity_id',      table_name='cacfp_audit_log')
    op.drop_index('ix_cacfp_audit_log_entity_type',    table_name='cacfp_audit_log')
    op.drop_index('ix_cacfp_audit_log_action',         table_name='cacfp_audit_log')
    op.drop_table('cacfp_audit_log')
