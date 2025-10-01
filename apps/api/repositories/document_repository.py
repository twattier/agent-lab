"""
Document repository for database operations.
"""
import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import Document, DocumentType, Language


class DocumentRepository:
    """Repository for document database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_document(
        self,
        project_id: uuid.UUID,
        name: str,
        content: str,
        content_hash: str,
        language: Language,
        document_type: DocumentType,
        content_vector: Optional[List[float]] = None,
        version: int = 1
    ) -> Document:
        """
        Create a new document.

        Args:
            project_id: Project ID
            name: Document name
            content: Document content
            content_hash: SHA-256 hash of content
            language: Document language
            document_type: Document type
            content_vector: Embedding vector (1536 dimensions)
            version: Document version (default 1)

        Returns:
            Created document
        """
        # Convert list to pgvector format string
        vector_str = None
        if content_vector:
            vector_str = str(content_vector)

        document = Document(
            id=uuid.uuid4(),
            project_id=project_id,
            name=name,
            content=content,
            content_hash=content_hash,
            version=version,
            language=language,
            document_type=document_type,
            content_vector=vector_str
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document or None if not found
        """
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project_id(
        self,
        project_id: uuid.UUID,
        document_type: Optional[DocumentType] = None,
        language: Optional[Language] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """
        Get documents by project ID with optional filters.

        Args:
            project_id: Project ID
            document_type: Optional document type filter
            language: Optional language filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of documents
        """
        query = select(Document).where(Document.project_id == project_id)

        if document_type:
            query = query.where(Document.document_type == document_type)

        if language:
            query = query.where(Document.language == language)

        query = query.order_by(Document.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_document(
        self,
        document_id: uuid.UUID,
        content: str,
        content_hash: str,
        version: int,
        content_vector: Optional[List[float]] = None
    ) -> Optional[Document]:
        """
        Update document content and version.

        Args:
            document_id: Document ID
            content: New content
            content_hash: New content hash
            version: New version number
            content_vector: New embedding vector

        Returns:
            Updated document or None if not found
        """
        document = await self.get_by_id(document_id)
        if not document:
            return None

        document.content = content
        document.content_hash = content_hash
        document.version = version

        if content_vector:
            document.content_vector = str(content_vector)

        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        """
        Delete document by ID.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        document = await self.get_by_id(document_id)
        if not document:
            return False

        await self.db.delete(document)
        await self.db.commit()
        return True

    async def search_by_vector(
        self,
        query_vector: List[float],
        limit: int = 10,
        project_id: Optional[uuid.UUID] = None
    ) -> List[Document]:
        """
        Search documents by vector similarity.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            project_id: Optional project ID filter

        Returns:
            List of documents ordered by similarity
        """
        # Convert vector to string format for pgvector
        vector_str = str(query_vector)

        # Build query with vector similarity
        query = select(Document).where(Document.content_vector.isnot(None))

        if project_id:
            query = query.where(Document.project_id == project_id)

        # Order by cosine distance (smaller is more similar)
        query = query.order_by(Document.content_vector.cosine_distance(vector_str)).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())
