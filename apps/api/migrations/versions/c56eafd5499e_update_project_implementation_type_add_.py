"""update_project_implementation_type_add_junction_tables

Revision ID: c56eafd5499e
Revises: 6c7a6edca855
Create Date: 2025-10-01 09:31:34.404602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision: str = 'c56eafd5499e'
down_revision: Union[str, Sequence[str], None] = '6c7a6edca855'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Drop old enums and recreate with Story 2.2 values
    # First, alter projects table to use string temporarily
    op.execute("ALTER TABLE projects ALTER COLUMN project_type TYPE varchar(50)")
    op.execute("ALTER TABLE projects ALTER COLUMN status TYPE varchar(50)")

    # Drop old enums
    op.execute("DROP TYPE IF EXISTS project_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS project_status_enum CASCADE")

    # Create new enums with Story 2.2 values
    op.execute("CREATE TYPE project_type_enum AS ENUM ('new', 'existing')")
    op.execute("CREATE TYPE project_status_enum AS ENUM ('draft', 'active', 'blocked', 'completed', 'archived')")

    # 2. Update implementation_types table
    # Add new columns
    op.add_column('implementation_types',
                  sa.Column('code', sa.String(50), nullable=True, unique=True))
    op.add_column('implementation_types',
                  sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('implementation_types',
                  sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

    # Update created_at to have timezone
    op.execute("ALTER TABLE implementation_types ALTER COLUMN created_at TYPE timestamp with time zone")

    # Remove unique constraint from name
    op.drop_constraint('implementation_types_name_key', 'implementation_types', type_='unique')

    # Seed data for implementation types with codes
    op.execute("""
        INSERT INTO implementation_types (id, code, name, description, is_active, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'RAG', 'Retrieval-Augmented Generation', 'Systems that combine retrieval and generation for enhanced AI responses', true, now(), now()),
        (gen_random_uuid(), 'AGENTIC', 'Agentic AI', 'Autonomous AI agents capable of independent decision-making and task execution', true, now(), now()),
        (gen_random_uuid(), 'AUTOMATON', 'Process Automation', 'Rule-based automation systems for workflow and business process automation', true, now(), now()),
        (gen_random_uuid(), 'CHATBOT', 'Conversational AI', 'Interactive chat-based AI systems for customer service and support', true, now(), now()),
        (gen_random_uuid(), 'ANALYTICS', 'AI Analytics', 'Data analysis and insights generation using AI/ML techniques', true, now(), now()),
        (gen_random_uuid(), 'RECOMMENDATION', 'Recommendation Engine', 'Personalized recommendation systems for content or product suggestions', true, now(), now())
        ON CONFLICT DO NOTHING
    """)

    # Make code NOT NULL after seeding
    op.alter_column('implementation_types', 'code', nullable=False)

    # Create indexes for implementation_types
    op.create_index('idx_implementation_type_code', 'implementation_types', ['code'])
    op.create_index('idx_implementation_type_active', 'implementation_types', ['is_active'])

    # 3. Update projects table
    # Update existing data to new enum values (draft -> draft, others to draft)
    op.execute("""
        UPDATE projects
        SET project_type = 'new'
        WHERE project_type NOT IN ('new', 'existing')
    """)
    op.execute("""
        UPDATE projects
        SET status = CASE
            WHEN status = 'draft' THEN 'draft'
            WHEN status = 'completed' THEN 'completed'
            WHEN status IN ('in_progress', 'planning') THEN 'active'
            ELSE 'draft'
        END
    """)

    # Make description NOT NULL with default for existing rows
    op.execute("UPDATE projects SET description = '' WHERE description IS NULL")
    op.alter_column('projects', 'description', nullable=False)

    # Update workflow_state to JSONB and NOT NULL with default
    op.execute("UPDATE projects SET workflow_state = '{}' WHERE workflow_state IS NULL")
    op.execute("ALTER TABLE projects ALTER COLUMN workflow_state TYPE jsonb USING workflow_state::jsonb")
    op.alter_column('projects', 'workflow_state',
                   nullable=False,
                   server_default='{}')

    # Update timestamp columns to have timezone
    op.execute("ALTER TABLE projects ALTER COLUMN created_at TYPE timestamp with time zone")
    op.execute("ALTER TABLE projects ALTER COLUMN updated_at TYPE timestamp with time zone")

    # Now convert back to enum types
    op.execute("ALTER TABLE projects ALTER COLUMN project_type TYPE project_type_enum USING project_type::project_type_enum")
    op.execute("ALTER TABLE projects ALTER COLUMN status TYPE project_status_enum USING status::project_status_enum")

    # Drop the vector embedding column (not in Story 2.2 requirements)
    op.drop_column('projects', 'embedding')

    # Update foreign key constraints to add CASCADE and SET NULL
    op.drop_constraint('projects_service_id_fkey', 'projects', type_='foreignkey')
    op.drop_constraint('projects_implementation_type_id_fkey', 'projects', type_='foreignkey')

    op.create_foreign_key('projects_service_id_fkey', 'projects', 'services',
                         ['service_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('projects_implementation_type_id_fkey', 'projects', 'implementation_types',
                         ['implementation_type_id'], ['id'], ondelete='SET NULL')

    # Create additional indexes for projects
    op.create_index('idx_project_implementation_type_id', 'projects', ['implementation_type_id'])
    op.create_index('idx_project_service_status', 'projects', ['service_id', 'status'])
    op.create_index('idx_project_service_impl_type', 'projects', ['service_id', 'implementation_type_id'])

    # 4. Create project_contacts junction table
    op.create_table(
        'project_contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', UUID(as_uuid=True), nullable=False),
        sa.Column('contact_type', sa.String(50), nullable=False, server_default='stakeholder'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'contact_id', 'contact_type', name='uq_project_contact')
    )

    # Create indexes for project_contacts
    op.create_index('idx_project_contact_project_id', 'project_contacts', ['project_id'])
    op.create_index('idx_project_contact_contact_id', 'project_contacts', ['contact_id'])
    op.create_index('idx_project_contact_active', 'project_contacts', ['project_id', 'is_active'])

    # 5. Create project_service_categories junction table
    op.create_table(
        'project_service_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('service_category_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_category_id'], ['service_categories.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'service_category_id', name='uq_project_service_category')
    )

    # Create indexes for project_service_categories
    op.create_index('idx_project_service_category_project_id', 'project_service_categories', ['project_id'])
    op.create_index('idx_project_service_category_category_id', 'project_service_categories', ['service_category_id'])


def downgrade() -> None:
    """Downgrade schema."""

    # Drop indexes for project_service_categories
    op.drop_index('idx_project_service_category_category_id')
    op.drop_index('idx_project_service_category_project_id')

    # Drop project_service_categories table
    op.drop_table('project_service_categories')

    # Drop indexes for project_contacts
    op.drop_index('idx_project_contact_active')
    op.drop_index('idx_project_contact_contact_id')
    op.drop_index('idx_project_contact_project_id')

    # Drop project_contacts table
    op.drop_table('project_contacts')

    # Drop new project indexes
    op.drop_index('idx_project_service_impl_type')
    op.drop_index('idx_project_service_status')
    op.drop_index('idx_project_implementation_type_id')

    # Drop implementation_types indexes
    op.drop_index('idx_implementation_type_active')
    op.drop_index('idx_implementation_type_code')

    # Revert implementation_types table changes
    op.drop_column('implementation_types', 'updated_at')
    op.drop_column('implementation_types', 'is_active')
    op.drop_column('implementation_types', 'code')

    # Delete seeded implementation types (optional, or keep them)
    op.execute("DELETE FROM implementation_types WHERE code IN ('RAG', 'AGENTIC', 'AUTOMATON', 'CHATBOT', 'ANALYTICS', 'RECOMMENDATION')")

    # Restore unique constraint on name
    op.create_unique_constraint('implementation_types_name_key', 'implementation_types', ['name'])

    # Revert projects table
    # Add embedding column back
    op.add_column('projects', sa.Column('embedding', sa.Text(), nullable=True))
    op.execute('ALTER TABLE projects ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)')
    op.execute('CREATE INDEX idx_projects_embedding_cosine ON projects USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')

    # Revert workflow_state
    op.alter_column('projects', 'workflow_state', nullable=True, server_default=None)
    op.execute("ALTER TABLE projects ALTER COLUMN workflow_state TYPE json USING workflow_state::json")

    # Revert description to nullable
    op.alter_column('projects', 'description', nullable=True)

    # Revert foreign keys
    op.drop_constraint('projects_implementation_type_id_fkey', 'projects', type_='foreignkey')
    op.drop_constraint('projects_service_id_fkey', 'projects', type_='foreignkey')

    op.create_foreign_key('projects_service_id_fkey', 'projects', 'services', ['service_id'], ['id'])
    op.create_foreign_key('projects_implementation_type_id_fkey', 'projects', 'implementation_types',
                         ['implementation_type_id'], ['id'])

    # Revert to old enum values
    op.execute("ALTER TABLE projects ALTER COLUMN project_type TYPE varchar(50)")
    op.execute("ALTER TABLE projects ALTER COLUMN status TYPE varchar(50)")

    op.execute("DROP TYPE IF EXISTS project_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS project_status_enum CASCADE")

    # Recreate old enums
    op.execute("CREATE TYPE project_type_enum AS ENUM ('web_application', 'mobile_app', 'api_service', 'data_pipeline', 'ml_model', 'automation_script')")
    op.execute("CREATE TYPE project_status_enum AS ENUM ('draft', 'planning', 'in_progress', 'review', 'completed', 'on_hold', 'cancelled')")

    op.execute("ALTER TABLE projects ALTER COLUMN project_type TYPE project_type_enum USING 'web_application'::project_type_enum")
    op.execute("ALTER TABLE projects ALTER COLUMN status TYPE project_status_enum USING 'draft'::project_status_enum")
