"""seed_reference_data

Revision ID: 090f812c94b9
Revises: 7f75422758cd
Create Date: 2025-10-01 14:22:11.174768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '090f812c94b9'
down_revision: Union[str, Sequence[str], None] = '7f75422758cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed reference data tables."""
    # Seed implementation types
    op.execute("""
        INSERT INTO implementation_types (id, code, name, description, is_active, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'RAG', 'Retrieval-Augmented Generation', 'AI systems that combine retrieval and generation for enhanced responses', true, now(), now()),
            (gen_random_uuid(), 'AGENTIC', 'Agentic AI', 'Autonomous AI agents that can perform complex tasks and make decisions', true, now(), now()),
            (gen_random_uuid(), 'AUTOMATON', 'Automation', 'Rule-based automation systems for repetitive tasks', true, now(), now()),
            (gen_random_uuid(), 'CHATBOT', 'Chatbot', 'Conversational AI interfaces for customer interaction', true, now(), now()),
            (gen_random_uuid(), 'ANALYTICS', 'Analytics', 'AI-powered data analysis and insights generation', true, now(), now()),
            (gen_random_uuid(), 'RECOMMENDATION', 'Recommendation Engine', 'AI systems for personalized recommendations', true, now(), now())
        ON CONFLICT (code) DO NOTHING;
    """)

    # Seed service categories
    op.execute("""
        INSERT INTO service_categories (id, code, name, description, color, is_active, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'SALES', 'Sales', 'Sales and business development services', '#3B82F6', true, now(), now()),
            (gen_random_uuid(), 'HR', 'Human Resources', 'HR and talent management services', '#10B981', true, now(), now()),
            (gen_random_uuid(), 'FINANCE', 'Finance', 'Financial and accounting services', '#F59E0B', true, now(), now()),
            (gen_random_uuid(), 'OPERATIONS', 'Operations', 'Operational and logistics services', '#8B5CF6', true, now(), now()),
            (gen_random_uuid(), 'CUSTOMER_SERVICE', 'Customer Service', 'Customer support and service delivery', '#EC4899', true, now(), now()),
            (gen_random_uuid(), 'IT', 'Information Technology', 'IT infrastructure and development services', '#06B6D4', true, now(), now()),
            (gen_random_uuid(), 'LEGAL', 'Legal', 'Legal and compliance services', '#6366F1', true, now(), now()),
            (gen_random_uuid(), 'PRODUCT', 'Product Management', 'Product development and management', '#84CC16', true, now(), now()),
            (gen_random_uuid(), 'EXECUTIVE', 'Executive', 'Executive and C-level services', '#EF4444', true, now(), now())
        ON CONFLICT (code) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove reference data."""
    # Only delete if no foreign key dependencies exist
    op.execute("DELETE FROM service_service_categories;")
    op.execute("DELETE FROM project_service_categories;")
    op.execute("DELETE FROM service_categories WHERE code IN ('SALES', 'HR', 'FINANCE', 'OPERATIONS', 'CUSTOMER_SERVICE', 'IT', 'LEGAL', 'PRODUCT', 'EXECUTIVE');")
    op.execute("DELETE FROM projects WHERE implementation_type_id IS NOT NULL;")
    op.execute("DELETE FROM implementation_types WHERE code IN ('RAG', 'AGENTIC', 'AUTOMATON', 'CHATBOT', 'ANALYTICS', 'RECOMMENDATION');")

