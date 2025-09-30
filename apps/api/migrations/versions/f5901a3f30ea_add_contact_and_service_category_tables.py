"""add_contact_and_service_category_tables

Revision ID: f5901a3f30ea
Revises: 001
Create Date: 2025-10-01 00:03:10.411380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'f5901a3f30ea'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('role', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create service_categories table
    op.create_table(
        'service_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create service_contacts junction table
    op.create_table(
        'service_contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('service_id', UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_primary', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('relationship_type', sa.String(50), nullable=False, server_default='main'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('service_id', 'contact_id', name='uq_service_contact')
    )

    # Create service_service_categories junction table
    op.create_table(
        'service_service_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('service_id', UUID(as_uuid=True), nullable=False),
        sa.Column('service_category_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_category_id'], ['service_categories.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('service_id', 'service_category_id', name='uq_service_service_category')
    )

    # Create indexes
    op.create_index('idx_contacts_email', 'contacts', ['email'])
    op.create_index('idx_contacts_is_active', 'contacts', ['is_active'])
    op.create_index('idx_service_categories_code', 'service_categories', ['code'])
    op.create_index('idx_service_categories_is_active', 'service_categories', ['is_active'])
    op.create_index('idx_service_contacts_service_id', 'service_contacts', ['service_id'])
    op.create_index('idx_service_contacts_contact_id', 'service_contacts', ['contact_id'])
    op.create_index('idx_service_service_categories_service_id', 'service_service_categories', ['service_id'])
    op.create_index('idx_service_service_categories_category_id', 'service_service_categories', ['service_category_id'])

    # Seed service_categories with reference data
    op.execute("""
        INSERT INTO service_categories (id, code, name, description, color, is_active) VALUES
        (gen_random_uuid(), 'SALES', 'Sales & Marketing', 'Sales operations, lead generation, and marketing automation', '#2563eb', true),
        (gen_random_uuid(), 'HR', 'Human Resources', 'HR processes, recruitment, employee management', '#dc2626', true),
        (gen_random_uuid(), 'FINANCE', 'Finance & Accounting', 'Financial operations, accounting, and reporting', '#059669', true),
        (gen_random_uuid(), 'OPERATIONS', 'Operations', 'Business operations and process management', '#7c3aed', true),
        (gen_random_uuid(), 'CUSTOMER_SERVICE', 'Customer Service', 'Customer support and service operations', '#ea580c', true),
        (gen_random_uuid(), 'IT', 'Information Technology', 'IT infrastructure and technical services', '#0891b2', true),
        (gen_random_uuid(), 'LEGAL', 'Legal & Compliance', 'Legal services and regulatory compliance', '#4338ca', true),
        (gen_random_uuid(), 'PRODUCT', 'Product Management', 'Product development and management', '#be185d', true),
        (gen_random_uuid(), 'EXECUTIVE', 'Executive & Strategy', 'C-level and strategic decision support', '#16a34a', true)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_service_service_categories_category_id')
    op.drop_index('idx_service_service_categories_service_id')
    op.drop_index('idx_service_contacts_contact_id')
    op.drop_index('idx_service_contacts_service_id')
    op.drop_index('idx_service_categories_is_active')
    op.drop_index('idx_service_categories_code')
    op.drop_index('idx_contacts_is_active')
    op.drop_index('idx_contacts_email')

    # Drop tables
    op.drop_table('service_service_categories')
    op.drop_table('service_contacts')
    op.drop_table('service_categories')
    op.drop_table('contacts')
