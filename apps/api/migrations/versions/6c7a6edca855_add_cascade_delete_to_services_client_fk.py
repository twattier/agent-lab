"""add_cascade_delete_to_services_client_fk

Revision ID: 6c7a6edca855
Revises: f5901a3f30ea
Create Date: 2025-10-01 00:43:55.581380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c7a6edca855'
down_revision: Union[str, Sequence[str], None] = 'f5901a3f30ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CASCADE delete to services.client_id foreign key."""
    # Drop existing foreign key constraint
    op.drop_constraint('services_client_id_fkey', 'services', type_='foreignkey')

    # Recreate foreign key with ON DELETE CASCADE
    op.create_foreign_key(
        'services_client_id_fkey',
        'services',
        'clients',
        ['client_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Remove CASCADE delete from services.client_id foreign key."""
    # Drop foreign key with CASCADE
    op.drop_constraint('services_client_id_fkey', 'services', type_='foreignkey')

    # Recreate foreign key without ON DELETE CASCADE
    op.create_foreign_key(
        'services_client_id_fkey',
        'services',
        'clients',
        ['client_id'],
        ['id']
    )
