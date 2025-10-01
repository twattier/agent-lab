"""
Integration tests for document API endpoints.
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from models.database import Document, DocumentVersion, Comment, Language, DocumentType
from tests.fixtures.factories import (
    ProjectFactory, DocumentFactory, DocumentVersionFactory, CommentFactory
)
from core.document_utils import generate_content_hash


@pytest.mark.asyncio
class TestCreateDocument:
    """Tests for POST /api/v1/documents/projects/{project_id}/documents."""

    async def test_create_document_success(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test successful document creation."""
        # Create a project first
        project = await ProjectFactory.create_async(test_session)

        # Mock embedding service to avoid OpenAI API calls
        with patch('services.embedding_service.EmbeddingService.generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 1536

            response = await test_client.post(
                f"/api/v1/documents/projects/{project.id}/documents",
                json={
                    "name": "Test PRD Document",
                    "content": "This is the product requirements document.",
                    "language": "en",
                    "documentType": "prd"
                }
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test PRD Document"
        assert data["content"] == "This is the product requirements document."
        assert data["language"] == "en"
        assert data["documentType"] == "prd"
        assert data["version"] == 1
        assert "id" in data
        assert "contentHash" in data

        # Verify document was created in database
        result = await test_session.execute(
            select(Document).where(Document.id == uuid.UUID(data["id"]))
        )
        doc = result.scalar_one()
        assert doc.name == "Test PRD Document"
        assert doc.version == 1

        # Verify initial version was created
        version_result = await test_session.execute(
            select(DocumentVersion).where(DocumentVersion.document_id == doc.id)
        )
        versions = list(version_result.scalars().all())
        assert len(versions) == 1
        assert versions[0].version == 1

    async def test_create_document_french(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test creating document in French."""
        project = await ProjectFactory.create_async(test_session)

        with patch('services.embedding_service.EmbeddingService.generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.1] * 1536

            response = await test_client.post(
                f"/api/v1/documents/projects/{project.id}/documents",
                json={
                    "name": "Document français",
                    "content": "Contenu en français",
                    "language": "fr",
                    "documentType": "requirements"
                }
            )

        assert response.status_code == 201
        data = response.json()
        assert data["language"] == "fr"

    async def test_create_document_invalid_data(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test document creation with invalid data."""
        project = await ProjectFactory.create_async(test_session)

        response = await test_client.post(
            f"/api/v1/documents/projects/{project.id}/documents",
            json={
                "name": "",  # Invalid: empty name
                "content": "Content",
                "documentType": "prd"
            }
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestListProjectDocuments:
    """Tests for GET /api/v1/documents/projects/{project_id}/documents."""

    async def test_list_documents(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test listing documents for a project."""
        project = await ProjectFactory.create_async(test_session)

        # Create multiple documents
        doc1 = await DocumentFactory.create_async(test_session, project_id=project.id, name="Doc 1")
        doc2 = await DocumentFactory.create_async(test_session, project_id=project.id, name="Doc 2")

        response = await test_client.get(
            f"/api/v1/documents/projects/{project.id}/documents"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [d["name"] for d in data]
        assert "Doc 1" in names
        assert "Doc 2" in names

    async def test_filter_by_document_type(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test filtering documents by type."""
        project = await ProjectFactory.create_async(test_session)

        # Create documents of different types
        await DocumentFactory.create_async(
            test_session, project_id=project.id, document_type=DocumentType.PRD
        )
        await DocumentFactory.create_async(
            test_session, project_id=project.id, document_type=DocumentType.ARCHITECTURE
        )
        await DocumentFactory.create_async(
            test_session, project_id=project.id, document_type=DocumentType.PRD
        )

        response = await test_client.get(
            f"/api/v1/documents/projects/{project.id}/documents?type=prd"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(d["documentType"] == "prd" for d in data)

    async def test_filter_by_language(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test filtering documents by language."""
        project = await ProjectFactory.create_async(test_session)

        # Create documents in different languages
        await DocumentFactory.create_async(
            test_session, project_id=project.id, language=Language.ENGLISH
        )
        await DocumentFactory.create_async(
            test_session, project_id=project.id, language=Language.FRENCH
        )

        response = await test_client.get(
            f"/api/v1/documents/projects/{project.id}/documents?language=fr"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["language"] == "fr"


@pytest.mark.asyncio
class TestGetDocument:
    """Tests for GET /api/v1/documents/documents/{document_id}."""

    async def test_get_document_success(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test getting document by ID."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(
            test_session, project_id=project.id, name="Test Doc"
        )

        response = await test_client.get(
            f"/api/v1/documents/documents/{document.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Doc"
        assert data["id"] == str(document.id)

    async def test_get_nonexistent_document(self, test_client: AsyncClient):
        """Test getting nonexistent document returns 404."""
        fake_id = uuid.uuid4()
        response = await test_client.get(
            f"/api/v1/documents/documents/{fake_id}"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateDocument:
    """Tests for PUT /api/v1/documents/documents/{document_id}."""

    async def test_update_creates_version_on_content_change(
        self, test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test that updating content creates a new version."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(
            test_session, project_id=project.id, content="Original content", version=1
        )

        with patch('services.embedding_service.EmbeddingService.generate_embedding', new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = [0.2] * 1536

            response = await test_client.put(
                f"/api/v1/documents/documents/{document.id}",
                json={
                    "content": "Updated content",
                    "changeSummary": "Made significant updates"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 2
        assert data["content"] == "Updated content"

        # Verify version was created in database
        version_result = await test_session.execute(
            select(DocumentVersion).where(DocumentVersion.document_id == document.id)
        )
        versions = list(version_result.scalars().all())
        assert len(versions) >= 1  # At least the new version

    async def test_update_no_version_when_content_unchanged(
        self, test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test that unchanged content doesn't create new version."""
        project = await ProjectFactory.create_async(test_session)
        original_content = "Same content"
        document = await DocumentFactory.create_async(
            test_session, project_id=project.id, content=original_content, version=1
        )

        response = await test_client.put(
            f"/api/v1/documents/documents/{document.id}",
            json={
                "content": original_content,  # Same content
                "changeSummary": "No changes"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1  # Version should NOT increment

    async def test_update_nonexistent_document(self, test_client: AsyncClient):
        """Test updating nonexistent document returns 404."""
        fake_id = uuid.uuid4()
        response = await test_client.put(
            f"/api/v1/documents/documents/{fake_id}",
            json={"content": "New content"}
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteDocument:
    """Tests for DELETE /api/v1/documents/documents/{document_id}."""

    async def test_delete_document_success(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test successful document deletion."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(test_session, project_id=project.id)

        response = await test_client.delete(
            f"/api/v1/documents/documents/{document.id}"
        )

        assert response.status_code == 204

        # Verify document was deleted
        result = await test_session.execute(
            select(Document).where(Document.id == document.id)
        )
        assert result.scalar_one_or_none() is None

    async def test_delete_cascade_versions_and_comments(
        self, test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test that deleting document cascades to versions and comments."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(test_session, project_id=project.id)

        # Create version and comment
        version = await DocumentVersionFactory.create_async(
            test_session, document_id=document.id
        )
        comment = await CommentFactory.create_async(
            test_session, document_id=document.id
        )

        response = await test_client.delete(
            f"/api/v1/documents/documents/{document.id}"
        )

        assert response.status_code == 204

        # Verify versions were deleted
        version_result = await test_session.execute(
            select(DocumentVersion).where(DocumentVersion.id == version.id)
        )
        assert version_result.scalar_one_or_none() is None

        # Verify comments were deleted
        comment_result = await test_session.execute(
            select(Comment).where(Comment.id == comment.id)
        )
        assert comment_result.scalar_one_or_none() is None


@pytest.mark.asyncio
class TestGetDocumentVersions:
    """Tests for GET /api/v1/documents/documents/{document_id}/versions."""

    async def test_get_version_history(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test getting version history."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(test_session, project_id=project.id)

        # Create multiple versions
        v1 = await DocumentVersionFactory.create_async(
            test_session, document_id=document.id, version=1
        )
        v2 = await DocumentVersionFactory.create_async(
            test_session, document_id=document.id, version=2
        )

        response = await test_client.get(
            f"/api/v1/documents/documents/{document.id}/versions"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should be ordered by version DESC
        assert data[0]["version"] >= data[1]["version"]


@pytest.mark.asyncio
class TestCreateComment:
    """Tests for POST /api/v1/documents/documents/{document_id}/comments."""

    async def test_create_comment_success(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test creating a comment."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(test_session, project_id=project.id)
        user_id = uuid.uuid4()

        response = await test_client.post(
            f"/api/v1/documents/documents/{document.id}/comments",
            json={
                "userId": str(user_id),
                "content": "This needs revision",
                "lineNumber": 42
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "This needs revision"
        assert data["lineNumber"] == 42
        assert data["resolved"] is False


@pytest.mark.asyncio
class TestListComments:
    """Tests for GET /api/v1/documents/documents/{document_id}/comments."""

    async def test_list_comments(self, test_client: AsyncClient, test_session: AsyncSession):
        """Test listing comments."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(test_session, project_id=project.id)

        # Create comments
        await CommentFactory.create_async(
            test_session, document_id=document.id, resolved=False
        )
        await CommentFactory.create_async(
            test_session, document_id=document.id, resolved=True
        )

        response = await test_client.get(
            f"/api/v1/documents/documents/{document.id}/comments"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_filter_comments_by_resolved(
        self, test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test filtering comments by resolved status."""
        project = await ProjectFactory.create_async(test_session)
        document = await DocumentFactory.create_async(test_session, project_id=project.id)

        # Create comments
        await CommentFactory.create_async(
            test_session, document_id=document.id, resolved=False
        )
        await CommentFactory.create_async(
            test_session, document_id=document.id, resolved=True
        )

        response = await test_client.get(
            f"/api/v1/documents/documents/{document.id}/comments?resolved=false"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["resolved"] is False
