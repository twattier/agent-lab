"""
Client management API endpoints.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    SuccessResponse,
    BusinessDomain
)
from repositories.client_repository import ClientRepository

router = APIRouter()


@router.post("/clients", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Create a new client."""
    repo = ClientRepository(db)
    client = await repo.create(
        name=client_data.name,
        business_domain=client_data.business_domain.value
    )
    return SuccessResponse(
        data=ClientResponse.model_validate(client),
        message="Client created successfully"
    )


@router.get("/clients", response_model=SuccessResponse)
async def list_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    business_domain: Optional[BusinessDomain] = Query(None, description="Filter by business domain"),
    name_search: Optional[str] = Query(None, description="Search clients by name"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List clients with optional filtering."""
    repo = ClientRepository(db)

    if name_search:
        clients = await repo.search_by_name(name_search, skip, limit)
    elif business_domain:
        clients = await repo.get_by_business_domain(business_domain.value, skip, limit)
    else:
        clients = await repo.get_all(skip=skip, limit=limit)

    client_responses = [ClientResponse.model_validate(client) for client in clients]
    return SuccessResponse(
        data=client_responses,
        message=f"Found {len(client_responses)} clients"
    )


@router.get("/clients/{client_id}", response_model=SuccessResponse)
async def get_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a specific client by ID."""
    repo = ClientRepository(db)
    client = await repo.get_by_id(client_id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    return SuccessResponse(
        data=ClientResponse.model_validate(client),
        message="Client retrieved successfully"
    )


@router.get("/clients/{client_id}/with-services", response_model=SuccessResponse)
async def get_client_with_services(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a client with all associated services."""
    repo = ClientRepository(db)
    client = await repo.get_with_services(client_id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    return SuccessResponse(
        data=ClientResponse.model_validate(client),
        message="Client with services retrieved successfully"
    )


@router.put("/clients/{client_id}", response_model=SuccessResponse)
async def update_client(
    client_id: uuid.UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Update a client."""
    repo = ClientRepository(db)

    # Check if client exists
    existing_client = await repo.get_by_id(client_id)
    if not existing_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Prepare update data
    update_data = {}
    if client_data.name is not None:
        update_data["name"] = client_data.name
    if client_data.business_domain is not None:
        update_data["business_domain"] = client_data.business_domain.value

    # Update client
    updated_client = await repo.update(client_id, **update_data)

    return SuccessResponse(
        data=ClientResponse.model_validate(updated_client),
        message="Client updated successfully"
    )


@router.delete("/clients/{client_id}", response_model=SuccessResponse)
async def delete_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Delete a client."""
    repo = ClientRepository(db)

    # Check if client exists
    existing_client = await repo.get_by_id(client_id)
    if not existing_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Delete client
    deleted = await repo.delete(client_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete client"
        )

    return SuccessResponse(
        data={"id": str(client_id)},
        message="Client deleted successfully"
    )