"""Mock implementation of workflow progression engine for Story 3.2 testing."""
import logging
from uuid import UUID

from services.interfaces.workflow_progression_interface import IWorkflowProgressionEngine

logger = logging.getLogger(__name__)


class MockWorkflowProgressionEngine(IWorkflowProgressionEngine):
    """Mock workflow progression engine for testing Story 3.2.

    This mock will be replaced with the real implementation once Story 3.3 is complete.
    It logs calls and returns success to allow gate approval testing.
    """

    def __init__(self):
        """Initialize mock progression engine."""
        self.advance_called = False
        self.last_project_id: UUID | None = None
        self.last_gate_id: UUID | None = None
        self.call_count = 0

    async def advance_workflow_stage(
        self,
        project_id: UUID,
        gate_id: UUID
    ) -> bool:
        """Mock advance workflow stage method.

        Args:
            project_id: Project UUID
            gate_id: Gate UUID that was approved

        Returns:
            True (always succeeds in mock)
        """
        self.advance_called = True
        self.last_project_id = project_id
        self.last_gate_id = gate_id
        self.call_count += 1

        logger.info(
            f"MockWorkflowProgressionEngine.advance_workflow_stage called: "
            f"project_id={project_id}, gate_id={gate_id}, call_count={self.call_count}"
        )

        return True

    def reset(self):
        """Reset mock state for testing."""
        self.advance_called = False
        self.last_project_id = None
        self.last_gate_id = None
        self.call_count = 0
