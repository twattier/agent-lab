"""story_3_2_gate_management_tables

Revision ID: 3c0d9b26a0a0
Revises: 126b23b40b72
Create Date: 2025-10-02 01:02:18.822862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c0d9b26a0a0'
down_revision: Union[str, Sequence[str], None] = '126b23b40b72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column to workflow_gate table
    op.add_column('workflow_gate', sa.Column('status', sa.String(20), nullable=False, server_default='pending'))
    op.create_check_constraint(
        'ck_workflow_gate_status',
        'workflow_gate',
        sa.text("status IN ('pending', 'approved', 'rejected', 'blocked')")
    )

    # Create gate_reviewer table
    op.create_table(
        'gate_reviewer',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('gate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_role', sa.String(50), nullable=False),
        sa.Column('assigned_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['gate_id'], ['workflow_gate.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('gate_id', 'contact_id', name='uq_gate_reviewer_gate_contact')
    )

    # Create indexes
    op.create_index('idx_gate_reviewer_gate_id', 'gate_reviewer', ['gate_id'])
    op.create_index('idx_gate_reviewer_contact_id', 'gate_reviewer', ['contact_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_gate_reviewer_contact_id', table_name='gate_reviewer')
    op.drop_index('idx_gate_reviewer_gate_id', table_name='gate_reviewer')

    # Drop gate_reviewer table
    op.drop_table('gate_reviewer')

    # Drop check constraint and status column from workflow_gate
    op.drop_constraint('ck_workflow_gate_status', 'workflow_gate', type_='check')
    op.drop_column('workflow_gate', 'status')
