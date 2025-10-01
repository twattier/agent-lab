"""
Document version repository for database operations.
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import DocumentVersion


class DocumentVersionRepository:
    """Repository for document version database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_version(
        self,
        document_id: uuid.UUID,
        version: int,
        content: str,
        content_hash: str,
        created_by: uuid.UUID,
        change_summary: Optional[str] = None
    ) -> DocumentVersion:
        """
        Create a new document version.

        Args:
            document_id: Document ID
            version: Version number
            content: Document content snapshot
            content_hash: SHA-256 hash of content
            created_by: User ID who made the change
            change_summary: Optional summary of changes

        Returns:
            Created document version
        """
        doc_version = DocumentVersion(
            id=uuid.uuid4(),
            document_id=document_id,
            version=version,
            content=content,
            content_hash=content_hash,
            change_summary=change_summary,
            created_by=created_by
        )
        self.db.add(doc_version)
        await self.db.commit()
        await self.db.refresh(doc_version)
        return doc_version

    async def get_by_document_id(
        self,
        document_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[DocumentVersion]:
        """
        Get version history for a document.

        Args:
            document_id: Document ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of document versions ordered by version DESC
        """
        query = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_version_by_number(
        self,
        document_id: uuid.UUID,
        version: int
    ) -> Optional[DocumentVersion]:
        """
        Get specific version of a document.

        Args:
            document_id: Document ID
            version: Version number

        Returns:
            Document version or None if not found
        """
        result = await self.db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version == version
            )
        )
        return result.scalar_one_or_none()
