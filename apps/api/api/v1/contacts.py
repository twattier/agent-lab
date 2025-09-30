"""
Contact management API endpoints.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from core.database import get_db
from models.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    SuccessResponse,
)
from repositories.contact_repository import ContactRepository

router = APIRouter()


@router.post("/contacts", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Create a new contact."""
    repo = ContactRepository(db)

    # Check if email already exists
    existing_contact = await repo.get_by_email(contact_data.email)
    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    try:
        contact = await repo.create(
            name=contact_data.name,
            email=contact_data.email,
            role=contact_data.role,
            phone=contact_data.phone,
            is_active=contact_data.is_active
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    return SuccessResponse(
        data=ContactResponse.model_validate(contact),
        message="Contact created successfully"
    )


@router.get("/contacts", response_model=SuccessResponse)
async def list_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    name_search: Optional[str] = Query(None, description="Search contacts by name"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List contacts with optional filtering."""
    repo = ContactRepository(db)

    if name_search:
        contacts = await repo.search_by_name(name_search, skip, limit)
    elif is_active is not None:
        contacts = await repo.get_all(skip=skip, limit=limit, is_active=is_active)
    else:
        contacts = await repo.get_all(skip=skip, limit=limit)

    contact_responses = [ContactResponse.model_validate(contact) for contact in contacts]
    return SuccessResponse(
        data=contact_responses,
        message=f"Found {len(contact_responses)} contacts"
    )


@router.get("/contacts/{contact_id}", response_model=SuccessResponse)
async def get_contact(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a specific contact by ID."""
    repo = ContactRepository(db)
    contact = await repo.get_by_id(contact_id)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return SuccessResponse(
        data=ContactResponse.model_validate(contact),
        message="Contact retrieved successfully"
    )


@router.put("/contacts/{contact_id}", response_model=SuccessResponse)
async def update_contact(
    contact_id: uuid.UUID,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Update a contact."""
    repo = ContactRepository(db)

    # Check if contact exists
    existing_contact = await repo.get_by_id(contact_id)
    if not existing_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Check if new email conflicts with existing contact
    if contact_data.email and contact_data.email != existing_contact.email:
        email_conflict = await repo.get_by_email(contact_data.email)
        if email_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    # Prepare update data
    update_data = {}
    if contact_data.name is not None:
        update_data["name"] = contact_data.name
    if contact_data.email is not None:
        update_data["email"] = contact_data.email
    if contact_data.role is not None:
        update_data["role"] = contact_data.role
    if contact_data.phone is not None:
        update_data["phone"] = contact_data.phone
    if contact_data.is_active is not None:
        update_data["is_active"] = contact_data.is_active

    try:
        updated_contact = await repo.update(contact_id, **update_data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    return SuccessResponse(
        data=ContactResponse.model_validate(updated_contact),
        message="Contact updated successfully"
    )


@router.delete("/contacts/{contact_id}", response_model=SuccessResponse)
async def delete_contact(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Delete a contact."""
    repo = ContactRepository(db)

    # Check if contact exists
    existing_contact = await repo.get_by_id(contact_id)
    if not existing_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Delete contact
    deleted = await repo.delete(contact_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contact"
        )

    return SuccessResponse(
        data={"id": str(contact_id)},
        message="Contact deleted successfully"
    )
