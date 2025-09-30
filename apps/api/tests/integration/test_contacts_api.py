"""
Integration tests for contact API endpoints.
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.factories import ContactFactory


@pytest.mark.asyncio
async def test_create_contact(test_client: AsyncClient):
    """Test creating a new contact."""
    contact_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "role": "Product Manager",
        "phone": "+1-555-0123",
        "is_active": True
    }

    response = await test_client.post("/api/v1/contacts", json=contact_data)

    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "Contact created successfully"
    assert "data" in data

    contact = data["data"]
    assert contact["name"] == "John Doe"
    assert contact["email"] == "john.doe@example.com"
    assert contact["role"] == "Product Manager"
    assert contact["phone"] == "+1-555-0123"
    assert contact["is_active"] is True
    assert "id" in contact
    assert "created_at" in contact
    assert "updated_at" in contact


@pytest.mark.asyncio
async def test_create_contact_duplicate_email(test_client: AsyncClient, db_session: AsyncSession):
    """Test creating contact with duplicate email fails."""
    # Create first contact
    await ContactFactory.create_async(db_session, email="duplicate@example.com")

    # Try to create second contact with same email
    contact_data = {
        "name": "Another Person",
        "email": "duplicate@example.com"
    }

    response = await test_client.post("/api/v1/contacts", json=contact_data)

    assert response.status_code == 400
    data = response.json()
    assert "Email already exists" in data["detail"]


@pytest.mark.asyncio
async def test_create_contact_invalid_email(test_client: AsyncClient):
    """Test creating contact with invalid email format."""
    contact_data = {
        "name": "John Doe",
        "email": "not-an-email"
    }

    response = await test_client.post("/api/v1/contacts", json=contact_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_contacts_empty(test_client: AsyncClient):
    """Test listing contacts when none exist."""
    response = await test_client.get("/api/v1/contacts")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 0 contacts"
    assert data["data"] == []


@pytest.mark.asyncio
async def test_list_contacts_with_data(test_client: AsyncClient, db_session: AsyncSession):
    """Test listing contacts with existing data."""
    # Create test contacts
    await ContactFactory.create_async(db_session, name="Contact 1", email="contact1@example.com")
    await ContactFactory.create_async(db_session, name="Contact 2", email="contact2@example.com")

    response = await test_client.get("/api/v1/contacts")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 2 contacts"
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_filter_contacts_by_active_status(test_client: AsyncClient, db_session: AsyncSession):
    """Test filtering contacts by is_active status."""
    # Create active and inactive contacts
    await ContactFactory.create_async(db_session, email="active1@example.com", is_active=True)
    await ContactFactory.create_async(db_session, email="active2@example.com", is_active=True)
    await ContactFactory.create_async(db_session, email="inactive@example.com", is_active=False)

    response = await test_client.get("/api/v1/contacts?is_active=true")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 2 contacts"
    assert len(data["data"]) == 2

    for contact in data["data"]:
        assert contact["is_active"] is True


@pytest.mark.asyncio
async def test_search_contacts_by_name(test_client: AsyncClient, db_session: AsyncSession):
    """Test searching contacts by name."""
    # Create contacts with different names
    await ContactFactory.create_async(db_session, name="John Smith", email="john@example.com")
    await ContactFactory.create_async(db_session, name="Jane Doe", email="jane@example.com")
    await ContactFactory.create_async(db_session, name="John Doe", email="johndoe@example.com")

    response = await test_client.get("/api/v1/contacts?name_search=John")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Found 2 contacts"
    assert len(data["data"]) == 2

    # Both "John Smith" and "John Doe" should match
    names = [contact["name"] for contact in data["data"]]
    assert "John Smith" in names
    assert "John Doe" in names


@pytest.mark.asyncio
async def test_get_contact_by_id(test_client: AsyncClient, db_session: AsyncSession):
    """Test getting a specific contact by ID."""
    # Create test contact
    contact = await ContactFactory.create_async(
        db_session,
        name="Test Contact",
        email="test@example.com"
    )

    response = await test_client.get(f"/api/v1/contacts/{contact.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Contact retrieved successfully"

    contact_data = data["data"]
    assert contact_data["id"] == str(contact.id)
    assert contact_data["name"] == "Test Contact"
    assert contact_data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_contact_not_found(test_client: AsyncClient):
    """Test getting a non-existent contact."""
    non_existent_id = uuid.uuid4()

    response = await test_client.get(f"/api/v1/contacts/{non_existent_id}")

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "Contact not found"


@pytest.mark.asyncio
async def test_update_contact(test_client: AsyncClient, db_session: AsyncSession):
    """Test updating a contact."""
    # Create test contact
    contact = await ContactFactory.create_async(
        db_session,
        name="Original Name",
        email="original@example.com"
    )

    update_data = {
        "name": "Updated Name",
        "role": "New Role"
    }

    response = await test_client.put(f"/api/v1/contacts/{contact.id}", json=update_data)

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Contact updated successfully"

    updated_contact = data["data"]
    assert updated_contact["name"] == "Updated Name"
    assert updated_contact["role"] == "New Role"
    assert updated_contact["email"] == "original@example.com"  # Unchanged


@pytest.mark.asyncio
async def test_update_contact_email_conflict(test_client: AsyncClient, db_session: AsyncSession):
    """Test updating contact email to duplicate fails."""
    # Create two contacts
    contact1 = await ContactFactory.create_async(db_session, email="contact1@example.com")
    await ContactFactory.create_async(db_session, email="contact2@example.com")

    # Try to update contact1's email to contact2's email
    update_data = {
        "email": "contact2@example.com"
    }

    response = await test_client.put(f"/api/v1/contacts/{contact1.id}", json=update_data)

    assert response.status_code == 400
    data = response.json()
    assert "Email already exists" in data["detail"]


@pytest.mark.asyncio
async def test_delete_contact(test_client: AsyncClient, db_session: AsyncSession):
    """Test deleting a contact."""
    # Create test contact
    contact = await ContactFactory.create_async(db_session, email="delete@example.com")

    response = await test_client.delete(f"/api/v1/contacts/{contact.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Contact deleted successfully"
    assert data["data"]["id"] == str(contact.id)

    # Verify contact is actually deleted
    get_response = await test_client.get(f"/api/v1/contacts/{contact.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_pagination_contacts(test_client: AsyncClient, db_session: AsyncSession):
    """Test pagination of contacts list."""
    # Create 10 contacts
    for i in range(10):
        await ContactFactory.create_async(db_session, email=f"contact{i}@example.com")

    # Get first page (limit 5)
    response = await test_client.get("/api/v1/contacts?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5

    # Get second page
    response = await test_client.get("/api/v1/contacts?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
