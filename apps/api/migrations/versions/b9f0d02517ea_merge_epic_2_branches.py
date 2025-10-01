"""merge_epic_2_branches

Revision ID: b9f0d02517ea
Revises: 51bd71c161cb, e2fa0f621a83
Create Date: 2025-10-01 15:46:34.748942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9f0d02517ea'
down_revision: Union[str, Sequence[str], None] = ('51bd71c161cb', 'e2fa0f621a83')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
