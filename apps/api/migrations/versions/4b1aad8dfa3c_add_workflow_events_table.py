"""add_workflow_events_table

Revision ID: 4b1aad8dfa3c
Revises: c56eafd5499e
Create Date: 2025-10-01 11:39:05.702840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4b1aad8dfa3c'
down_revision: Union[str, Sequence[str], None] = 'c56eafd5499e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create WorkflowEventType enum
    workflow_event_type = postgresql.ENUM(
        'stage_advance',
        'gate_approved',
        'gate_rejected',
        'manual_override',
        name='workfloweventtype',
        create_type=True
    )
    workflow_event_type.create(op.get_bind(), checkfirst=True)

    # Create workflow_events table
    op.create_table(
        'workflow_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', workflow_event_type, nullable=False),
        sa.Column('from_stage', sa.String(100), nullable=True),
        sa.Column('to_stage', sa.String(100), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_workflow_event_project_id', 'workflow_events', ['project_id'])
    op.create_index('idx_workflow_event_timestamp', 'workflow_events', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_workflow_event_type', 'workflow_events', ['event_type'])
    op.create_index('idx_workflow_event_project_type', 'workflow_events', ['project_id', 'event_type'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_workflow_event_project_type', 'workflow_events')
    op.drop_index('idx_workflow_event_type', 'workflow_events')
    op.drop_index('idx_workflow_event_timestamp', 'workflow_events')
    op.drop_index('idx_workflow_event_project_id', 'workflow_events')

    # Drop table
    op.drop_table('workflow_events')

    # Drop enum
    workflow_event_type = postgresql.ENUM(
        'stage_advance',
        'gate_approved',
        'gate_rejected',
        'manual_override',
        name='workfloweventtype',
        create_type=False
    )
    workflow_event_type.drop(op.get_bind(), checkfirst=True)
