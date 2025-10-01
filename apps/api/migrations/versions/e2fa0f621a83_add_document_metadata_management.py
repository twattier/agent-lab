"""add_document_metadata_management

Revision ID: e2fa0f621a83
Revises: 4b1aad8dfa3c
Create Date: 2025-10-01 13:13:37.009536

Migration: Document Metadata Management (Story 2.4)
===================================================

This migration adds comprehensive document tracking with:
- Document model with semantic search (pgvector)
- DocumentVersion model for change history
- Comment model for collaboration
- CASCADE delete relationships

PRODUCTION ROLLBACK PROCEDURE:
------------------------------
⚠️  CRITICAL: Follow this procedure exactly to safely rollback in production

1. **Pre-Rollback Checks:**
   ```bash
   # Verify current revision
   alembic current
   # Should show: e2fa0f621a83 (head)

   # Check for existing document data
   psql -U agentlab -d agentlab -c "SELECT COUNT(*) FROM document;"
   ```

2. **Backup Database (MANDATORY):**
   ```bash
   # Create full database backup before rollback
   pg_dump -U agentlab -d agentlab -Fc -f backup_before_rollback_$(date +%Y%m%d_%H%M%S).dump

   # Verify backup was created
   ls -lh backup_before_rollback_*.dump
   ```

3. **Execute Rollback:**
   ```bash
   # Downgrade to previous revision
   alembic downgrade -1

   # Verify rollback succeeded
   alembic current
   # Should show: 4b1aad8dfa3c
   ```

4. **Post-Rollback Verification:**
   ```bash
   # Verify tables removed
   psql -U agentlab -d agentlab -c "\dt document*"
   # Should return: Did not find any relation named "document*"

   # Verify enums removed
   psql -U agentlab -d agentlab -c "\dT language"
   psql -U agentlab -d agentlab -c "\dT documenttype"
   # Should return: Did not find any relation
   ```

5. **Restore Data (if needed):**
   ```bash
   # If rollback was a mistake, restore from backup
   pg_restore -U agentlab -d agentlab -c backup_before_rollback_YYYYMMDD_HHMMSS.dump
   ```

DATA LOSS WARNING:
-----------------
⚠️  Rolling back this migration will PERMANENTLY DELETE:
   - All documents and their content
   - All document version history
   - All comments on documents

   Ensure you have a valid backup before proceeding!

DEPENDENCIES:
------------
- Requires: pgvector extension (will remain installed)
- Blocks: Any future migrations depending on document tables
- Previous migration: 4b1aad8dfa3c (workflow_events)

TESTING ROLLBACK IN STAGING:
----------------------------
Always test rollback procedure in staging environment first:

```bash
# In staging environment
export DATABASE_URL="postgresql://user:pass@staging-db:5432/dbname"
alembic downgrade -1
# Verify functionality
alembic upgrade +1
# Verify re-upgrade works
```

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'e2fa0f621a83'
down_revision: Union[str, Sequence[str], None] = '4b1aad8dfa3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Create Language enum
    op.execute("CREATE TYPE language AS ENUM ('fr', 'en');")

    # Create DocumentType enum
    op.execute("CREATE TYPE documenttype AS ENUM ('prd', 'architecture', 'requirements', 'feedback', 'other');")

    # Create document table
    op.create_table(
        'document',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('language', sa.Enum('fr', 'en', name='language'), nullable=False, server_default='en'),
        sa.Column('document_type', sa.Enum('prd', 'architecture', 'requirements', 'feedback', 'other', name='documenttype'), nullable=False),
        sa.Column('content_vector', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Create indexes for document table
    op.create_index('idx_document_project_id', 'document', ['project_id'])
    op.create_index('idx_document_type', 'document', ['document_type'])
    op.create_index('idx_document_language', 'document', ['language'])
    op.execute("CREATE INDEX idx_document_vector ON document USING ivfflat (content_vector vector_cosine_ops);")

    # Create document_version table
    op.create_table(
        'document_version',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('document.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Create indexes for document_version table
    op.create_index('idx_document_version_document_id', 'document_version', ['document_id'])
    op.create_index('idx_document_version_created_at', 'document_version', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # Create comment table
    op.create_table(
        'comment',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('document.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # Create indexes for comment table
    op.create_index('idx_comment_document_id', 'comment', ['document_id'])
    op.create_index('idx_comment_user_id', 'comment', ['user_id'])
    op.create_index('idx_comment_resolved', 'comment', ['resolved'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_index('idx_comment_resolved', table_name='comment')
    op.drop_index('idx_comment_user_id', table_name='comment')
    op.drop_index('idx_comment_document_id', table_name='comment')
    op.drop_table('comment')

    op.drop_index('idx_document_version_created_at', table_name='document_version')
    op.drop_index('idx_document_version_document_id', table_name='document_version')
    op.drop_table('document_version')

    op.execute("DROP INDEX IF EXISTS idx_document_vector;")
    op.drop_index('idx_document_language', table_name='document')
    op.drop_index('idx_document_type', table_name='document')
    op.drop_index('idx_document_project_id', table_name='document')
    op.drop_table('document')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS documenttype;")
    op.execute("DROP TYPE IF EXISTS language;")
