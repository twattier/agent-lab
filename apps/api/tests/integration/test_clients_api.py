"""
Integration tests for client API endpoints.
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.factories import ClientFactory


@pytest.mark.asyncio
async def test_create_client(test_client: AsyncClient):
    """Test creating a new client."""
    client_data = {
        "name": "Test Client",
        "business_domain": "technology"
    }

    response = await test_client.post("/api/v1/clients", json=client_data)

    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "Client created successfully"
    assert "data" in data

    client = data["data"]
    assert client["name"] == "Test Client"
    assert client["business_domain"] == "technology"
    assert "id" in client
    assert "created_at" in client
    assert "updated_at" in client


@pytest.mark.asyncio
async def test_create_client_invalid_domain(test_client: AsyncClient):
    """Test creating client with invalid business domain."""
    client_data = {
        "name": "Test Client",
        "business_domain": "invalid_domain"
    }

    response = await test_client.post("/api/v1/clients", json=client_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_clients_empty(test_client: AsyncClient):
    """Test listing clients when none exist."""
    response = await test_client.get("/api/v1/clients")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 0 clients"
    assert data["data"] == []


@pytest.mark.asyncio
async def test_list_clients_with_data(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing clients with existing data."""
    # Create test clients
    await ClientFactory.create_async(db_session, name="Client 1", business_domain="healthcare")
    await ClientFactory.create_async(db_session, name="Client 2", business_domain="finance")

    response = await test_client.get("/api/v1/clients")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 2 clients"
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_client_by_id(test_client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific client by ID."""
    # Create test client
    client = await ClientFactory.create_async(
        db_session,
        name="Test Client",
        business_domain="technology"
    )

    response = await test_client.get(f"/api/v1/clients/{client.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Client retrieved successfully"

    client_data = data["data"]
    assert client_data["id"] == str(client.id)
    assert client_data["name"] == "Test Client"
    assert client_data["business_domain"] == "technology"


@pytest.mark.asyncio
async def test_get_client_not_found(test_client: AsyncClient):
    """Test getting a non-existent client."""
    non_existent_id = uuid.uuid4()

    response = await test_client.get(f"/api/v1/clients/{non_existent_id}")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Client not found"


@pytest.mark.asyncio
async def test_update_client(test_client: AsyncClient, db_session: AsyncSession):
    """Test updating a client."""
    # Create test client
    client = await ClientFactory.create_async(
        db_session,
        name="Original Name",
        business_domain="healthcare"
    )

    update_data = {
        "name": "Updated Name",
        "business_domain": "finance"
    }

    response = await test_client.put(f"/api/v1/clients/{client.id}", json=update_data)

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Client updated successfully"

    updated_client = data["data"]
    assert updated_client["name"] == "Updated Name"
    assert updated_client["business_domain"] == "finance"


@pytest.mark.asyncio
async def test_update_client_partial(test_client: AsyncClient, db_session: AsyncSession):
    """Test partial update of a client."""
    # Create test client
    client = await ClientFactory.create_async(
        db_session,
        name="Original Name",
        business_domain="healthcare"
    )

    update_data = {
        "name": "New Name"
        # business_domain not provided (partial update)
    }

    response = await test_client.put(f"/api/v1/clients/{client.id}", json=update_data)

    assert response.status_code == 200

    data = response.json()
    updated_client = data["data"]
    assert updated_client["name"] == "New Name"
    assert updated_client["business_domain"] == "healthcare"  # Unchanged


@pytest.mark.asyncio
async def test_delete_client(test_client: AsyncClient, db_session: AsyncSession):
    """Test deleting a client."""
    # Create test client
    client = await ClientFactory.create_async(db_session)

    response = await test_client.delete(f"/api/v1/clients/{client.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Client deleted successfully"
    assert data["data"]["id"] == str(client.id)

    # Verify client is actually deleted
    get_response = await test_client.get(f"/api/v1/clients/{client.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_filter_clients_by_business_domain(test_client: AsyncClient, db_session: AsyncSession):
    """Test filtering clients by business domain."""
    # Create clients with different domains
    await ClientFactory.create_async(db_session, business_domain="healthcare")
    await ClientFactory.create_async(db_session, business_domain="finance")
    await ClientFactory.create_async(db_session, business_domain="healthcare")

    response = await test_client.get("/api/v1/clients?business_domain=healthcare")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 2 clients"
    assert len(data["data"]) == 2

    for client in data["data"]:
        assert client["business_domain"] == "healthcare"


@pytest.mark.asyncio
async def test_search_clients_by_name(test_client: AsyncClient, db_session: AsyncSession):
    """Test searching clients by name."""
    # Create clients with different names
    await ClientFactory.create_async(db_session, name="Healthcare Corp")
    await ClientFactory.create_async(db_session, name="Finance Solutions")
    await ClientFactory.create_async(db_session, name="Health Systems")

    response = await test_client.get("/api/v1/clients?name_search=Health")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 2 clients"
    assert len(data["data"]) == 2

    # Both "Healthcare Corp" and "Health Systems" should match
    names = [client["name"] for client in data["data"]]
    assert "Healthcare Corp" in names
    assert "Health Systems" in names


@pytest.mark.asyncio
async def test_cascade_delete_client_to_services(test_client: AsyncClient, db_session: AsyncSession):
    """Test that deleting a client cascades to delete all its services."""
    from tests.fixtures.factories import ServiceFactory

    # Create client with services
    client = await ClientFactory.create_async(db_session, name="Cascade Test Client")
    service1 = await ServiceFactory.create_async(
        db_session,
        name="Service 1",
        client_id=client.id
    )
    service2 = await ServiceFactory.create_async(
        db_session,
        name="Service 2",
        client_id=client.id
    )

    # Verify services exist
    service1_response = await test_client.get(f"/api/v1/services/{service1.id}")
    assert service1_response.status_code == 200

    service2_response = await test_client.get(f"/api/v1/services/{service2.id}")
    assert service2_response.status_code == 200

    # Delete the client
    delete_response = await test_client.delete(f"/api/v1/clients/{client.id}")
    assert delete_response.status_code == 200

    # Verify services are also deleted (cascade delete)
    service1_after = await test_client.get(f"/api/v1/services/{service1.id}")
    assert service1_after.status_code == 404

    service2_after = await test_client.get(f"/api/v1/services/{service2.id}")
    assert service2_after.status_code == 404