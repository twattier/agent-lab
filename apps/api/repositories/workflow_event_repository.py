"""
Repository for workflow event data access.
"""
import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import WorkflowEvent, WorkflowEventType
from repositories.base import BaseRepository


class WorkflowEventRepository(BaseRepository[WorkflowEvent]):
    """Repository for managing workflow events."""

    def __init__(self, db: AsyncSession):
        """
        Initialize workflow event repository.

        Args:
            db: AsyncSession for database operations
        """
        super().__init__(WorkflowEvent, db)

    async def create_event(
        self,
        project_id: uuid.UUID,
        event_type: WorkflowEventType,
        from_stage: Optional[str],
        to_stage: str,
        user_id: uuid.UUID,
        event_metadata: dict
    ) -> WorkflowEvent:
        """
        Create a new workflow event.

        Args:
            project_id: Project UUID
            event_type: Type of workflow event
            from_stage: Previous stage (None for gate events)
            to_stage: Target/current stage
            user_id: User performing the action
            metadata: Event metadata (notes, feedback, etc.)

        Returns:
            Created WorkflowEvent
        """
        return await self.create(
            project_id=project_id,
            event_type=event_type,
            from_stage=from_stage,
            to_stage=to_stage,
            user_id=user_id,
            event_metadata=event_metadata
        )

    async def get_project_history(
        self,
        project_id: uuid.UUID,
        event_type: Optional[WorkflowEventType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowEvent]:
        """
        Get workflow event history for a project.

        Args:
            project_id: Project UUID
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of WorkflowEvents sorted by timestamp DESC
        """
        query = select(WorkflowEvent).where(WorkflowEvent.project_id == project_id)

        if event_type:
            query = query.where(WorkflowEvent.event_type == event_type)

        query = query.order_by(desc(WorkflowEvent.timestamp)).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_event_by_id(self, event_id: uuid.UUID) -> Optional[WorkflowEvent]:
        """
        Get a specific workflow event by ID.

        Args:
            event_id: WorkflowEvent UUID

        Returns:
            WorkflowEvent if found, None otherwise
        """
        return await self.get_by_id(event_id)
