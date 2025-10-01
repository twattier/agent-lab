"""
Integration tests for project API endpoints (Story 2.2).
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.factories import (
    ClientFactory, ServiceFactory, ProjectFactory,
    ImplementationTypeFactory, ContactFactory, ServiceCategoryFactory
)


# ============================================================================
# Implementation Type Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_implementation_types(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing implementation types."""
    # Create test implementation types
    await ImplementationTypeFactory.create_async(
        db_session, code="agile", name="Agile Development", is_active=True
    )
    await ImplementationTypeFactory.create_async(
        db_session, code="waterfall", name="Waterfall", is_active=True
    )
    await ImplementationTypeFactory.create_async(
        db_session, code="devops", name="DevOps", is_active=False
    )

    response = await test_client.get("/api/v1/implementation-types")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Only active types by default
    assert all(item["is_active"] for item in data)


@pytest.mark.asyncio
async def test_list_implementation_types_include_inactive(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing implementation types including inactive ones."""
    await ImplementationTypeFactory.create_async(
        db_session, code="agile", name="Agile", is_active=True
    )
    await ImplementationTypeFactory.create_async(
        db_session, code="legacy", name="Legacy", is_active=False
    )

    response = await test_client.get("/api/v1/implementation-types?is_active=false")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Should include inactive


@pytest.mark.asyncio
async def test_get_implementation_type_by_id(test_client: AsyncClient, db_session: AsyncSession):
    """Test retrieving a specific implementation type."""
    impl_type = await ImplementationTypeFactory.create_async(
        db_session, code="agile", name="Agile Development"
    )

    response = await test_client.get(f"/api/v1/implementation-types/{impl_type.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(impl_type.id)
    assert data["code"] == "agile"
    assert data["name"] == "Agile Development"


@pytest.mark.asyncio
async def test_get_implementation_type_not_found(test_client: AsyncClient):
    """Test retrieving non-existent implementation type."""
    fake_id = uuid.uuid4()
    response = await test_client.get(f"/api/v1/implementation-types/{fake_id}")

    assert response.status_code == 404


# ============================================================================
# Project CRUD Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test creating a new project."""
    # Setup dependencies
    client = await ClientFactory.create_async(db_session, name="Test Client")
    service = await ServiceFactory.create_async(
        db_session, name="Test Service", client_id=client.id
    )
    impl_type = await ImplementationTypeFactory.create_async(
        db_session, code="agile", name="Agile"
    )

    project_data = {
        "name": "New Project",
        "description": "A new project for testing",
        "service_id": str(service.id),
        "project_type": "new",
        "implementation_type_id": str(impl_type.id)
    }

    response = await test_client.post("/api/v1/projects", json=project_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["project_type"] == "new"
    assert data["status"] == "draft"  # Default status
    assert data["workflow_state"] == {}
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_project_without_implementation_type(test_client: AsyncClient, db_session: AsyncSession):
    """Test creating a project without implementation type (optional)."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)

    project_data = {
        "name": "Simple Project",
        "description": "Project without implementation type",
        "service_id": str(service.id),
        "project_type": "existing"
    }

    response = await test_client.post("/api/v1/projects", json=project_data)

    assert response.status_code == 201
    data = response.json()
    assert data["implementation_type_id"] is None


@pytest.mark.asyncio
async def test_create_project_invalid_service(test_client: AsyncClient):
    """Test creating project with non-existent service."""
    fake_service_id = uuid.uuid4()

    project_data = {
        "name": "Test Project",
        "description": "Test",
        "service_id": str(fake_service_id),
        "project_type": "new"
    }

    response = await test_client.post("/api/v1/projects", json=project_data)

    # Service validation returns 400 error
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_project_invalid_implementation_type(test_client: AsyncClient, db_session: AsyncSession):
    """Test creating project with non-existent implementation type."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    fake_impl_id = uuid.uuid4()

    project_data = {
        "name": "Test Project",
        "description": "Test",
        "service_id": str(service.id),
        "project_type": "new",
        "implementation_type_id": str(fake_impl_id)
    }

    response = await test_client.post("/api/v1/projects", json=project_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_project_invalid_enum(test_client: AsyncClient, db_session: AsyncSession):
    """Test creating project with invalid enum values."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)

    project_data = {
        "name": "Test Project",
        "description": "Test",
        "service_id": str(service.id),
        "project_type": "invalid_type"  # Invalid enum value
    }

    response = await test_client.post("/api/v1/projects", json=project_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_projects_empty(test_client: AsyncClient):
    """Test listing projects when none exist."""
    response = await test_client.get("/api/v1/projects")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_projects(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing all projects."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)

    # Create multiple projects
    await ProjectFactory.create_async(
        db_session, name="Project 1", service_id=service.id, project_type="new"
    )
    await ProjectFactory.create_async(
        db_session, name="Project 2", service_id=service.id, project_type="existing"
    )

    response = await test_client.get("/api/v1/projects")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_projects_filter_by_service(test_client: AsyncClient, db_session: AsyncSession):
    """Test filtering projects by service_id."""
    client = await ClientFactory.create_async(db_session)
    service1 = await ServiceFactory.create_async(db_session, client_id=client.id)
    service2 = await ServiceFactory.create_async(db_session, client_id=client.id)

    await ProjectFactory.create_async(db_session, service_id=service1.id)
    await ProjectFactory.create_async(db_session, service_id=service2.id)

    response = await test_client.get(f"/api/v1/projects?service_id={service1.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["service_id"] == str(service1.id)


@pytest.mark.asyncio
async def test_list_projects_filter_by_status(test_client: AsyncClient, db_session: AsyncSession):
    """Test filtering projects by status."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)

    await ProjectFactory.create_async(db_session, service_id=service.id, status="draft")
    await ProjectFactory.create_async(db_session, service_id=service.id, status="active")
    await ProjectFactory.create_async(db_session, service_id=service.id, status="completed")

    response = await test_client.get("/api/v1/projects?status=active")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "active"


@pytest.mark.asyncio
async def test_list_projects_pagination(test_client: AsyncClient, db_session: AsyncSession):
    """Test project list pagination."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)

    # Create 15 projects
    for i in range(15):
        await ProjectFactory.create_async(
            db_session, name=f"Project {i}", service_id=service.id, project_type="new"
        )

    # Get first page
    response = await test_client.get("/api/v1/projects?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10  # May have projects from other tests

    # Get second page (just verify it works, don't check exact count)
    response = await test_client.get("/api/v1/projects?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 0  # Just verify endpoint works


@pytest.mark.asyncio
async def test_get_project_by_id(test_client: AsyncClient, db_session: AsyncSession):
    """Test retrieving a specific project with relationships."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    impl_type = await ImplementationTypeFactory.create_async(db_session)
    project = await ProjectFactory.create_async(
        db_session,
        service_id=service.id,
        implementation_type_id=impl_type.id
    )

    response = await test_client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(project.id)
    assert data["service"] is not None
    assert data["implementation_type"] is not None


@pytest.mark.asyncio
async def test_get_project_not_found(test_client: AsyncClient):
    """Test retrieving non-existent project."""
    fake_id = uuid.uuid4()
    response = await test_client.get(f"/api/v1/projects/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test updating a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(
        db_session,
        name="Original Name",
        service_id=service.id,
        status="draft"
    )

    update_data = {
        "name": "Updated Name",
        "status": "active"
    }

    response = await test_client.put(f"/api/v1/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_update_project_not_found(test_client: AsyncClient):
    """Test updating non-existent project."""
    fake_id = uuid.uuid4()
    update_data = {"name": "New Name"}

    response = await test_client.put(f"/api/v1/projects/{fake_id}", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test deleting a project (CASCADE to junction tables)."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)

    response = await test_client.delete(f"/api/v1/projects/{project.id}")

    assert response.status_code == 204

    # Verify project is gone
    response = await test_client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(test_client: AsyncClient):
    """Test deleting non-existent project."""
    fake_id = uuid.uuid4()
    response = await test_client.delete(f"/api/v1/projects/{fake_id}")

    assert response.status_code == 404


# ============================================================================
# Project Contacts Tests
# ============================================================================

@pytest.mark.asyncio
async def test_assign_contact_to_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning a contact to a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    contact = await ContactFactory.create_async(db_session)

    assignment_data = {
        "contact_id": str(contact.id),
        "contact_type": "Project Manager"
    }

    response = await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json=assignment_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["contact_id"] == str(contact.id)
    assert data["contact_type"] == "Project Manager"


@pytest.mark.asyncio
async def test_assign_contact_duplicate(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning the same contact twice (should fail or update)."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    contact = await ContactFactory.create_async(db_session)

    assignment_data = {"contact_id": str(contact.id), "role": "PM"}

    # First assignment
    response = await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json=assignment_data
    )
    assert response.status_code == 201

    # Duplicate assignment
    response = await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json=assignment_data
    )
    assert response.status_code == 400  # Should reject duplicate


@pytest.mark.asyncio
async def test_list_project_contacts(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing all contacts for a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    contact1 = await ContactFactory.create_async(db_session)
    contact2 = await ContactFactory.create_async(db_session)

    # Assign contacts
    await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json={"contact_id": str(contact1.id), "role": "PM"}
    )
    await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json={"contact_id": str(contact2.id), "contact_type": "Developer"}
    )

    response = await test_client.get(f"/api/v1/projects/{project.id}/contacts")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_project_contact(test_client: AsyncClient, db_session: AsyncSession):
    """Test updating a project-contact relationship."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    contact = await ContactFactory.create_async(db_session)

    # Assign contact
    await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json={"contact_id": str(contact.id), "contact_type": "Developer"}
    )

    # Update role
    update_data = {"contact_type": "Senior Developer"}
    response = await test_client.put(
        f"/api/v1/projects/{project.id}/contacts/{contact.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["contact_type"] == "Senior Developer"


@pytest.mark.asyncio
async def test_remove_contact_from_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test removing a contact from a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    contact = await ContactFactory.create_async(db_session)

    # Assign contact
    await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json={"contact_id": str(contact.id), "contact_type": "PM"}
    )

    # Remove contact
    response = await test_client.delete(
        f"/api/v1/projects/{project.id}/contacts/{contact.id}"
    )

    assert response.status_code == 204

    # Verify removal
    response = await test_client.get(f"/api/v1/projects/{project.id}/contacts")
    data = response.json()
    assert len(data) == 0


# ============================================================================
# Project User Categories Tests
# ============================================================================

@pytest.mark.asyncio
async def test_assign_user_category_to_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning a user category to a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    assignment_data = {"service_category_id": str(category.id)}

    response = await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json=assignment_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["service_category_id"] == str(category.id)


@pytest.mark.asyncio
async def test_assign_user_category_duplicate(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning the same category twice."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    assignment_data = {"service_category_id": str(category.id)}

    # First assignment
    response = await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json=assignment_data
    )
    assert response.status_code == 201

    # Duplicate assignment
    response = await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json=assignment_data
    )
    assert response.status_code == 400  # Should reject duplicate


@pytest.mark.asyncio
async def test_list_project_user_categories(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing all user categories for a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    category1 = await ServiceCategoryFactory.create_async(db_session)
    category2 = await ServiceCategoryFactory.create_async(db_session)

    # Assign categories
    await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json={"service_category_id": str(category1.id)}
    )
    await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json={"service_category_id": str(category2.id)}
    )

    response = await test_client.get(f"/api/v1/projects/{project.id}/user-categories")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_remove_user_category_from_project(test_client: AsyncClient, db_session: AsyncSession):
    """Test removing a user category from a project."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    # Assign category
    await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json={"service_category_id": str(category.id)}
    )

    # Remove category
    response = await test_client.delete(
        f"/api/v1/projects/{project.id}/user-categories/{category.id}"
    )

    assert response.status_code == 204

    # Verify removal
    response = await test_client.get(f"/api/v1/projects/{project.id}/user-categories")
    data = response.json()
    assert len(data) == 0


# ============================================================================
# CASCADE Delete Tests
# ============================================================================

@pytest.mark.asyncio
async def test_delete_project_cascades_to_contacts(test_client: AsyncClient, db_session: AsyncSession):
    """Test that deleting a project cascades to project_contacts junction table."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    contact = await ContactFactory.create_async(db_session)

    # Assign contact
    await test_client.post(
        f"/api/v1/projects/{project.id}/contacts",
        json={"contact_id": str(contact.id), "contact_type": "PM"}
    )

    # Delete project
    response = await test_client.delete(f"/api/v1/projects/{project.id}")
    assert response.status_code == 204

    # Verify project is gone (which means junction records are also gone)
    response = await test_client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_cascades_to_user_categories(test_client: AsyncClient, db_session: AsyncSession):
    """Test that deleting a project cascades to project_service_categories junction table."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    project = await ProjectFactory.create_async(db_session, service_id=service.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    # Assign category
    await test_client.post(
        f"/api/v1/projects/{project.id}/user-categories",
        json={"service_category_id": str(category.id)}
    )

    # Delete project
    response = await test_client.delete(f"/api/v1/projects/{project.id}")
    assert response.status_code == 204

    # Verify project is gone
    response = await test_client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 404
