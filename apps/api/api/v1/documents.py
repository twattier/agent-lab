"""
Document API endpoints.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import (
    CreateDocumentRequest,
    UpdateDocumentRequest,
    DocumentResponse,
    DocumentVersionResponse,
    CreateCommentRequest,
    CommentResponse,
    DocumentType,
    Language
)
from services.document_service import DocumentService
from repositories.document_version_repository import DocumentVersionRepository
from repositories.comment_repository import CommentRepository

router = APIRouter(prefix="/documents", tags=["documents"])


# Dependency to get document service
def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """Get document service instance."""
    return DocumentService(db)


def get_version_repo(db: AsyncSession = Depends(get_db)) -> DocumentVersionRepository:
    """Get document version repository instance."""
    return DocumentVersionRepository(db)


def get_comment_repo(db: AsyncSession = Depends(get_db)) -> CommentRepository:
    """Get comment repository instance."""
    return CommentRepository(db)


@router.post(
    "/projects/{project_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    description="Create a new document with initial version and generate embeddings."
)
async def create_document(
    project_id: uuid.UUID,
    request: CreateDocumentRequest,
    service: DocumentService = Depends(get_document_service)
):
    """
    Create a new document.

    - **project_id**: UUID of the project
    - **name**: Document name (1-255 characters)
    - **content**: Document content (required)
    - **language**: Language ('fr' or 'en', default 'en')
    - **documentType**: Document type (prd, architecture, requirements, feedback, other)

    Returns the created document with version 1.
    """
    # TODO: Verify project exists (add project repository check)
    # For now, assuming project exists

    # Use a mock user ID (in production, get from auth context)
    created_by = uuid.uuid4()

    try:
        document = await service.create_document_with_version(
            project_id=project_id,
            name=request.name,
            content=request.content,
            language=request.language,
            document_type=request.documentType,
            created_by=created_by
        )
        return DocumentResponse.model_validate(document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create document: {str(e)}"
        )


@router.get(
    "/projects/{project_id}/documents",
    response_model=List[DocumentResponse],
    summary="List project documents",
    description="Get all documents for a project with optional filters."
)
async def list_project_documents(
    project_id: uuid.UUID,
    type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    language: Optional[Language] = Query(None, description="Filter by language"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    service: DocumentService = Depends(get_document_service)
):
    """
    List all documents for a project.

    - **project_id**: UUID of the project
    - **type**: Optional document type filter
    - **language**: Optional language filter
    - **page**: Page number (starting from 1)
    - **limit**: Maximum results per page

    Returns list of documents with pagination.
    """
    offset = (page - 1) * limit

    documents = await service.get_project_documents(
        project_id=project_id,
        document_type=type,
        language=language,
        limit=limit,
        offset=offset
    )

    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    description="Get a specific document by ID."
)
async def get_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service)
):
    """
    Get document by ID.

    - **document_id**: UUID of the document

    Returns the document details.
    """
    document = await service.get_document_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    return DocumentResponse.model_validate(document)


@router.put(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Update document",
    description="Update document content with automatic versioning."
)
async def update_document(
    document_id: uuid.UUID,
    request: UpdateDocumentRequest,
    service: DocumentService = Depends(get_document_service)
):
    """
    Update document content.

    - **document_id**: UUID of the document
    - **content**: New document content
    - **changeSummary**: Optional summary of changes

    If content changed, increments version and creates version record.
    If content unchanged, returns existing document without creating new version.
    """
    # Use a mock user ID (in production, get from auth context)
    updated_by = uuid.uuid4()

    document = await service.update_document_with_versioning(
        document_id=document_id,
        new_content=request.content,
        updated_by=updated_by,
        change_summary=request.changeSummary
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    return DocumentResponse.model_validate(document)


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document and all associated versions and comments."
)
async def delete_document(
    document_id: uuid.UUID,
    service: DocumentService = Depends(get_document_service)
):
    """
    Delete document.

    - **document_id**: UUID of the document

    Deletes the document and all associated versions and comments (CASCADE).
    """
    deleted = await service.delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    return None


@router.get(
    "/documents/{document_id}/versions",
    response_model=List[DocumentVersionResponse],
    summary="Get document version history",
    description="Get all versions for a document."
)
async def get_document_versions(
    document_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    version_repo: DocumentVersionRepository = Depends(get_version_repo),
    service: DocumentService = Depends(get_document_service)
):
    """
    Get version history for a document.

    - **document_id**: UUID of the document
    - **page**: Page number (starting from 1)
    - **limit**: Maximum results per page

    Returns list of versions ordered by version number (descending).
    """
    # Verify document exists
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    offset = (page - 1) * limit

    versions = await version_repo.get_by_document_id(
        document_id=document_id,
        limit=limit,
        offset=offset
    )

    return [DocumentVersionResponse.model_validate(v) for v in versions]


@router.post(
    "/documents/{document_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment to document",
    description="Add a comment to a document (general or line-specific)."
)
async def create_comment(
    document_id: uuid.UUID,
    request: CreateCommentRequest,
    comment_repo: CommentRepository = Depends(get_comment_repo),
    service: DocumentService = Depends(get_document_service)
):
    """
    Add comment to document.

    - **document_id**: UUID of the document
    - **userId**: UUID of the user creating the comment
    - **content**: Comment content
    - **lineNumber**: Optional line number for line-specific comments

    Returns the created comment.
    """
    # Verify document exists
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    comment = await comment_repo.create_comment(
        document_id=document_id,
        user_id=request.userId,
        content=request.content,
        line_number=request.lineNumber
    )

    return CommentResponse.model_validate(comment)


@router.get(
    "/documents/{document_id}/comments",
    response_model=List[CommentResponse],
    summary="List document comments",
    description="Get all comments for a document with optional filters."
)
async def list_document_comments(
    document_id: uuid.UUID,
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    comment_repo: CommentRepository = Depends(get_comment_repo),
    service: DocumentService = Depends(get_document_service)
):
    """
    List comments for a document.

    - **document_id**: UUID of the document
    - **resolved**: Optional filter for resolved status (true/false)
    - **page**: Page number (starting from 1)
    - **limit**: Maximum results per page

    Returns list of comments.
    """
    # Verify document exists
    document = await service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    offset = (page - 1) * limit

    comments = await comment_repo.get_by_document_id(
        document_id=document_id,
        resolved=resolved,
        limit=limit,
        offset=offset
    )

    return [CommentResponse.model_validate(c) for c in comments]
