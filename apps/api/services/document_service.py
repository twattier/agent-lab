"""
Document service for business logic and orchestration.
"""
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Document, DocumentType, Language
from repositories.document_repository import DocumentRepository
from repositories.document_version_repository import DocumentVersionRepository
from services.embedding_service import get_embedding_service
from core.document_utils import generate_content_hash


class DocumentService:
    """Service for document business logic."""

    def __init__(self, db: AsyncSession):
        """
        Initialize service.

        Args:
            db: Async database session
        """
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.version_repo = DocumentVersionRepository(db)
        self.embedding_service = get_embedding_service()

    async def create_document_with_version(
        self,
        project_id: uuid.UUID,
        name: str,
        content: str,
        language: Language,
        document_type: DocumentType,
        created_by: uuid.UUID
    ) -> Document:
        """
        Create a new document with initial version.

        Args:
            project_id: Project ID
            name: Document name
            content: Document content
            language: Document language
            document_type: Document type
            created_by: User ID creating the document

        Returns:
            Created document
        """
        # Generate content hash
        content_hash = generate_content_hash(content)

        # Generate embedding vector
        try:
            content_vector = await self.embedding_service.generate_embedding(content)
        except Exception:
            # If embedding generation fails, continue without it
            content_vector = None

        # Create document
        document = await self.document_repo.create_document(
            project_id=project_id,
            name=name,
            content=content,
            content_hash=content_hash,
            language=language,
            document_type=document_type,
            content_vector=content_vector,
            version=1
        )

        # Create initial version record
        await self.version_repo.create_version(
            document_id=document.id,
            version=1,
            content=content,
            content_hash=content_hash,
            created_by=created_by,
            change_summary="Initial version"
        )

        return document

    async def update_document_with_versioning(
        self,
        document_id: uuid.UUID,
        new_content: str,
        updated_by: uuid.UUID,
        change_summary: Optional[str] = None
    ) -> Optional[Document]:
        """
        Update document with automatic versioning if content changed.

        Args:
            document_id: Document ID
            new_content: New document content
            updated_by: User ID making the update
            change_summary: Optional summary of changes

        Returns:
            Updated document or None if not found
        """
        # Get existing document
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            return None

        # Generate new content hash
        new_hash = generate_content_hash(new_content)

        # Check if content actually changed
        if new_hash == document.content_hash:
            # Content unchanged, return existing document
            return document

        # Content changed, increment version
        new_version = document.version + 1

        # Generate new embedding vector
        try:
            content_vector = await self.embedding_service.generate_embedding(new_content)
        except Exception:
            # If embedding generation fails, keep existing vector
            content_vector = None

        # Update document
        updated_document = await self.document_repo.update_document(
            document_id=document_id,
            content=new_content,
            content_hash=new_hash,
            version=new_version,
            content_vector=content_vector
        )

        # Create version record
        if updated_document:
            await self.version_repo.create_version(
                document_id=document_id,
                version=new_version,
                content=new_content,
                content_hash=new_hash,
                created_by=updated_by,
                change_summary=change_summary
            )

        return updated_document

    async def get_document_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document or None if not found
        """
        return await self.document_repo.get_by_id(document_id)

    async def get_project_documents(
        self,
        project_id: uuid.UUID,
        document_type: Optional[DocumentType] = None,
        language: Optional[Language] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """
        Get documents for a project with optional filters.

        Args:
            project_id: Project ID
            document_type: Optional document type filter
            language: Optional language filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of documents
        """
        return await self.document_repo.get_by_project_id(
            project_id=project_id,
            document_type=document_type,
            language=language,
            limit=limit,
            offset=offset
        )

    async def search_similar_documents(
        self,
        query_text: str,
        limit: int = 10,
        project_id: Optional[uuid.UUID] = None
    ) -> List[Document]:
        """
        Search for similar documents using semantic search.

        Args:
            query_text: Query text
            limit: Maximum number of results
            project_id: Optional project ID filter

        Returns:
            List of similar documents
        """
        # Generate query embedding
        try:
            query_vector = await self.embedding_service.generate_embedding(query_text)
        except Exception:
            # If embedding generation fails, return empty list
            return []

        # Search by vector similarity
        return await self.document_repo.search_by_vector(
            query_vector=query_vector,
            limit=limit,
            project_id=project_id
        )

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        return await self.document_repo.delete_document(document_id)
