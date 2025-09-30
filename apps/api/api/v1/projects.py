"""
Project management API endpoints.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    SuccessResponse,
    ProjectStatus,
    ProjectType
)
from repositories.project_repository import ProjectRepository
from repositories.service_repository import ServiceRepository

router = APIRouter()


@router.post("/projects", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Create a new project."""
    # Verify service exists
    service_repo = ServiceRepository(db)
    service = await service_repo.get_by_id(project_data.service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    project_repo = ProjectRepository(db)
    project = await project_repo.create(
        name=project_data.name,
        description=project_data.description,
        service_id=project_data.service_id,
        project_type=project_data.project_type.value,
        implementation_type_id=project_data.implementation_type_id,
        claude_code_path=project_data.claude_code_path
    )

    return SuccessResponse(
        data=ProjectResponse.model_validate(project),
        message="Project created successfully"
    )


@router.get("/projects", response_model=SuccessResponse)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service_id: Optional[uuid.UUID] = Query(None, description="Filter by service ID"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    project_type: Optional[ProjectType] = Query(None, description="Filter by project type"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List projects with optional filtering."""
    project_repo = ProjectRepository(db)

    if service_id:
        projects = await project_repo.get_by_service_id(service_id, skip, limit)
    elif status:
        projects = await project_repo.get_by_status(status.value, skip, limit)
    else:
        # Apply additional filters if needed
        filter_kwargs = {}
        if project_type:
            filter_kwargs["project_type"] = project_type.value

        projects = await project_repo.get_all(skip=skip, limit=limit, **filter_kwargs)

    project_responses = [ProjectResponse.model_validate(project) for project in projects]
    return SuccessResponse(
        data=project_responses,
        message=f"Found {len(project_responses)} projects"
    )


@router.get("/services/{service_id}/projects", response_model=SuccessResponse)
async def list_service_projects(
    service_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """List projects for a specific service."""
    # Verify service exists
    service_repo = ServiceRepository(db)
    service = await service_repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    project_repo = ProjectRepository(db)
    projects = await project_repo.get_by_service_id(service_id, skip, limit)

    project_responses = [ProjectResponse.model_validate(project) for project in projects]
    return SuccessResponse(
        data=project_responses,
        message=f"Found {len(project_responses)} projects for service"
    )


@router.get("/projects/{project_id}", response_model=SuccessResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a specific project by ID."""
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return SuccessResponse(
        data=ProjectResponse.model_validate(project),
        message="Project retrieved successfully"
    )


@router.get("/projects/{project_id}/with-service", response_model=SuccessResponse)
async def get_project_with_service(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Get a project with associated service information."""
    project_repo = ProjectRepository(db)
    project = await project_repo.get_with_service(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return SuccessResponse(
        data=ProjectResponse.model_validate(project),
        message="Project with service retrieved successfully"
    )


@router.post("/projects/search-similar", response_model=SuccessResponse)
async def search_similar_projects(
    query_vector: List[float],
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    threshold: float = Query(0.8, ge=0.0, le=1.0, description="Similarity threshold"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Search for similar projects using vector similarity."""
    if len(query_vector) != 1536:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query vector must be 1536 dimensions"
        )

    project_repo = ProjectRepository(db)
    projects = await project_repo.search_by_vector_similarity(
        query_vector, limit, threshold
    )

    project_responses = [ProjectResponse.model_validate(project) for project in projects]
    return SuccessResponse(
        data=project_responses,
        message=f"Found {len(project_responses)} similar projects"
    )


@router.put("/projects/{project_id}", response_model=SuccessResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Update a project."""
    project_repo = ProjectRepository(db)

    # Check if project exists
    existing_project = await project_repo.get_by_id(project_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Prepare update data
    update_data = {}
    if project_data.name is not None:
        update_data["name"] = project_data.name
    if project_data.description is not None:
        update_data["description"] = project_data.description
    if project_data.project_type is not None:
        update_data["project_type"] = project_data.project_type.value
    if project_data.implementation_type_id is not None:
        update_data["implementation_type_id"] = project_data.implementation_type_id
    if project_data.status is not None:
        update_data["status"] = project_data.status.value
    if project_data.workflow_state is not None:
        update_data["workflow_state"] = project_data.workflow_state
    if project_data.claude_code_path is not None:
        update_data["claude_code_path"] = project_data.claude_code_path

    # Update project
    updated_project = await project_repo.update(project_id, **update_data)

    return SuccessResponse(
        data=ProjectResponse.model_validate(updated_project),
        message="Project updated successfully"
    )


@router.put("/projects/{project_id}/embedding", response_model=SuccessResponse)
async def update_project_embedding(
    project_id: uuid.UUID,
    embedding: List[float],
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Update a project's vector embedding."""
    if len(embedding) != 1536:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Embedding vector must be 1536 dimensions"
        )

    project_repo = ProjectRepository(db)

    # Check if project exists
    existing_project = await project_repo.get_by_id(project_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update embedding
    updated_project = await project_repo.update_embedding(project_id, embedding)

    return SuccessResponse(
        data=ProjectResponse.model_validate(updated_project),
        message="Project embedding updated successfully"
    )


@router.delete("/projects/{project_id}", response_model=SuccessResponse)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Delete a project."""
    project_repo = ProjectRepository(db)

    # Check if project exists
    existing_project = await project_repo.get_by_id(project_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Delete project
    deleted = await project_repo.delete(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

    return SuccessResponse(
        data={"id": str(project_id)},
        message="Project deleted successfully"
    )