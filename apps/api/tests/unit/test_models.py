"""
Unit tests for database models.
"""
import uuid
import pytest
from datetime import datetime

from models.database import Client, Service, Project, ImplementationType
from models.schemas import BusinessDomain, ProjectType, ProjectStatus


class TestClientModel:
    """Test Client model."""

    def test_client_creation(self):
        """Test basic client creation."""
        client_id = uuid.uuid4()
        client = Client(
            id=client_id,
            name="Test Client",
            business_domain="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert client.id == client_id
        assert client.name == "Test Client"
        assert client.business_domain == "technology"
        assert isinstance(client.created_at, datetime)
        assert isinstance(client.updated_at, datetime)

    def test_client_business_domain_enum(self):
        """Test business domain validation."""
        valid_domains = [
            "healthcare", "finance", "education", "government",
            "technology", "retail", "manufacturing"
        ]

        for domain in valid_domains:
            client = Client(
                name="Test Client",
                business_domain=domain
            )
            assert client.business_domain == domain


class TestServiceModel:
    """Test Service model."""

    def test_service_creation(self):
        """Test basic service creation."""
        service_id = uuid.uuid4()
        client_id = uuid.uuid4()

        service = Service(
            id=service_id,
            name="Test Service",
            description="A test service",
            client_id=client_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert service.id == service_id
        assert service.name == "Test Service"
        assert service.description == "A test service"
        assert service.client_id == client_id

    def test_service_optional_description(self):
        """Test service with optional description."""
        service = Service(
            name="Test Service",
            client_id=uuid.uuid4(),
            description=None
        )

        assert service.description is None


class TestProjectModel:
    """Test Project model."""

    def test_project_creation(self):
        """Test basic project creation."""
        project_id = uuid.uuid4()
        service_id = uuid.uuid4()

        project = Project(
            id=project_id,
            name="Test Project",
            description="A test project",
            service_id=service_id,
            project_type="web_application",
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert project.id == project_id
        assert project.name == "Test Project"
        assert project.service_id == service_id
        assert project.project_type == "web_application"
        assert project.status == "draft"

    def test_project_enums(self):
        """Test project type and status enums."""
        project_types = [
            "web_application", "mobile_app", "api_service",
            "data_pipeline", "ml_model", "automation_script"
        ]

        project_statuses = [
            "draft", "planning", "in_progress", "review",
            "completed", "on_hold", "cancelled"
        ]

        for project_type in project_types:
            project = Project(
                name="Test Project",
                service_id=uuid.uuid4(),
                project_type=project_type
            )
            assert project.project_type == project_type

        for status in project_statuses:
            project = Project(
                name="Test Project",
                service_id=uuid.uuid4(),
                project_type="web_application",
                status=status
            )
            assert project.status == status

    def test_project_workflow_state(self):
        """Test project workflow state JSON field."""
        workflow_state = {
            "phase": "development",
            "progress": 45,
            "tasks": ["design", "implementation", "testing"],
            "metadata": {"priority": "high"}
        }

        project = Project(
            name="Test Project",
            service_id=uuid.uuid4(),
            project_type="web_application",
            workflow_state=workflow_state
        )

        assert project.workflow_state == workflow_state
        assert project.workflow_state["phase"] == "development"
        assert project.workflow_state["progress"] == 45

    def test_project_claude_code_path(self):
        """Test Claude Code path field."""
        project = Project(
            name="Test Project",
            service_id=uuid.uuid4(),
            project_type="web_application",
            claude_code_path="/projects/test-project"
        )

        assert project.claude_code_path == "/projects/test-project"


class TestImplementationTypeModel:
    """Test ImplementationType model."""

    def test_implementation_type_creation(self):
        """Test basic implementation type creation."""
        impl_type_id = uuid.uuid4()

        impl_type = ImplementationType(
            id=impl_type_id,
            name="Custom Development",
            description="Full custom application development",
            created_at=datetime.utcnow()
        )

        assert impl_type.id == impl_type_id
        assert impl_type.name == "Custom Development"
        assert impl_type.description == "Full custom application development"

    def test_implementation_type_optional_description(self):
        """Test implementation type with optional description."""
        impl_type = ImplementationType(
            name="Framework Integration",
            description=None
        )

        assert impl_type.description is None