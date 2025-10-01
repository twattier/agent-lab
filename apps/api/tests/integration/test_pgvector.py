"""
Integration tests for pgvector extension and semantic search.
"""
import uuid
import pytest
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Document, DocumentType, Language
from tests.fixtures.factories import ProjectFactory, DocumentFactory
from repositories.document_repository import DocumentRepository


@pytest.mark.asyncio
class TestPgvectorExtension:
    """Tests for pgvector extension setup."""

    async def test_pgvector_extension_enabled(self, test_session: AsyncSession):
        """Test that pgvector extension is enabled."""
        result = await test_session.execute(
            text("SELECT * FROM pg_extension WHERE extname = 'vector'")
        )
        extension = result.first()

        assert extension is not None, "pgvector extension not installed"

    async def test_vector_column_exists(self, test_session: AsyncSession):
        """Test that content_vector column exists with correct type."""
        result = await test_session.execute(
            text("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'document' AND column_name = 'content_vector'
            """)
        )
        column = result.first()

        assert column is not None, "content_vector column not found"
        assert column.udt_name == 'vector', f"Expected vector type, got {column.udt_name}"

    async def test_ivfflat_index_exists(self, test_session: AsyncSession):
        """Test that ivfflat index exists on content_vector."""
        result = await test_session.execute(
            text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'document' AND indexname = 'idx_document_vector'
            """)
        )
        index = result.first()

        assert index is not None, "idx_document_vector index not found"
        assert 'ivfflat' in index.indexdef.lower(), "Index is not using ivfflat"
        assert 'vector_cosine_ops' in index.indexdef, "Index not using cosine distance"


@pytest.mark.asyncio
class TestEmbeddingStorage:
    """Tests for embedding vector storage."""

    async def test_store_embedding_vector(self, test_session: AsyncSession):
        """Test storing a document with embedding vector."""
        project = await ProjectFactory.create_async(test_session)

        # Create mock embedding (1536 dimensions for text-embedding-ada-002)
        mock_embedding = [0.1] * 1536

        doc_repo = DocumentRepository(test_session)
        document = await doc_repo.create_document(
            project_id=project.id,
            name="Test Document with Embedding",
            content="Content for embedding test",
            content_hash="test_hash",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=mock_embedding
        )

        assert document.id is not None
        assert document.content_vector is not None

        # Verify it was stored correctly
        result = await test_session.execute(
            select(Document).where(Document.id == document.id)
        )
        stored_doc = result.scalar_one()
        assert stored_doc.content_vector is not None

    async def test_update_embedding_on_content_change(self, test_session: AsyncSession):
        """Test updating embedding when content changes."""
        project = await ProjectFactory.create_async(test_session)

        # Create document with initial embedding
        initial_embedding = [0.1] * 1536
        doc_repo = DocumentRepository(test_session)
        document = await doc_repo.create_document(
            project_id=project.id,
            name="Test Doc",
            content="Initial content",
            content_hash="hash1",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=initial_embedding
        )

        # Update with new embedding
        new_embedding = [0.2] * 1536
        updated_doc = await doc_repo.update_document(
            document_id=document.id,
            content="Updated content",
            content_hash="hash2",
            version=2,
            content_vector=new_embedding
        )

        assert updated_doc is not None
        assert updated_doc.content_vector is not None
        # Verify the embedding was updated (compare first value)
        assert updated_doc.content_vector != document.content_vector


@pytest.mark.asyncio
class TestVectorSimilaritySearch:
    """Tests for vector similarity search queries."""

    async def test_cosine_distance_query(self, test_session: AsyncSession):
        """Test vector similarity search using cosine distance."""
        project = await ProjectFactory.create_async(test_session)

        # Create documents with different embeddings
        doc_repo = DocumentRepository(test_session)

        # Document 1: similar to query
        embedding1 = [0.9] + [0.1] * 1535
        doc1 = await doc_repo.create_document(
            project_id=project.id,
            name="Similar Document",
            content="Content about machine learning",
            content_hash="hash1",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=embedding1
        )

        # Document 2: less similar
        embedding2 = [0.1] + [0.9] * 1535
        doc2 = await doc_repo.create_document(
            project_id=project.id,
            name="Different Document",
            content="Content about cooking recipes",
            content_hash="hash2",
            language=Language.ENGLISH,
            document_type=DocumentType.OTHER,
            content_vector=embedding2
        )

        # Query vector (similar to doc1)
        query_vector = [0.85] + [0.15] * 1535

        # Search for similar documents
        results = await doc_repo.search_by_vector(
            query_vector=query_vector,
            limit=2,
            project_id=project.id
        )

        assert len(results) >= 1
        # First result should be doc1 (more similar)
        assert results[0].id == doc1.id

    async def test_search_with_project_filter(self, test_session: AsyncSession):
        """Test vector search filtered by project."""
        project1 = await ProjectFactory.create_async(test_session)
        project2 = await ProjectFactory.create_async(test_session)

        doc_repo = DocumentRepository(test_session)
        embedding = [0.5] * 1536

        # Create document in project1
        doc1 = await doc_repo.create_document(
            project_id=project1.id,
            name="Project 1 Doc",
            content="Content",
            content_hash="hash1",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=embedding
        )

        # Create document in project2
        doc2 = await doc_repo.create_document(
            project_id=project2.id,
            name="Project 2 Doc",
            content="Content",
            content_hash="hash2",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=embedding
        )

        # Search only in project1
        results = await doc_repo.search_by_vector(
            query_vector=embedding,
            limit=10,
            project_id=project1.id
        )

        # Should only return doc1
        result_ids = [r.id for r in results]
        assert doc1.id in result_ids
        assert doc2.id not in result_ids

    async def test_search_ignores_documents_without_embeddings(
        self, test_session: AsyncSession
    ):
        """Test that search ignores documents without embeddings."""
        project = await ProjectFactory.create_async(test_session)

        doc_repo = DocumentRepository(test_session)

        # Create document without embedding
        doc_no_embed = await doc_repo.create_document(
            project_id=project.id,
            name="No Embedding Doc",
            content="Content",
            content_hash="hash1",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=None
        )

        # Create document with embedding
        embedding = [0.5] * 1536
        doc_with_embed = await doc_repo.create_document(
            project_id=project.id,
            name="With Embedding Doc",
            content="Content",
            content_hash="hash2",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=embedding
        )

        # Search
        results = await doc_repo.search_by_vector(
            query_vector=embedding,
            limit=10
        )

        # Should only return document with embedding
        result_ids = [r.id for r in results]
        assert doc_with_embed.id in result_ids
        assert doc_no_embed.id not in result_ids


@pytest.mark.asyncio
class TestPgvectorCompatibility:
    """Tests for pgvector 0.5.0 compatibility."""

    async def test_pgvector_version(self, test_session: AsyncSession):
        """Test that pgvector version is compatible (0.5.0+)."""
        result = await test_session.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        )
        version = result.scalar_one()

        # Parse version (format: "0.5.0" or similar)
        major, minor, patch = version.split('.')
        assert int(major) == 0, f"Expected major version 0, got {major}"
        assert int(minor) >= 5, f"Expected minor version >= 5, got {minor}"

    async def test_vector_dimension_validation(self, test_session: AsyncSession):
        """Test that vector dimension is enforced (1536)."""
        project = await ProjectFactory.create_async(test_session)

        doc_repo = DocumentRepository(test_session)

        # Try to create document with correct dimensions (1536)
        correct_embedding = [0.1] * 1536
        doc_correct = await doc_repo.create_document(
            project_id=project.id,
            name="Correct Dimensions",
            content="Content",
            content_hash="hash1",
            language=Language.ENGLISH,
            document_type=DocumentType.PRD,
            content_vector=correct_embedding
        )

        assert doc_correct.id is not None

        # Try with wrong dimensions (should fail or be rejected)
        # Note: pgvector will enforce dimension constraints at the database level
        wrong_embedding = [0.1] * 512  # Wrong dimension
        with pytest.raises(Exception):
            await doc_repo.create_document(
                project_id=project.id,
                name="Wrong Dimensions",
                content="Content",
                content_hash="hash2",
                language=Language.ENGLISH,
                document_type=DocumentType.PRD,
                content_vector=wrong_embedding
            )
