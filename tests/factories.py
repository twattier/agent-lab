"""
Test data factories for creating model instances.

Provides factory functions for creating test data with sensible defaults.
"""
import uuid
from datetime import datetime
from typing import Optional

from models.database import (
    Client, Service, Project, Contact, ServiceContact, ProjectContact,
    ImplementationType, ServiceCategory, WorkflowEvent
)


class ClientFactory:
    """Factory for creating Client instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        name: str = "Test Client",
        business_domain: str = "technology",
        **kwargs
    ) -> Client:
        """Create a Client instance."""
        return Client(
            id=id or uuid.uuid4(),
            name=name,
            business_domain=business_domain,
            created_at=kwargs.get('created_at', datetime.utcnow()),
            updated_at=kwargs.get('updated_at', datetime.utcnow()),
        )


class ServiceFactory:
    """Factory for creating Service instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        name: str = "Test Service",
        description: Optional[str] = "Test service description",
        client_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> Service:
        """Create a Service instance."""
        if client_id is None:
            raise ValueError("client_id is required")

        return Service(
            id=id or uuid.uuid4(),
            name=name,
            description=description,
            client_id=client_id,
            created_at=kwargs.get('created_at', datetime.utcnow()),
            updated_at=kwargs.get('updated_at', datetime.utcnow()),
        )


class ProjectFactory:
    """Factory for creating Project instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        name: str = "Test Project",
        description: str = "Test project description",
        service_id: Optional[uuid.UUID] = None,
        project_type: str = "new",
        status: str = "draft",
        workflow_state: Optional[dict] = None,
        **kwargs
    ) -> Project:
        """Create a Project instance."""
        if service_id is None:
            raise ValueError("service_id is required")

        if workflow_state is None:
            workflow_state = {
                "currentStage": "business_analysis",
                "completedStages": []
            }

        return Project(
            id=id or uuid.uuid4(),
            name=name,
            description=description,
            service_id=service_id,
            project_type=project_type,
            status=status,
            workflow_state=workflow_state,
            implementation_type_id=kwargs.get('implementation_type_id'),
            claude_code_path=kwargs.get('claude_code_path'),
            created_at=kwargs.get('created_at', datetime.utcnow()),
            updated_at=kwargs.get('updated_at', datetime.utcnow()),
        )


class ContactFactory:
    """Factory for creating Contact instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        name: str = "Test Contact",
        email: Optional[str] = None,
        role: Optional[str] = "Test Role",
        phone: Optional[str] = "+15551234567",
        **kwargs
    ) -> Contact:
        """Create a Contact instance."""
        if email is None:
            email = f"test.{uuid.uuid4().hex[:8]}@example.com"

        return Contact(
            id=id or uuid.uuid4(),
            name=name,
            email=email,
            role=role,
            phone=phone,
            is_active=kwargs.get('is_active', True),
            created_at=kwargs.get('created_at', datetime.utcnow()),
            updated_at=kwargs.get('updated_at', datetime.utcnow()),
        )


class ImplementationTypeFactory:
    """Factory for creating ImplementationType instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        code: str = "TEST",
        name: str = "Test Implementation",
        description: Optional[str] = "Test implementation type",
        **kwargs
    ) -> ImplementationType:
        """Create an ImplementationType instance."""
        return ImplementationType(
            id=id or uuid.uuid4(),
            code=code,
            name=name,
            description=description,
            is_active=kwargs.get('is_active', True),
            created_at=kwargs.get('created_at', datetime.utcnow()),
            updated_at=kwargs.get('updated_at', datetime.utcnow()),
        )


class ServiceCategoryFactory:
    """Factory for creating ServiceCategory instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        code: str = "TEST",
        name: str = "Test Category",
        description: Optional[str] = "Test service category",
        color: Optional[str] = "#3B82F6",
        **kwargs
    ) -> ServiceCategory:
        """Create a ServiceCategory instance."""
        return ServiceCategory(
            id=id or uuid.uuid4(),
            code=code,
            name=name,
            description=description,
            color=color,
            is_active=kwargs.get('is_active', True),
            created_at=kwargs.get('created_at', datetime.utcnow()),
            updated_at=kwargs.get('updated_at', datetime.utcnow()),
        )


class WorkflowEventFactory:
    """Factory for creating WorkflowEvent instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        event_type: str = "stage_advance",
        from_stage: Optional[str] = None,
        to_stage: str = "business_analysis",
        user_id: Optional[uuid.UUID] = None,
        event_metadata: Optional[dict] = None,
        **kwargs
    ) -> WorkflowEvent:
        """Create a WorkflowEvent instance."""
        if project_id is None:
            raise ValueError("project_id is required")

        return WorkflowEvent(
            id=id or uuid.uuid4(),
            project_id=project_id,
            event_type=event_type,
            from_stage=from_stage,
            to_stage=to_stage,
            user_id=user_id or uuid.uuid4(),
            event_metadata=event_metadata or {},
            timestamp=kwargs.get('timestamp', datetime.utcnow()),
        )


class ServiceContactFactory:
    """Factory for creating ServiceContact instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        service_id: Optional[uuid.UUID] = None,
        contact_id: Optional[uuid.UUID] = None,
        is_primary: bool = False,
        relationship_type: str = "main",
        **kwargs
    ) -> ServiceContact:
        """Create a ServiceContact instance."""
        if service_id is None:
            raise ValueError("service_id is required")
        if contact_id is None:
            raise ValueError("contact_id is required")

        return ServiceContact(
            id=id or uuid.uuid4(),
            service_id=service_id,
            contact_id=contact_id,
            is_primary=is_primary,
            relationship_type=relationship_type,
            created_at=kwargs.get('created_at', datetime.utcnow()),
        )


class ProjectContactFactory:
    """Factory for creating ProjectContact instances."""

    @staticmethod
    def create(
        id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        contact_id: Optional[uuid.UUID] = None,
        contact_type: str = "stakeholder",
        is_active: bool = True,
        **kwargs
    ) -> ProjectContact:
        """Create a ProjectContact instance."""
        if project_id is None:
            raise ValueError("project_id is required")
        if contact_id is None:
            raise ValueError("contact_id is required")

        return ProjectContact(
            id=id or uuid.uuid4(),
            project_id=project_id,
            contact_id=contact_id,
            contact_type=contact_type,
            is_active=is_active,
            created_at=kwargs.get('created_at', datetime.utcnow()),
        )
