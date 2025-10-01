"""story_3_1_bmad_template_tables

Revision ID: 126b23b40b72
Revises: b9f0d02517ea
Create Date: 2025-10-02 00:23:16.945500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision: str = '126b23b40b72'
down_revision: Union[str, Sequence[str], None] = 'b9f0d02517ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create workflow template tables."""
    # Create workflow_template table
    op.create_table(
        'workflow_template',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('template_name', sa.String(255), nullable=False),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('configuration', JSONB, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create workflow_stage table
    op.create_table(
        'workflow_stage',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('workflow_template.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stage_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )

    # Create workflow_gate table
    op.create_table(
        'workflow_gate',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('workflow_template.id', ondelete='CASCADE'), nullable=False),
        sa.Column('gate_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('stage_id', sa.String(100), nullable=False),
        sa.Column('criteria', JSONB, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
    )

    # Create indexes for performance
    op.create_index('idx_workflow_stage_template_id', 'workflow_stage', ['template_id'])
    op.create_index('idx_workflow_gate_template_id', 'workflow_gate', ['template_id'])


def downgrade() -> None:
    """Downgrade schema - Drop workflow template tables."""
    # Drop indexes first
    op.drop_index('idx_workflow_gate_template_id', table_name='workflow_gate')
    op.drop_index('idx_workflow_stage_template_id', table_name='workflow_stage')

    # Drop tables in reverse order (children first due to foreign keys)
    op.drop_table('workflow_gate')
    op.drop_table('workflow_stage')
    op.drop_table('workflow_template')
