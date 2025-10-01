"""
Unit tests for Pydantic validation and input sanitization.
"""
import pytest
from pydantic import ValidationError

from models.schemas import (
    ClientCreate,
    ServiceCreate,
    ProjectCreate,
    ContactCreate,
    ServiceCategoryCreate,
    ImplementationTypeCreate,
    CreateDocumentRequest,
    CreateCommentRequest,
    BusinessDomain,
    ProjectType,
    Language,
    DocumentType,
)


class TestClientValidation:
    """Test client validation."""

    def test_valid_client(self):
        """Test creating a valid client."""
        client = ClientCreate(
            name="Test Company",
            business_domain=BusinessDomain.TECHNOLOGY
        )
        assert client.name == "Test Company"
        assert client.business_domain == BusinessDomain.TECHNOLOGY

    def test_client_name_sanitization(self):
        """Test HTML sanitization in client name."""
        client = ClientCreate(
            name="<script>alert('xss')</script>Test Company",
            business_domain=BusinessDomain.HEALTHCARE
        )
        assert "<script>" not in client.name
        assert "Test Company" in client.name

    def test_client_name_too_short(self):
        """Test client name minimum length validation."""
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(
                name="",
                business_domain=BusinessDomain.FINANCE
            )
        assert "min_length" in str(exc_info.value).lower() or "string_too_short" in str(exc_info.value).lower()

    def test_client_name_too_long(self):
        """Test client name maximum length validation."""
        with pytest.raises(ValidationError) as exc_info:
            ClientCreate(
                name="x" * 256,
                business_domain=BusinessDomain.EDUCATION
            )
        assert "max_length" in str(exc_info.value).lower() or "string_too_long" in str(exc_info.value).lower()


class TestContactValidation:
    """Test contact validation."""

    def test_valid_contact(self):
        """Test creating a valid contact."""
        contact = ContactCreate(
            name="John Doe",
            email="john.doe@example.com",
            role="Developer",
            phone="+15551234567"
        )
        assert contact.name == "John Doe"
        assert contact.email == "john.doe@example.com"

    def test_contact_invalid_email(self):
        """Test invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            ContactCreate(
                name="John Doe",
                email="not-an-email",
                role="Developer"
            )
        assert "email" in str(exc_info.value).lower() or "value_error" in str(exc_info.value).lower()

    def test_contact_invalid_phone(self):
        """Test invalid phone format."""
        with pytest.raises(ValidationError) as exc_info:
            ContactCreate(
                name="John Doe",
                email="john@example.com",
                phone="abc123"  # Contains letters, invalid
            )
        assert "phone" in str(exc_info.value).lower() or "international format" in str(exc_info.value).lower()

    def test_contact_name_sanitization(self):
        """Test HTML sanitization in contact name."""
        contact = ContactCreate(
            name="<b>John</b> <script>alert('xss')</script>Doe",
            email="john@example.com"
        )
        assert "<script>" not in contact.name
        assert "John" in contact.name or "Doe" in contact.name


class TestServiceCategoryValidation:
    """Test service category validation."""

    def test_valid_service_category(self):
        """Test creating a valid service category."""
        category = ServiceCategoryCreate(
            code="SALES",
            name="Sales Department",
            description="Sales and business development",
            color="#3B82F6"
        )
        assert category.code == "SALES"
        assert category.color == "#3B82F6"

    def test_service_category_invalid_code_format(self):
        """Test invalid code format (must be uppercase alphanumeric)."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceCategoryCreate(
                code="sales",  # lowercase not allowed
                name="Sales Department"
            )
        assert "uppercase" in str(exc_info.value).lower()

    def test_service_category_invalid_code_special_chars(self):
        """Test code with invalid special characters."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceCategoryCreate(
                code="SALES-DEPT",  # hyphens not allowed
                name="Sales Department"
            )
        assert "uppercase" in str(exc_info.value).lower() or "alphanumeric" in str(exc_info.value).lower()

    def test_service_category_invalid_color(self):
        """Test invalid color format."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceCategoryCreate(
                code="SALES",
                name="Sales",
                color="blue"  # Must be hex format
            )
        assert "pattern" in str(exc_info.value).lower() or "string_pattern_mismatch" in str(exc_info.value).lower()


class TestImplementationTypeValidation:
    """Test implementation type validation."""

    def test_valid_implementation_type(self):
        """Test creating a valid implementation type."""
        impl_type = ImplementationTypeCreate(
            code="RAG",
            name="Retrieval-Augmented Generation",
            description="AI with retrieval"
        )
        assert impl_type.code == "RAG"

    def test_implementation_type_invalid_code(self):
        """Test invalid code format."""
        with pytest.raises(ValidationError) as exc_info:
            ImplementationTypeCreate(
                code="rag",  # lowercase not allowed
                name="RAG"
            )
        assert "uppercase" in str(exc_info.value).lower()


class TestProjectValidation:
    """Test project validation."""

    def test_valid_project(self):
        """Test creating a valid project."""
        import uuid
        project = ProjectCreate(
            name="Test Project",
            description="A test project for validation",
            project_type=ProjectType.NEW,
            service_id=uuid.uuid4()
        )
        assert project.name == "Test Project"
        assert project.project_type == ProjectType.NEW

    def test_project_path_sanitization(self):
        """Test path traversal sanitization."""
        import uuid
        from models.schemas import ProjectUpdate

        project = ProjectUpdate(
            claude_code_path="../../../etc/passwd"
        )
        # Path should be sanitized to remove ../
        assert "../" not in project.claude_code_path


class TestDocumentValidation:
    """Test document validation."""

    def test_valid_document(self):
        """Test creating a valid document."""
        doc = CreateDocumentRequest(
            name="Project Requirements",
            language=Language.ENGLISH,
            documentType=DocumentType.PRD,
            content="# Requirements\n\nThis is a test document."
        )
        assert doc.name == "Project Requirements"
        assert doc.language == Language.ENGLISH

    def test_document_content_sanitization(self):
        """Test markdown content sanitization."""
        doc = CreateDocumentRequest(
            name="Test Doc",
            language=Language.ENGLISH,
            documentType=DocumentType.PRD,
            content="# Title\n<script>alert('xss')</script>\n\nContent here."
        )
        # Script tags should be removed
        assert "<script>" not in doc.content


class TestCommentValidation:
    """Test comment validation."""

    def test_valid_comment(self):
        """Test creating a valid comment."""
        import uuid
        comment = CreateCommentRequest(
            userId=uuid.uuid4(),
            content="This is a comment",
            lineNumber=42
        )
        assert comment.content == "This is a comment"
        assert comment.lineNumber == 42

    def test_comment_invalid_line_number(self):
        """Test invalid line number (must be positive)."""
        import uuid
        with pytest.raises(ValidationError) as exc_info:
            CreateCommentRequest(
                userId=uuid.uuid4(),
                content="Test comment",
                lineNumber=0  # Must be >= 1
            )
        assert "positive" in str(exc_info.value).lower()

    def test_comment_content_sanitization(self):
        """Test comment content sanitization."""
        import uuid
        comment = CreateCommentRequest(
            userId=uuid.uuid4(),
            content="<script>alert('xss')</script>Good comment"
        )
        # Script tags should be removed
        assert "<script>" not in comment.content
