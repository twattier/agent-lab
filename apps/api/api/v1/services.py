"""
Service management API endpoints.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    SuccessResponse
)
from repositories.service_repository import ServiceRepository
from repositories.client_repository import ClientRepository

router = APIRouter()


@router.post("/services", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Create a new service."""
    # Verify client exists
    client_repo = ClientRepository(db)
    client = await client_repo.get_by_id(service_data.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    service_repo = ServiceRepository(db)
    service = await service_repo.create(
        name=service_data.name,
        description=service_data.description,
        client_id=service_data.client_id
    )

    return SuccessResponse(
        data=ServiceResponse.model_validate(service),
        message="Service created successfully"
    )


@router.get("/services", response_model=SuccessResponse)
async def list_services(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    name_search: Optional[str] = Query(None, description="Search services by name"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List services with optional filtering."""
    service_repo = ServiceRepository(db)

    if client_id and name_search:
        services = await service_repo.search_by_name_and_client(name_search, client_id, skip, limit)
    elif client_id:
        services = await service_repo.get_by_client_id(client_id, skip, limit)
    else:
        services = await service_repo.get_all(skip=skip, limit=limit)

    service_responses = [ServiceResponse.model_validate(service) for service in services]
    return SuccessResponse(
        data=service_responses,
        message=f"Found {len(service_responses)} services"
    )


@router.get("/clients/{client_id}/services", response_model=SuccessResponse)
async def list_client_services(
    client_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List services for a specific client."""
    # Verify client exists
    client_repo = ClientRepository(db)
    client = await client_repo.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    service_repo = ServiceRepository(db)
    services = await service_repo.get_by_client_id(client_id, skip, limit)

    service_responses = [ServiceResponse.model_validate(service) for service in services]
    return SuccessResponse(
        data=service_responses,
        message=f"Found {len(service_responses)} services for client"
    )


@router.get("/services/{service_id}", response_model=SuccessResponse)
async def get_service(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a specific service by ID."""
    service_repo = ServiceRepository(db)
    service = await service_repo.get_by_id(service_id)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return SuccessResponse(
        data=ServiceResponse.model_validate(service),
        message="Service retrieved successfully"
    )


@router.get("/services/{service_id}/with-projects", response_model=SuccessResponse)
async def get_service_with_projects(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a service with all associated projects."""
    service_repo = ServiceRepository(db)
    service = await service_repo.get_with_projects(service_id)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return SuccessResponse(
        data=ServiceResponse.model_validate(service),
        message="Service with projects retrieved successfully"
    )


@router.put("/services/{service_id}", response_model=SuccessResponse)
async def update_service(
    service_id: uuid.UUID,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Update a service."""
    service_repo = ServiceRepository(db)

    # Check if service exists
    existing_service = await service_repo.get_by_id(service_id)
    if not existing_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Prepare update data
    update_data = {}
    if service_data.name is not None:
        update_data["name"] = service_data.name
    if service_data.description is not None:
        update_data["description"] = service_data.description

    # Update service
    updated_service = await service_repo.update(service_id, **update_data)

    return SuccessResponse(
        data=ServiceResponse.model_validate(updated_service),
        message="Service updated successfully"
    )


@router.delete("/services/{service_id}", response_model=SuccessResponse)
async def delete_service(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Delete a service."""
    service_repo = ServiceRepository(db)

    # Check if service exists
    existing_service = await service_repo.get_by_id(service_id)
    if not existing_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Delete service
    deleted = await service_repo.delete(service_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete service"
        )

    return SuccessResponse(
        data={"id": str(service_id)},
        message="Service deleted successfully"
    )