"""Repository for Project model and related operations."""
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import (
    Project,
    ProjectContact,
    ProjectServiceCategory,
    Contact,
    ServiceCategory,
    Service,
    ImplementationType,
)
from models.schemas import WorkflowState


class ProjectRepository:
    """Repository for managing projects and related associations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create_project(self, data: Dict[str, Any]) -> Project:
        """
        Create a new project with initialized workflow state.

        Args:
            data: Project data dictionary

        Returns:
            Created Project object
        """
        # Initialize workflow_state if not provided
        if "workflow_state" not in data or not data["workflow_state"]:
            initial_workflow = WorkflowState(
                currentStage="discovery",
                completedStages=[],
                stageData={"template": "bmad_method"},
                lastTransition=None,
                gateStatus="not_required"
            )
            data["workflow_state"] = initial_workflow.model_dump(mode='json')

        project = Project(**data)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def list_projects(
        self,
        service_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        project_type: Optional[str] = None,
        implementation_type_id: Optional[uuid.UUID] = None,
        page: int = 1,
        limit: int = 50,
    ) -> List[Project]:
        """
        List projects with optional filtering and pagination.

        Args:
            service_id: Filter by service ID
            status: Filter by project status
            project_type: Filter by project type
            implementation_type_id: Filter by implementation type ID
            page: Page number (1-indexed)
            limit: Number of results per page

        Returns:
            List of Project objects
        """
        query = select(Project).options(
            selectinload(Project.service),
            selectinload(Project.implementation_type),
        )

        # Apply filters
        filters = []
        if service_id:
            filters.append(Project.service_id == service_id)
        if status:
            filters.append(Project.status == status)
        if project_type:
            filters.append(Project.project_type == project_type)
        if implementation_type_id:
            filters.append(Project.implementation_type_id == implementation_type_id)

        if filters:
            query = query.where(and_(*filters))

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Order by most recent first
        query = query.order_by(Project.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project_by_id(
        self, project_id: uuid.UUID, include_relations: bool = True
    ) -> Optional[Project]:
        """
        Get a single project by ID with optional relationship loading.

        Args:
            project_id: UUID of the project
            include_relations: Whether to load related entities

        Returns:
            Project object or None if not found
        """
        query = select(Project).where(Project.id == project_id)

        if include_relations:
            query = query.options(
                selectinload(Project.service),
                selectinload(Project.implementation_type),
                selectinload(Project.project_contacts).selectinload(ProjectContact.contact),
                selectinload(Project.user_category_assignments).selectinload(
                    ProjectServiceCategory.service_category
                ),
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_project(
        self, project_id: uuid.UUID, data: Dict[str, Any]
    ) -> Optional[Project]:
        """
        Update a project.

        Args:
            project_id: UUID of the project to update
            data: Dictionary of fields to update

        Returns:
            Updated Project object or None if not found
        """
        project = await self.get_project_by_id(project_id, include_relations=False)
        if not project:
            return None

        for key, value in data.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: uuid.UUID) -> bool:
        """
        Delete a project (cascade deletes associations).

        Args:
            project_id: UUID of the project to delete

        Returns:
            True if deleted, False if not found
        """
        project = await self.get_project_by_id(project_id, include_relations=False)
        if not project:
            return False

        await self.db.delete(project)
        await self.db.commit()
        return True

    # Project Contact methods
    async def assign_contact_to_project(
        self, project_id: uuid.UUID, contact_id: uuid.UUID, data: Dict[str, Any]
    ) -> ProjectContact:
        """
        Assign a contact to a project.

        Args:
            project_id: UUID of the project
            contact_id: UUID of the contact
            data: Additional data (contact_type, is_active)

        Returns:
            Created ProjectContact association
        """
        project_contact = ProjectContact(
            project_id=project_id, contact_id=contact_id, **data
        )
        self.db.add(project_contact)
        await self.db.commit()
        await self.db.refresh(project_contact)
        return project_contact

    async def list_project_contacts(self, project_id: uuid.UUID) -> List[ProjectContact]:
        """
        List all contacts assigned to a project.

        Args:
            project_id: UUID of the project

        Returns:
            List of ProjectContact associations with contact data
        """
        query = (
            select(ProjectContact)
            .where(ProjectContact.project_id == project_id)
            .options(selectinload(ProjectContact.contact))
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project_contact(
        self, project_id: uuid.UUID, contact_id: uuid.UUID
    ) -> Optional[ProjectContact]:
        """
        Get a specific project-contact association.

        Args:
            project_id: UUID of the project
            contact_id: UUID of the contact

        Returns:
            ProjectContact association or None
        """
        query = select(ProjectContact).where(
            and_(
                ProjectContact.project_id == project_id,
                ProjectContact.contact_id == contact_id,
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_project_contact(
        self, project_id: uuid.UUID, contact_id: uuid.UUID, data: Dict[str, Any]
    ) -> Optional[ProjectContact]:
        """
        Update a project-contact relationship.

        Args:
            project_id: UUID of the project
            contact_id: UUID of the contact
            data: Fields to update

        Returns:
            Updated ProjectContact or None if not found
        """
        project_contact = await self.get_project_contact(project_id, contact_id)
        if not project_contact:
            return None

        for key, value in data.items():
            if hasattr(project_contact, key) and value is not None:
                setattr(project_contact, key, value)

        await self.db.commit()
        await self.db.refresh(project_contact)
        return project_contact

    async def remove_contact_from_project(
        self, project_id: uuid.UUID, contact_id: uuid.UUID
    ) -> bool:
        """
        Remove a contact from a project.

        Args:
            project_id: UUID of the project
            contact_id: UUID of the contact

        Returns:
            True if removed, False if not found
        """
        project_contact = await self.get_project_contact(project_id, contact_id)
        if not project_contact:
            return False

        await self.db.delete(project_contact)
        await self.db.commit()
        return True

    # Project User Category methods
    async def assign_user_category_to_project(
        self, project_id: uuid.UUID, category_id: uuid.UUID
    ) -> ProjectServiceCategory:
        """
        Assign a user category to a project.

        Args:
            project_id: UUID of the project
            category_id: UUID of the service category

        Returns:
            Created ProjectServiceCategory association
        """
        assignment = ProjectServiceCategory(
            project_id=project_id, service_category_id=category_id
        )
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def list_project_user_categories(
        self, project_id: uuid.UUID
    ) -> List[ProjectServiceCategory]:
        """
        List all user categories assigned to a project.

        Args:
            project_id: UUID of the project

        Returns:
            List of ProjectServiceCategory associations with category data
        """
        query = (
            select(ProjectServiceCategory)
            .where(ProjectServiceCategory.project_id == project_id)
            .options(selectinload(ProjectServiceCategory.service_category))
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project_user_category(
        self, project_id: uuid.UUID, category_id: uuid.UUID
    ) -> Optional[ProjectServiceCategory]:
        """
        Get a specific project-category association.

        Args:
            project_id: UUID of the project
            category_id: UUID of the service category

        Returns:
            ProjectServiceCategory association or None
        """
        query = select(ProjectServiceCategory).where(
            and_(
                ProjectServiceCategory.project_id == project_id,
                ProjectServiceCategory.service_category_id == category_id,
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def remove_user_category_from_project(
        self, project_id: uuid.UUID, category_id: uuid.UUID
    ) -> bool:
        """
        Remove a user category from a project.

        Args:
            project_id: UUID of the project
            category_id: UUID of the service category

        Returns:
            True if removed, False if not found
        """
        assignment = await self.get_project_user_category(project_id, category_id)
        if not assignment:
            return False

        await self.db.delete(assignment)
        await self.db.commit()
        return True

    # Workflow State methods
    async def update_workflow_state(
        self, project_id: uuid.UUID, workflow_state: WorkflowState
    ) -> Optional[Project]:
        """
        Update workflow state for a project with atomic operation.

        Args:
            project_id: UUID of the project
            workflow_state: WorkflowState object to update

        Returns:
            Updated Project object or None if not found
        """
        project = await self.get_project_by_id(project_id, include_relations=False)
        if not project:
            return None

        # Convert WorkflowState to dict for JSONB storage
        project.workflow_state = workflow_state.model_dump(mode='json')

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_workflow_state(self, project_id: uuid.UUID) -> Optional[WorkflowState]:
        """
        Get workflow state from project JSONB field.

        Args:
            project_id: UUID of the project

        Returns:
            WorkflowState object or None if project not found or state not initialized
        """
        project = await self.get_project_by_id(project_id, include_relations=False)
        if not project:
            return None

        workflow_data = project.workflow_state
        if not workflow_data:
            return None

        try:
            return WorkflowState(**workflow_data)
        except Exception:
            # Handle deserialization errors gracefully
            return None
