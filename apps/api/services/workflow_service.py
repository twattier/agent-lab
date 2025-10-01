"""
Workflow service for managing project workflow state transitions and gate approvals.
"""
import uuid
from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.workflow_templates import load_workflow_template, get_stage, WorkflowTemplate
from models.database import Project, WorkflowEvent, WorkflowEventType
from models.schemas import WorkflowState, GateStatus
from services.workflow_validators import validate_stage_transition, validate_gate_requirement


class WorkflowService:
    """Service for managing workflow state transitions and gate approvals."""

    def __init__(self, db: AsyncSession):
        """
        Initialize workflow service.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db
        self._default_template_name = "bmad_method"

    async def get_project(self, project_id: uuid.UUID) -> Optional[Project]:
        """
        Get project by ID.

        Args:
            project_id: Project UUID

        Returns:
            Project if found, None otherwise
        """
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_workflow_state(self, project_id: uuid.UUID) -> Optional[WorkflowState]:
        """
        Get current workflow state for a project.

        Args:
            project_id: Project UUID

        Returns:
            WorkflowState if project exists, None otherwise
        """
        project = await self.get_project(project_id)
        if not project:
            return None

        # Parse workflow_state JSONB to WorkflowState model
        workflow_data = project.workflow_state or {}
        if not workflow_data:
            return None

        return WorkflowState(**workflow_data)

    async def get_available_transitions(
        self,
        project_id: uuid.UUID,
        template_name: str = "bmad_method"
    ) -> List[str]:
        """
        Get list of available next stages for a project.

        Args:
            project_id: Project UUID
            template_name: Workflow template name

        Returns:
            List of available stage IDs
        """
        workflow_state = await self.get_workflow_state(project_id)
        if not workflow_state:
            return []

        template = load_workflow_template(template_name)
        stage = get_stage(template, workflow_state.currentStage)

        if not stage:
            return []

        return stage.next_stages

    async def initialize_workflow(
        self,
        project_id: uuid.UUID,
        template_name: str = "bmad_method"
    ) -> WorkflowState:
        """
        Initialize workflow state for a new project.

        Args:
            project_id: Project UUID
            template_name: Workflow template name (default: "bmad_method")

        Returns:
            Initialized WorkflowState

        Raises:
            ValueError: If project not found
        """
        project = await self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Create initial workflow state
        initial_state = WorkflowState(
            currentStage="discovery",
            completedStages=[],
            stageData={"template": template_name},
            lastTransition=None,
            gateStatus=GateStatus.NOT_REQUIRED
        )

        # Update project with initial workflow state
        project.workflow_state = initial_state.model_dump(mode='json')
        await self.db.commit()
        await self.db.refresh(project)

        return initial_state

    async def advance_stage(
        self,
        project_id: uuid.UUID,
        to_stage: str,
        user_id: uuid.UUID,
        notes: Optional[str] = None,
        stage_data: Optional[dict] = None
    ) -> WorkflowState:
        """
        Advance workflow to next stage with validation.

        Args:
            project_id: Project UUID
            to_stage: Target stage ID
            user_id: User performing the transition
            notes: Optional notes for the transition
            stage_data: Optional additional stage data

        Returns:
            Updated WorkflowState

        Raises:
            ValueError: If validation fails or project not found
        """
        # Get project and current workflow state
        project = await self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        workflow_state = await self.get_workflow_state(project_id)
        if not workflow_state:
            raise ValueError(f"Workflow state not initialized for project {project_id}")

        # Load template
        template_name = workflow_state.stageData.get("template", self._default_template_name)
        template = load_workflow_template(template_name)

        # Validate transition
        is_valid, error_msg = validate_stage_transition(
            workflow_state.currentStage,
            to_stage,
            workflow_state.gateStatus,
            template
        )

        if not is_valid:
            raise ValueError(error_msg)

        # Store current stage for event logging
        from_stage = workflow_state.currentStage

        # Update workflow state
        workflow_state.completedStages.append(workflow_state.currentStage)
        workflow_state.currentStage = to_stage
        workflow_state.lastTransition = datetime.utcnow()

        # Merge stage data
        if stage_data:
            workflow_state.stageData.update(stage_data)

        # Check if new stage requires gate approval
        new_stage = get_stage(template, to_stage)
        if new_stage and new_stage.gate_required:
            workflow_state.gateStatus = GateStatus.PENDING
        else:
            workflow_state.gateStatus = GateStatus.NOT_REQUIRED

        # Update project
        project.workflow_state = workflow_state.model_dump(mode='json')

        # Create workflow event
        event_metadata = {"notes": notes} if notes else {}
        if stage_data:
            event_metadata["stage_data"] = stage_data

        event = WorkflowEvent(
            project_id=project_id,
            event_type=WorkflowEventType.STAGE_ADVANCE,
            from_stage=from_stage,
            to_stage=to_stage,
            user_id=user_id,
            event_metadata=event_metadata
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(project)

        return workflow_state

    async def approve_gate(
        self,
        project_id: uuid.UUID,
        approver_id: uuid.UUID,
        feedback: Optional[str] = None
    ) -> WorkflowState:
        """
        Approve gate for current stage.

        Args:
            project_id: Project UUID
            approver_id: User approving the gate
            feedback: Optional approval feedback

        Returns:
            Updated WorkflowState

        Raises:
            ValueError: If project not found or gate not required
        """
        # Get project and workflow state
        project = await self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        workflow_state = await self.get_workflow_state(project_id)
        if not workflow_state:
            raise ValueError(f"Workflow state not initialized for project {project_id}")

        # Load template and validate gate requirement
        template_name = workflow_state.stageData.get("template", self._default_template_name)
        template = load_workflow_template(template_name)

        gate_required, error_msg = validate_gate_requirement(
            workflow_state.currentStage,
            template
        )

        if not gate_required:
            raise ValueError(error_msg)

        # Update gate status
        workflow_state.gateStatus = GateStatus.APPROVED

        # Update project
        project.workflow_state = workflow_state.model_dump(mode='json')

        # Create workflow event
        event_metadata = {
            "approver_id": str(approver_id),
            "approval_date": datetime.utcnow().isoformat()
        }
        if feedback:
            event_metadata["feedback"] = feedback

        event = WorkflowEvent(
            project_id=project_id,
            event_type=WorkflowEventType.GATE_APPROVED,
            from_stage=None,
            to_stage=workflow_state.currentStage,
            user_id=approver_id,
            event_metadata=event_metadata
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(project)

        return workflow_state

    async def reject_gate(
        self,
        project_id: uuid.UUID,
        approver_id: uuid.UUID,
        feedback: Optional[str] = None
    ) -> WorkflowState:
        """
        Reject gate for current stage.

        Args:
            project_id: Project UUID
            approver_id: User rejecting the gate
            feedback: Optional rejection feedback

        Returns:
            Updated WorkflowState

        Raises:
            ValueError: If project not found or gate not required
        """
        # Get project and workflow state
        project = await self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        workflow_state = await self.get_workflow_state(project_id)
        if not workflow_state:
            raise ValueError(f"Workflow state not initialized for project {project_id}")

        # Load template and validate gate requirement
        template_name = workflow_state.stageData.get("template", self._default_template_name)
        template = load_workflow_template(template_name)

        gate_required, error_msg = validate_gate_requirement(
            workflow_state.currentStage,
            template
        )

        if not gate_required:
            raise ValueError(error_msg)

        # Update gate status
        workflow_state.gateStatus = GateStatus.REJECTED

        # Update project
        project.workflow_state = workflow_state.model_dump(mode='json')

        # Create workflow event
        event_metadata = {
            "approver_id": str(approver_id),
            "rejection_date": datetime.utcnow().isoformat()
        }
        if feedback:
            event_metadata["feedback"] = feedback

        event = WorkflowEvent(
            project_id=project_id,
            event_type=WorkflowEventType.GATE_REJECTED,
            from_stage=None,
            to_stage=workflow_state.currentStage,
            user_id=approver_id,
            event_metadata=event_metadata
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(project)

        return workflow_state
