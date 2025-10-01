"""
Implementation Type API endpoints.
Story 2.2 Implementation.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import ImplementationTypeResponse
from repositories.implementation_type_repository import ImplementationTypeRepository

router = APIRouter()


@router.get("/implementation-types", response_model=List[ImplementationTypeResponse])
async def list_implementation_types(
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
) -> List[ImplementationTypeResponse]:
    """
    List all implementation types with optional filtering.

    Query Parameters:
    - **is_active**: Filter by active status (default: True, returns only active types)
      - Set to `null` to get all types regardless of status
      - Set to `false` to get only inactive types

    Returns list of implementation types:
    - RAG: Retrieval-Augmented Generation
    - AGENTIC: Agentic AI
    - AUTOMATON: Process Automation
    - CHATBOT: Conversational AI
    - ANALYTICS: AI Analytics
    - RECOMMENDATION: Recommendation Engine
    """
    impl_repo = ImplementationTypeRepository(db)
    impl_types = await impl_repo.list_implementation_types(is_active=is_active)

    return [ImplementationTypeResponse.model_validate(it) for it in impl_types]


@router.get("/implementation-types/{id}", response_model=ImplementationTypeResponse)
async def get_implementation_type(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> ImplementationTypeResponse:
    """
    Get a single implementation type by ID.

    Returns full implementation type details including:
    - id: UUID
    - code: Unique code (e.g., 'RAG', 'AGENTIC')
    - name: Full name
    - description: Detailed description
    - is_active: Active status
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    """
    impl_repo = ImplementationTypeRepository(db)
    impl_type = await impl_repo.get_implementation_type_by_id(id)

    if not impl_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Implementation type not found"
        )

    return ImplementationTypeResponse.model_validate(impl_type)
