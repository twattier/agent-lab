"""
Integration tests for service category and assignment API endpoints.
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.factories import (
    ServiceFactory,
    ClientFactory,
    ContactFactory,
    ServiceCategoryFactory
)


@pytest.mark.asyncio
async def test_list_service_categories(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing service categories."""
    # Database should have seed data (9 categories), but let's create some test ones
    await ServiceCategoryFactory.create_async(
        db_session,
        code="TEST1",
        name="Test Category 1",
        is_active=True
    )
    await ServiceCategoryFactory.create_async(
        db_session,
        code="TEST2",
        name="Test Category 2",
        is_active=True
    )

    response = await test_client.get("/api/v1/service-categories")

    assert response.status_code == 200

    data = response.json()
    # Should include seed data + our test categories
    assert len(data["data"]) >= 2
    assert "Found" in data["message"]


@pytest.mark.asyncio
async def test_list_service_categories_filter_inactive(test_client: AsyncClient, db_session: AsyncSession):
    """Test filtering inactive service categories."""
    # Create active and inactive categories
    await ServiceCategoryFactory.create_async(
        db_session,
        code="ACTIVE",
        is_active=True
    )
    await ServiceCategoryFactory.create_async(
        db_session,
        code="INACTIVE",
        is_active=False
    )

    # Default should only show active
    response = await test_client.get("/api/v1/service-categories?is_active=true")

    assert response.status_code == 200
    data = response.json()

    # Verify all returned categories are active
    for category in data["data"]:
        assert category["is_active"] is True


@pytest.mark.asyncio
async def test_get_service_category_by_id(test_client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific service category by ID."""
    category = await ServiceCategoryFactory.create_async(
        db_session,
        code="TEST_GET",
        name="Test Get Category"
    )

    response = await test_client.get(f"/api/v1/service-categories/{category.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Service category retrieved successfully"

    category_data = data["data"]
    assert category_data["id"] == str(category.id)
    assert category_data["code"] == "TEST_GET"
    assert category_data["name"] == "Test Get Category"


@pytest.mark.asyncio
async def test_get_service_category_not_found(test_client: AsyncClient):
    """Test getting a non-existent service category."""
    non_existent_id = uuid.uuid4()

    response = await test_client.get(f"/api/v1/service-categories/{non_existent_id}")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Service category not found"


@pytest.mark.asyncio
async def test_assign_category_to_service(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning a category to a service."""
    # Create client, service, and category
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    category = await ServiceCategoryFactory.create_async(db_session, code="SALES")

    # Assign category to service
    assignment_data = {
        "service_category_id": str(category.id)
    }

    response = await test_client.post(
        f"/api/v1/services/{service.id}/categories",
        json=assignment_data
    )

    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "Category assigned to service successfully"

    assignment = data["data"]
    assert assignment["service_id"] == str(service.id)
    assert assignment["service_category_id"] == str(category.id)
    assert "created_at" in assignment


@pytest.mark.asyncio
async def test_assign_category_duplicate_fails(test_client: AsyncClient, db_session: AsyncSession):
    """Test that assigning the same category twice fails."""
    # Create client, service, and category
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    # First assignment should succeed
    assignment_data = {
        "service_category_id": str(category.id)
    }

    response1 = await test_client.post(
        f"/api/v1/services/{service.id}/categories",
        json=assignment_data
    )
    assert response1.status_code == 201

    # Second assignment should fail
    response2 = await test_client.post(
        f"/api/v1/services/{service.id}/categories",
        json=assignment_data
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already assigned" in data["detail"]


@pytest.mark.asyncio
async def test_assign_category_invalid_service(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning category to non-existent service."""
    category = await ServiceCategoryFactory.create_async(db_session)
    non_existent_service = uuid.uuid4()

    assignment_data = {
        "service_category_id": str(category.id)
    }

    response = await test_client.post(
        f"/api/v1/services/{non_existent_service}/categories",
        json=assignment_data
    )

    assert response.status_code == 404
    data = response.json()
    assert "Service not found" in data["detail"]


@pytest.mark.asyncio
async def test_assign_category_invalid_category(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning non-existent category to service."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    non_existent_category = uuid.uuid4()

    assignment_data = {
        "service_category_id": str(non_existent_category)
    }

    response = await test_client.post(
        f"/api/v1/services/{service.id}/categories",
        json=assignment_data
    )

    assert response.status_code == 404
    data = response.json()
    assert "Service category not found" in data["detail"]


@pytest.mark.asyncio
async def test_remove_category_from_service(test_client: AsyncClient, db_session: AsyncSession):
    """Test removing a category assignment from a service."""
    # Create and assign category
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    # Assign category
    assignment_data = {"service_category_id": str(category.id)}
    await test_client.post(f"/api/v1/services/{service.id}/categories", json=assignment_data)

    # Remove assignment
    response = await test_client.delete(
        f"/api/v1/services/{service.id}/categories/{category.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Category removed from service successfully"
    assert data["data"]["service_id"] == str(service.id)
    assert data["data"]["category_id"] == str(category.id)


@pytest.mark.asyncio
async def test_remove_category_not_assigned(test_client: AsyncClient, db_session: AsyncSession):
    """Test removing a category that wasn't assigned."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    category = await ServiceCategoryFactory.create_async(db_session)

    # Try to remove without assigning first
    response = await test_client.delete(
        f"/api/v1/services/{service.id}/categories/{category.id}"
    )

    assert response.status_code == 404
    data = response.json()
    assert "Category assignment not found" in data["detail"]


@pytest.mark.asyncio
async def test_assign_contact_to_service(test_client: AsyncClient, db_session: AsyncSession):
    """Test assigning a contact to a service."""
    # Create client, service, and contact
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    contact = await ContactFactory.create_async(db_session, email="contact@example.com")

    # Assign contact to service
    assignment_data = {
        "contact_id": str(contact.id),
        "is_primary": True,
        "relationship_type": "technical"
    }

    response = await test_client.post(
        f"/api/v1/services/{service.id}/contacts",
        json=assignment_data
    )

    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "Contact assigned to service successfully"

    assignment = data["data"]
    assert assignment["service_id"] == str(service.id)
    assert assignment["contact_id"] == str(contact.id)
    assert assignment["is_primary"] is True
    assert assignment["relationship_type"] == "technical"


@pytest.mark.asyncio
async def test_assign_contact_duplicate_fails(test_client: AsyncClient, db_session: AsyncSession):
    """Test that assigning the same contact twice fails."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    contact = await ContactFactory.create_async(db_session, email="dup@example.com")

    assignment_data = {
        "contact_id": str(contact.id)
    }

    # First assignment
    response1 = await test_client.post(
        f"/api/v1/services/{service.id}/contacts",
        json=assignment_data
    )
    assert response1.status_code == 201

    # Second assignment should fail
    response2 = await test_client.post(
        f"/api/v1/services/{service.id}/contacts",
        json=assignment_data
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already assigned" in data["detail"]


@pytest.mark.asyncio
async def test_remove_contact_from_service(test_client: AsyncClient, db_session: AsyncSession):
    """Test removing a contact assignment from a service."""
    # Create and assign contact
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    contact = await ContactFactory.create_async(db_session, email="remove@example.com")

    # Assign contact
    assignment_data = {"contact_id": str(contact.id)}
    await test_client.post(f"/api/v1/services/{service.id}/contacts", json=assignment_data)

    # Remove assignment
    response = await test_client.delete(
        f"/api/v1/services/{service.id}/contacts/{contact.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Contact removed from service successfully"


@pytest.mark.asyncio
async def test_remove_contact_not_assigned(test_client: AsyncClient, db_session: AsyncSession):
    """Test removing a contact that wasn't assigned."""
    client = await ClientFactory.create_async(db_session)
    service = await ServiceFactory.create_async(db_session, client_id=client.id)
    contact = await ContactFactory.create_async(db_session, email="notassigned@example.com")

    # Try to remove without assigning first
    response = await test_client.delete(
        f"/api/v1/services/{service.id}/contacts/{contact.id}"
    )

    assert response.status_code == 404
    data = response.json()
    assert "Contact assignment not found" in data["detail"]
