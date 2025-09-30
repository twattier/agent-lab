"""Initial schema with pgvector support

Revision ID: 001
Revises:
Create Date: 2025-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create business_domain_enum
    business_domain_enum = sa.Enum(
        'healthcare',
        'finance',
        'education',
        'government',
        'technology',
        'retail',
        'manufacturing',
        name='business_domain_enum'
    )
    business_domain_enum.create(op.get_bind())

    # Create project_type_enum
    project_type_enum = sa.Enum(
        'web_application',
        'mobile_app',
        'api_service',
        'data_pipeline',
        'ml_model',
        'automation_script',
        name='project_type_enum'
    )
    project_type_enum.create(op.get_bind())

    # Create project_status_enum
    project_status_enum = sa.Enum(
        'draft',
        'planning',
        'in_progress',
        'review',
        'completed',
        'on_hold',
        'cancelled',
        name='project_status_enum'
    )
    project_status_enum.create(op.get_bind())

    # Create implementation_types table
    op.create_table(
        'implementation_types',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('business_domain', business_domain_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create services table
    op.create_table(
        'services',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('client_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('service_id', UUID(as_uuid=True), nullable=False),
        sa.Column('project_type', project_type_enum, nullable=False),
        sa.Column('implementation_type_id', UUID(as_uuid=True), nullable=True),
        sa.Column('status', project_status_enum, nullable=False, server_default='draft'),
        sa.Column('workflow_state', sa.JSON(), nullable=True),
        sa.Column('claude_code_path', sa.String(500), nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True),  # Will be converted to vector type
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['implementation_type_id'], ['implementation_types.id'], ),
    )

    # Convert embedding column to vector type
    op.execute('ALTER TABLE projects ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)')

    # Create indexes
    op.create_index('idx_clients_business_domain', 'clients', ['business_domain'])
    op.create_index('idx_services_client_id', 'services', ['client_id'])
    op.create_index('idx_projects_service_id', 'projects', ['service_id'])
    op.create_index('idx_projects_status', 'projects', ['status'])
    op.create_index('idx_projects_project_type', 'projects', ['project_type'])

    # Create vector similarity index for pgvector
    op.execute('CREATE INDEX idx_projects_embedding_cosine ON projects USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_projects_embedding_cosine')
    op.drop_index('idx_projects_project_type')
    op.drop_index('idx_projects_status')
    op.drop_index('idx_projects_service_id')
    op.drop_index('idx_services_client_id')
    op.drop_index('idx_clients_business_domain')

    # Drop tables
    op.drop_table('projects')
    op.drop_table('services')
    op.drop_table('clients')
    op.drop_table('implementation_types')

    # Drop enums
    sa.Enum(name='project_status_enum').drop(op.get_bind())
    sa.Enum(name='project_type_enum').drop(op.get_bind())
    sa.Enum(name='business_domain_enum').drop(op.get_bind())

    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS vector')