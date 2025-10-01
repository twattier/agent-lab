"""Workflow progression engine interface for Story 3.3 integration."""
from abc import ABC, abstractmethod
from uuid import UUID


class IWorkflowProgressionEngine(ABC):
    """Interface for workflow progression engine (Story 3.3).

    This interface defines the contract between Story 3.2 (Gate Management)
    and Story 3.3 (Workflow Progression Engine). Gate approval triggers
    workflow progression to the next stage.
    """

    @abstractmethod
    async def advance_workflow_stage(
        self,
        project_id: UUID,
        gate_id: UUID
    ) -> bool:
        """Advance workflow to next stage after gate approval.

        Args:
            project_id: Project UUID
            gate_id: Gate UUID that was approved

        Returns:
            True if progression successful, False otherwise

        Raises:
            WorkflowProgressionError: If progression fails
        """
        pass
