"""
Unit tests for document service.
"""
import uuid
import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Document, DocumentVersion, Language, DocumentType
from services.document_service import DocumentService
from core.document_utils import generate_content_hash


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_document():
    """Mock document instance."""
    doc = Mock(spec=Document)
    doc.id = uuid.uuid4()
    doc.project_id = uuid.uuid4()
    doc.name = "Test Document"
    doc.content = "Original content"
    doc.content_hash = generate_content_hash("Original content")
    doc.version = 1
    doc.language = Language.ENGLISH
    doc.document_type = DocumentType.PRD
    return doc


@pytest.fixture
def document_service(mock_db):
    """Document service instance with mocked dependencies."""
    return DocumentService(mock_db)


class TestContentHashGeneration:
    """Tests for content hash generation."""

    def test_hash_generation_is_consistent(self):
        """Test that hash generation is consistent for same content."""
        content = "Test content for hashing"
        hash1 = generate_content_hash(content)
        hash2 = generate_content_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_hash_changes_with_content(self):
        """Test that hash changes when content changes."""
        content1 = "Original content"
        content2 = "Modified content"

        hash1 = generate_content_hash(content1)
        hash2 = generate_content_hash(content2)

        assert hash1 != hash2


class TestCreateDocumentWithVersion:
    """Tests for create_document_with_version method."""

    @pytest.mark.asyncio
    async def test_creates_document_and_version(self, document_service, mock_db):
        """Test that create_document_with_version creates both document and version."""
        project_id = uuid.uuid4()
        created_by = uuid.uuid4()

        # Mock the repository methods
        mock_doc = Mock(spec=Document)
        mock_doc.id = uuid.uuid4()
        mock_doc.version = 1

        with patch.object(document_service.document_repo, 'create_document', return_value=mock_doc) as mock_create_doc:
            with patch.object(document_service.version_repo, 'create_version', return_value=Mock()) as mock_create_ver:
                with patch.object(document_service.embedding_service, 'generate_embedding', return_value=[0.1] * 1536):
                    result = await document_service.create_document_with_version(
                        project_id=project_id,
                        name="Test Doc",
                        content="Test content",
                        language=Language.ENGLISH,
                        document_type=DocumentType.PRD,
                        created_by=created_by
                    )

                    # Verify document was created
                    mock_create_doc.assert_called_once()
                    # Verify version was created
                    mock_create_ver.assert_called_once()
                    assert result == mock_doc

    @pytest.mark.asyncio
    async def test_generates_embedding(self, document_service):
        """Test that embedding is generated for new document."""
        project_id = uuid.uuid4()
        created_by = uuid.uuid4()

        mock_embedding = [0.1] * 1536

        with patch.object(document_service.document_repo, 'create_document', return_value=Mock()):
            with patch.object(document_service.version_repo, 'create_version', return_value=Mock()):
                with patch.object(document_service.embedding_service, 'generate_embedding', return_value=mock_embedding) as mock_embed:
                    await document_service.create_document_with_version(
                        project_id=project_id,
                        name="Test",
                        content="Content for embedding",
                        language=Language.ENGLISH,
                        document_type=DocumentType.PRD,
                        created_by=created_by
                    )

                    mock_embed.assert_called_once_with("Content for embedding")


class TestUpdateDocumentWithVersioning:
    """Tests for update_document_with_versioning method."""

    @pytest.mark.asyncio
    async def test_creates_version_when_content_changes(self, document_service, mock_document):
        """Test that version is created when content changes."""
        document_id = mock_document.id
        updated_by = uuid.uuid4()
        new_content = "Modified content"

        # Mock document retrieval
        with patch.object(document_service.document_repo, 'get_by_id', return_value=mock_document):
            # Mock document update
            updated_doc = Mock(spec=Document)
            updated_doc.version = 2
            with patch.object(document_service.document_repo, 'update_document', return_value=updated_doc):
                # Mock version creation
                with patch.object(document_service.version_repo, 'create_version', return_value=Mock()) as mock_create_ver:
                    with patch.object(document_service.embedding_service, 'generate_embedding', return_value=[0.1] * 1536):
                        result = await document_service.update_document_with_versioning(
                            document_id=document_id,
                            new_content=new_content,
                            updated_by=updated_by,
                            change_summary="Updated content"
                        )

                        # Verify version was created
                        mock_create_ver.assert_called_once()
                        assert result == updated_doc

    @pytest.mark.asyncio
    async def test_no_version_when_content_unchanged(self, document_service, mock_document):
        """Test that version is NOT created when content is unchanged."""
        document_id = mock_document.id
        updated_by = uuid.uuid4()
        same_content = "Original content"  # Same as mock_document.content

        # Mock document retrieval
        with patch.object(document_service.document_repo, 'get_by_id', return_value=mock_document):
            with patch.object(document_service.version_repo, 'create_version') as mock_create_ver:
                result = await document_service.update_document_with_versioning(
                    document_id=document_id,
                    new_content=same_content,
                    updated_by=updated_by
                )

                # Verify NO version was created
                mock_create_ver.assert_not_called()
                # Should return existing document
                assert result == mock_document

    @pytest.mark.asyncio
    async def test_version_number_increments(self, document_service, mock_document):
        """Test that version number increments correctly."""
        document_id = mock_document.id
        updated_by = uuid.uuid4()
        new_content = "New content"

        mock_document.version = 5  # Start at version 5

        with patch.object(document_service.document_repo, 'get_by_id', return_value=mock_document):
            updated_doc = Mock(spec=Document)
            updated_doc.version = 6
            with patch.object(document_service.document_repo, 'update_document', return_value=updated_doc) as mock_update:
                with patch.object(document_service.version_repo, 'create_version', return_value=Mock()):
                    with patch.object(document_service.embedding_service, 'generate_embedding', return_value=[0.1] * 1536):
                        await document_service.update_document_with_versioning(
                            document_id=document_id,
                            new_content=new_content,
                            updated_by=updated_by
                        )

                        # Verify update was called with version 6
                        call_args = mock_update.call_args
                        assert call_args.kwargs['version'] == 6

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_document(self, document_service):
        """Test that None is returned for nonexistent document."""
        document_id = uuid.uuid4()
        updated_by = uuid.uuid4()

        with patch.object(document_service.document_repo, 'get_by_id', return_value=None):
            result = await document_service.update_document_with_versioning(
                document_id=document_id,
                new_content="New content",
                updated_by=updated_by
            )

            assert result is None


class TestEmbeddingGeneration:
    """Tests for embedding generation."""

    @pytest.mark.asyncio
    async def test_embedding_updates_on_content_change(self, document_service, mock_document):
        """Test that embedding is regenerated when content changes."""
        document_id = mock_document.id
        updated_by = uuid.uuid4()
        new_content = "New content requiring new embedding"

        with patch.object(document_service.document_repo, 'get_by_id', return_value=mock_document):
            with patch.object(document_service.document_repo, 'update_document', return_value=Mock()):
                with patch.object(document_service.version_repo, 'create_version', return_value=Mock()):
                    with patch.object(document_service.embedding_service, 'generate_embedding', return_value=[0.2] * 1536) as mock_embed:
                        await document_service.update_document_with_versioning(
                            document_id=document_id,
                            new_content=new_content,
                            updated_by=updated_by
                        )

                        mock_embed.assert_called_once_with(new_content)

    @pytest.mark.asyncio
    async def test_handles_embedding_failure_gracefully(self, document_service):
        """Test that document creation continues even if embedding fails."""
        project_id = uuid.uuid4()
        created_by = uuid.uuid4()

        with patch.object(document_service.document_repo, 'create_document', return_value=Mock()) as mock_create:
            with patch.object(document_service.version_repo, 'create_version', return_value=Mock()):
                with patch.object(document_service.embedding_service, 'generate_embedding', side_effect=Exception("API Error")):
                    # Should not raise exception
                    await document_service.create_document_with_version(
                        project_id=project_id,
                        name="Test",
                        content="Content",
                        language=Language.ENGLISH,
                        document_type=DocumentType.PRD,
                        created_by=created_by
                    )

                    # Document should still be created with None vector
                    mock_create.assert_called_once()
                    call_args = mock_create.call_args
                    assert call_args.kwargs['content_vector'] is None
