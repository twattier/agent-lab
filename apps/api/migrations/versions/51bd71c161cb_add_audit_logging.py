"""add_audit_logging

Revision ID: 51bd71c161cb
Revises: 090f812c94b9
Create Date: 2025-10-01 14:36:12.817753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51bd71c161cb'
down_revision: Union[str, Sequence[str], None] = '090f812c94b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add audit logging table."""
    from sqlalchemy.dialects.postgresql import UUID, JSONB

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('record_id', UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),  # INSERT, UPDATE, DELETE
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', JSONB, nullable=True),
        sa.Column('new_values', JSONB, nullable=True),
        sa.Column('changed_fields', sa.ARRAY(sa.String), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True)
    )

    # Create indexes for audit_log
    op.create_index('idx_audit_log_table_name', 'audit_log', ['table_name'])
    op.create_index('idx_audit_log_record_id', 'audit_log', ['record_id'])
    op.create_index('idx_audit_log_action', 'audit_log', ['action'])
    op.create_index('idx_audit_log_timestamp', 'audit_log', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_audit_log_user_id', 'audit_log', ['user_id'])

    # Add check constraint for action
    op.create_check_constraint(
        'ck_audit_log_action',
        'audit_log',
        "action IN ('INSERT', 'UPDATE', 'DELETE')"
    )


def downgrade() -> None:
    """Remove audit logging table."""
    op.drop_index('idx_audit_log_user_id', table_name='audit_log')
    op.drop_index('idx_audit_log_timestamp', table_name='audit_log')
    op.drop_index('idx_audit_log_action', table_name='audit_log')
    op.drop_index('idx_audit_log_record_id', table_name='audit_log')
    op.drop_index('idx_audit_log_table_name', table_name='audit_log')
    op.drop_table('audit_log')
