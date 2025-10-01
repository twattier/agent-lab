"""
Project management API endpoints with contacts and user categories.
Story 2.2 Implementation.
"""
import uuid
from typing import List, Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectContactCreate,
    ProjectContactUpdate,
    ProjectContactResponse,
    ProjectUserCategoryCreate,
    ProjectUserCategoryResponse,
    SuccessResponse,
    ProjectStatus,
    ProjectType
)
from repositories.project_repository import ProjectRepository
from repositories.implementation_type_repository import ImplementationTypeRepository

router = APIRouter()


def serialize_enums(data: dict) -> dict:
    """Convert Enum objects to their string values for database insertion."""
    result = {}
    for key, value in data.items():
        if isinstance(value, Enum):
            result[key] = value.value
        else:
            result[key] = value
    return result


# Project CRUD Endpoints

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Create a new project.

    - **name**: Project name (required, 1-255 characters)
    - **description**: Project description (required, min 1 character)
    - **service_id**: UUID of the parent service (required)
    - **project_type**: Project type - 'new' or 'existing' (required)
    - **implementation_type_id**: UUID of implementation type (optional)
    """
    project_repo = ProjectRepository(db)

    # Validate service exists
    from repositories.service_repository import ServiceRepository
    service_repo = ServiceRepository(db)
    service = await service_repo.get_with_projects(project_data.service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service_id"
        )

    # Validate implementation type if provided
    if project_data.implementation_type_id:
        impl_repo = ImplementationTypeRepository(db)
        impl_type = await impl_repo.get_implementation_type_by_id(project_data.implementation_type_id)
        if not impl_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid implementation_type_id"
            )

    # Create project - convert Pydantic model to dict and serialize enums
    project_dict = serialize_enums(project_data.model_dump())
    project = await project_repo.create_project(project_dict)

    return ProjectResponse.model_validate(project)


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service_id: Optional[uuid.UUID] = Query(None, description="Filter by service ID"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    project_type: Optional[ProjectType] = Query(None, description="Filter by project type"),
    implementation_type_id: Optional[uuid.UUID] = Query(None, description="Filter by implementation type"),
    db: AsyncSession = Depends(get_db)
) -> List[ProjectResponse]:
    """
    List projects with filtering and pagination.

    Filters:
    - **service_id**: Filter by service
    - **status**: Filter by project status (draft, active, blocked, completed, archived)
    - **project_type**: Filter by type (new, existing)
    - **implementation_type_id**: Filter by implementation type
    """
    project_repo = ProjectRepository(db)

    projects = await project_repo.list_projects(
        service_id=service_id,
        status=status.value if status else None,
        project_type=project_type.value if project_type else None,
        implementation_type_id=implementation_type_id,
        page=page,
        limit=limit
    )

    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> ProjectDetailResponse:
    """
    Get a specific project with all relationships.

    Includes:
    - Project details
    - Associated service
    - Implementation type
    - Assigned contacts
    - Assigned user categories
    """
    project_repo = ProjectRepository(db)
    project = await project_repo.get_project_by_id(project_id, include_relations=True)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Build response with relationships
    response_data = ProjectDetailResponse.model_validate(project)

    # Add contacts
    contacts = await project_repo.list_project_contacts(project_id)
    response_data.contacts = [ProjectContactResponse.model_validate(c) for c in contacts]

    # Add user categories
    categories = await project_repo.list_project_user_categories(project_id)
    response_data.user_categories = [cat.service_category for cat in categories if cat.service_category]

    return response_data


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Update a project.

    Updateable fields:
    - **name**: Project name
    - **description**: Project description
    - **status**: Project status
    - **implementation_type_id**: Implementation type
    - **claude_code_path**: Claude Code workspace path
    """
    project_repo = ProjectRepository(db)

    # Validate implementation type if provided
    if project_data.implementation_type_id:
        impl_repo = ImplementationTypeRepository(db)
        impl_type = await impl_repo.get_implementation_type_by_id(project_data.implementation_type_id)
        if not impl_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid implementation_type_id"
            )

    # Update project - serialize enums
    update_dict = serialize_enums({k: v for k, v in project_data.model_dump().items() if v is not None})
    updated_project = await project_repo.update_project(project_id, update_dict)

    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return ProjectResponse.model_validate(updated_project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a project.

    CASCADE behavior:
    - Deletes all project_contact associations
    - Deletes all project_service_category associations
    """
    project_repo = ProjectRepository(db)

    deleted = await project_repo.delete_project(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return None


# Project Contact Endpoints

@router.get("/projects/{project_id}/contacts", response_model=List[ProjectContactResponse])
async def list_project_contacts(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> List[ProjectContactResponse]:
    """
    List all contacts assigned to a project.

    Returns contact details with relationship metadata (contact_type, is_active).
    """
    project_repo = ProjectRepository(db)

    # Verify project exists
    project = await project_repo.get_project_by_id(project_id, include_relations=False)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    contacts = await project_repo.list_project_contacts(project_id)
    return [ProjectContactResponse.model_validate(c) for c in contacts]


@router.post("/projects/{project_id}/contacts", response_model=ProjectContactResponse, status_code=status.HTTP_201_CREATED)
async def assign_contact_to_project(
    project_id: uuid.UUID,
    contact_data: ProjectContactCreate,
    db: AsyncSession = Depends(get_db)
) -> ProjectContactResponse:
    """
    Assign a contact to a project.

    - **contact_id**: UUID of the contact (required)
    - **contact_type**: Role of contact (default: 'stakeholder')
    - **is_active**: Active status (default: true)

    Contact types: stakeholder, reviewer, approver, etc.
    """
    project_repo = ProjectRepository(db)

    # Verify project exists
    project = await project_repo.get_project_by_id(project_id, include_relations=False)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Assign contact
    try:
        assignment = await project_repo.assign_contact_to_project(
            project_id,
            contact_data.contact_id,
            {"contact_type": contact_data.contact_type, "is_active": contact_data.is_active}
        )
        return ProjectContactResponse.model_validate(assignment)
    except Exception as e:
        # Handle duplicate constraint violation
        if "uq_project_contact" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact already assigned to project with this type"
            )
        raise


@router.put("/projects/{project_id}/contacts/{contact_id}", response_model=ProjectContactResponse)
async def update_project_contact(
    project_id: uuid.UUID,
    contact_id: uuid.UUID,
    contact_data: ProjectContactUpdate,
    db: AsyncSession = Depends(get_db)
) -> ProjectContactResponse:
    """
    Update a project-contact relationship.

    - **contact_type**: Update contact role
    - **is_active**: Update active status
    """
    project_repo = ProjectRepository(db)

    update_dict = {k: v for k, v in contact_data.model_dump().items() if v is not None}
    updated = await project_repo.update_project_contact(project_id, contact_id, update_dict)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project-contact association not found"
        )

    return ProjectContactResponse.model_validate(updated)


@router.delete("/projects/{project_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact_from_project(
    project_id: uuid.UUID,
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove a contact from a project."""
    project_repo = ProjectRepository(db)

    removed = await project_repo.remove_contact_from_project(project_id, contact_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project-contact association not found"
        )

    return None


# Project User Category Endpoints

@router.get("/projects/{project_id}/user-categories", response_model=List[ProjectUserCategoryResponse])
async def list_project_user_categories(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> List[ProjectUserCategoryResponse]:
    """
    List all user categories (service categories) assigned to a project.

    Returns full category details (code, name, description, color).
    """
    project_repo = ProjectRepository(db)

    # Verify project exists
    project = await project_repo.get_project_by_id(project_id, include_relations=False)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    categories = await project_repo.list_project_user_categories(project_id)
    return [ProjectUserCategoryResponse.model_validate(c) for c in categories]


@router.post("/projects/{project_id}/user-categories", response_model=ProjectUserCategoryResponse, status_code=status.HTTP_201_CREATED)
async def assign_user_category_to_project(
    project_id: uuid.UUID,
    category_data: ProjectUserCategoryCreate,
    db: AsyncSession = Depends(get_db)
) -> ProjectUserCategoryResponse:
    """
    Assign a user category to a project.

    - **service_category_id**: UUID of the service category (required)
    """
    project_repo = ProjectRepository(db)

    # Verify project exists
    project = await project_repo.get_project_by_id(project_id, include_relations=False)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Assign category
    try:
        assignment = await project_repo.assign_user_category_to_project(
            project_id,
            category_data.service_category_id
        )
        return ProjectUserCategoryResponse.model_validate(assignment)
    except Exception as e:
        # Handle duplicate constraint violation
        if "uq_project_service_category" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already assigned to project"
            )
        raise


@router.delete("/projects/{project_id}/user-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_category_from_project(
    project_id: uuid.UUID,
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove a user category from a project."""
    project_repo = ProjectRepository(db)

    removed = await project_repo.remove_user_category_from_project(project_id, category_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project-category association not found"
        )

    return None
