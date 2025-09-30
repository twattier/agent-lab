"""
Service Category API endpoints.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from models.schemas import (
    ServiceCategoryResponse,
    ServiceCategoryAssignmentCreate,
    ServiceCategoryAssignmentResponse,
    ServiceContactCreate,
    ServiceContactResponse,
    SuccessResponse,
)
from models.database import ServiceCategory, ServiceServiceCategory, ServiceContact, Service, Contact
from repositories.service_category_repository import ServiceCategoryRepository

router = APIRouter()


@router.get("/service-categories", response_model=SuccessResponse)
async def list_service_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List all service categories."""
    repo = ServiceCategoryRepository(db)

    if is_active is not None:
        categories = await repo.get_all(skip=skip, limit=limit, is_active=is_active)
    else:
        categories = await repo.get_all(skip=skip, limit=limit)

    category_responses = [ServiceCategoryResponse.model_validate(cat) for cat in categories]
    return SuccessResponse(
        data=category_responses,
        message=f"Found {len(category_responses)} service categories"
    )


@router.get("/service-categories/{category_id}", response_model=SuccessResponse)
async def get_service_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a specific service category by ID."""
    repo = ServiceCategoryRepository(db)
    category = await repo.get_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found"
        )

    return SuccessResponse(
        data=ServiceCategoryResponse.model_validate(category),
        message="Service category retrieved successfully"
    )


@router.post("/services/{service_id}/categories", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def assign_category_to_service(
    service_id: uuid.UUID,
    assignment_data: ServiceCategoryAssignmentCreate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Assign a category to a service."""
    # Verify service exists
    service_result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Verify category exists
    category_result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.id == assignment_data.service_category_id)
    )
    category = category_result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found"
        )

    # Check if assignment already exists
    existing_result = await db.execute(
        select(ServiceServiceCategory).where(
            ServiceServiceCategory.service_id == service_id,
            ServiceServiceCategory.service_category_id == assignment_data.service_category_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already assigned to this service"
        )

    # Create assignment
    assignment = ServiceServiceCategory(
        service_id=service_id,
        service_category_id=assignment_data.service_category_id
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return SuccessResponse(
        data=ServiceCategoryAssignmentResponse.model_validate(assignment),
        message="Category assigned to service successfully"
    )


@router.delete("/services/{service_id}/categories/{category_id}", response_model=SuccessResponse)
async def remove_category_from_service(
    service_id: uuid.UUID,
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Remove a category assignment from a service."""
    # Find the assignment
    result = await db.execute(
        select(ServiceServiceCategory).where(
            ServiceServiceCategory.service_id == service_id,
            ServiceServiceCategory.service_category_id == category_id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category assignment not found"
        )

    await db.delete(assignment)
    await db.commit()

    return SuccessResponse(
        data={"service_id": str(service_id), "category_id": str(category_id)},
        message="Category removed from service successfully"
    )


@router.post("/services/{service_id}/contacts", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def assign_contact_to_service(
    service_id: uuid.UUID,
    contact_data: ServiceContactCreate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Assign a contact to a service."""
    # Verify service exists
    service_result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Verify contact exists
    contact_result = await db.execute(
        select(Contact).where(Contact.id == contact_data.contact_id)
    )
    contact = contact_result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Check if assignment already exists
    existing_result = await db.execute(
        select(ServiceContact).where(
            ServiceContact.service_id == service_id,
            ServiceContact.contact_id == contact_data.contact_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact already assigned to this service"
        )

    # Create assignment
    assignment = ServiceContact(
        service_id=service_id,
        contact_id=contact_data.contact_id,
        is_primary=contact_data.is_primary,
        relationship_type=contact_data.relationship_type
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return SuccessResponse(
        data=ServiceContactResponse.model_validate(assignment),
        message="Contact assigned to service successfully"
    )


@router.delete("/services/{service_id}/contacts/{contact_id}", response_model=SuccessResponse)
async def remove_contact_from_service(
    service_id: uuid.UUID,
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Remove a contact assignment from a service."""
    # Find the assignment
    result = await db.execute(
        select(ServiceContact).where(
            ServiceContact.service_id == service_id,
            ServiceContact.contact_id == contact_id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact assignment not found"
        )

    await db.delete(assignment)
    await db.commit()

    return SuccessResponse(
        data={"service_id": str(service_id), "contact_id": str(contact_id)},
        message="Contact removed from service successfully"
    )
