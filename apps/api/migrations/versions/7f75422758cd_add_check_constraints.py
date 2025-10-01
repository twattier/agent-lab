"""add_check_constraints

Revision ID: 7f75422758cd
Revises: e2fa0f621a83
Create Date: 2025-10-01 14:13:54.952614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f75422758cd'
down_revision: Union[str, Sequence[str], None] = '4b1aad8dfa3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add check constraints for data validation."""
    # Project constraints
    op.create_check_constraint(
        'ck_project_type',
        'projects',
        "project_type IN ('new', 'existing')"
    )

    op.create_check_constraint(
        'ck_project_status',
        'projects',
        "status IN ('draft', 'active', 'blocked', 'completed', 'archived')"
    )

    op.create_check_constraint(
        'ck_project_workflow_state',
        'projects',
        "workflow_state ? 'currentStage' AND workflow_state ? 'completedStages'"
    )

    # Contact constraints - email format validation
    op.create_check_constraint(
        'ck_contact_email',
        'contacts',
        "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'"
    )

    # Note: Document and WorkflowEvent constraints will be added when those tables are created
    # in their respective migrations to avoid dependency issues


def downgrade() -> None:
    """Remove check constraints."""
    # Project constraints
    op.drop_constraint('ck_project_type', 'projects', type_='check')
    op.drop_constraint('ck_project_status', 'projects', type_='check')
    op.drop_constraint('ck_project_workflow_state', 'projects', type_='check')

    # Contact constraints
    op.drop_constraint('ck_contact_email', 'contacts', type_='check')
