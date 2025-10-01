"""
Unit tests for foreign key CASCADE delete rules.

Tests verify that cascade deletes work correctly across all relationships.
"""
import pytest
from sqlalchemy import text

from models.database import (
    Client, Service, Project, Contact, ServiceContact, ProjectContact,
    ServiceServiceCategory, ProjectServiceCategory, WorkflowEvent
)


class TestCascadeDeleteRules:
    """Test CASCADE delete behavior."""

    @pytest.mark.asyncio
    async def test_client_delete_cascades_to_services(self, async_session):
        """Test deleting client cascades to services."""
        from uuid import uuid4
        from datetime import datetime

        # Create client
        client = Client(
            id=uuid4(),
            name="Test Client",
            business_domain="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(client)
        await async_session.commit()

        # Create service
        service = Service(
            id=uuid4(),
            name="Test Service",
            client_id=client.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(service)
        await async_session.commit()

        # Delete client
        await async_session.delete(client)
        await async_session.commit()

        # Verify service was also deleted (cascade)
        result = await async_session.execute(
            text("SELECT COUNT(*) FROM services WHERE id = :id"),
            {"id": str(service.id)}
        )
        count = result.scalar()
        assert count == 0, "Service should be deleted when client is deleted"

    @pytest.mark.asyncio
    async def test_service_delete_cascades_to_projects(self, async_session):
        """Test deleting service cascades to projects."""
        from uuid import uuid4
        from datetime import datetime

        # Create client and service
        client = Client(
            id=uuid4(),
            name="Test Client",
            business_domain="healthcare",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(client)
        await async_session.commit()

        service = Service(
            id=uuid4(),
            name="Test Service",
            client_id=client.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(service)
        await async_session.commit()

        # Create project
        project = Project(
            id=uuid4(),
            name="Test Project",
            description="Test description",
            service_id=service.id,
            project_type="new",
            status="draft",
            workflow_state={"currentStage": "business_analysis", "completedStages": []},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(project)
        await async_session.commit()

        # Delete service
        await async_session.delete(service)
        await async_session.commit()

        # Verify project was also deleted (cascade)
        result = await async_session.execute(
            text("SELECT COUNT(*) FROM projects WHERE id = :id"),
            {"id": str(project.id)}
        )
        count = result.scalar()
        assert count == 0, "Project should be deleted when service is deleted"

    @pytest.mark.asyncio
    async def test_project_delete_cascades_to_workflow_events(self, async_session):
        """Test deleting project cascades to workflow events."""
        from uuid import uuid4
        from datetime import datetime

        # Create client, service, and project
        client = Client(
            id=uuid4(),
            name="Test Client",
            business_domain="finance",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(client)
        await async_session.commit()

        service = Service(
            id=uuid4(),
            name="Test Service",
            client_id=client.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(service)
        await async_session.commit()

        project = Project(
            id=uuid4(),
            name="Test Project",
            description="Test description",
            service_id=service.id,
            project_type="new",
            status="active",
            workflow_state={"currentStage": "development", "completedStages": ["business_analysis"]},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(project)
        await async_session.commit()

        # Create workflow event
        event = WorkflowEvent(
            id=uuid4(),
            project_id=project.id,
            event_type="stage_advance",
            from_stage=None,
            to_stage="business_analysis",
            user_id=uuid4(),
            event_metadata={},
            timestamp=datetime.utcnow()
        )
        async_session.add(event)
        await async_session.commit()

        # Delete project
        await async_session.delete(project)
        await async_session.commit()

        # Verify workflow event was also deleted (cascade)
        result = await async_session.execute(
            text("SELECT COUNT(*) FROM workflow_events WHERE id = :id"),
            {"id": str(event.id)}
        )
        count = result.scalar()
        assert count == 0, "Workflow event should be deleted when project is deleted"

    @pytest.mark.asyncio
    async def test_contact_delete_cascades_to_service_contacts(self, async_session):
        """Test deleting contact cascades to service_contacts junction table."""
        from uuid import uuid4
        from datetime import datetime

        # Create contact
        contact = Contact(
            id=uuid4(),
            name="John Doe",
            email=f"john.doe.{uuid4()}@example.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(contact)
        await async_session.commit()

        # Create client and service
        client = Client(
            id=uuid4(),
            name="Test Client",
            business_domain="education",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(client)
        await async_session.commit()

        service = Service(
            id=uuid4(),
            name="Test Service",
            client_id=client.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(service)
        await async_session.commit()

        # Create service-contact relationship
        service_contact = ServiceContact(
            id=uuid4(),
            service_id=service.id,
            contact_id=contact.id,
            is_primary=True,
            relationship_type="main",
            created_at=datetime.utcnow()
        )
        async_session.add(service_contact)
        await async_session.commit()

        # Delete contact
        await async_session.delete(contact)
        await async_session.commit()

        # Verify service_contact was also deleted (cascade)
        result = await async_session.execute(
            text("SELECT COUNT(*) FROM service_contacts WHERE id = :id"),
            {"id": str(service_contact.id)}
        )
        count = result.scalar()
        assert count == 0, "ServiceContact should be deleted when contact is deleted"

    @pytest.mark.asyncio
    async def test_unique_constraint_prevents_duplicate_service_contacts(self, async_session):
        """Test unique constraint on service_contacts prevents duplicates."""
        from uuid import uuid4
        from datetime import datetime
        from sqlalchemy.exc import IntegrityError

        # Create contact, client, and service
        contact = Contact(
            id=uuid4(),
            name="Jane Doe",
            email=f"jane.doe.{uuid4()}@example.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(contact)
        await async_session.commit()

        client = Client(
            id=uuid4(),
            name="Test Client",
            business_domain="manufacturing",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(client)
        await async_session.commit()

        service = Service(
            id=uuid4(),
            name="Test Service",
            client_id=client.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        async_session.add(service)
        await async_session.commit()

        # Create first service-contact relationship
        service_contact1 = ServiceContact(
            id=uuid4(),
            service_id=service.id,
            contact_id=contact.id,
            is_primary=True,
            relationship_type="main",
            created_at=datetime.utcnow()
        )
        async_session.add(service_contact1)
        await async_session.commit()

        # Try to create duplicate - should fail
        service_contact2 = ServiceContact(
            id=uuid4(),
            service_id=service.id,  # Same service
            contact_id=contact.id,  # Same contact
            is_primary=False,
            relationship_type="secondary",
            created_at=datetime.utcnow()
        )
        async_session.add(service_contact2)

        with pytest.raises(IntegrityError):
            await async_session.commit()
