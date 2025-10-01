"""
Unit tests for workflow service.
"""
import uuid
from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from services.workflow_service import WorkflowService
from models.schemas import WorkflowState, GateStatus
from models.database import Project, WorkflowEventType


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def workflow_service(mock_db):
    """Create workflow service with mock database."""
    return WorkflowService(mock_db)


@pytest.fixture
def mock_project():
    """Create mock project with initialized workflow state."""
    project = MagicMock(spec=Project)
    project.id = uuid.uuid4()
    project.workflow_state = {
        "currentStage": "discovery",
        "completedStages": [],
        "stageData": {"template": "bmad_method"},
        "lastTransition": None,
        "gateStatus": "not_required"
    }
    return project


class TestWorkflowService:
    """Test workflow service business logic."""

    @pytest.mark.asyncio
    async def test_initialize_workflow(self, workflow_service, mock_db, mock_project):
        """Test workflow initialization on project creation."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        # Initialize workflow
        workflow_state = await workflow_service.initialize_workflow(mock_project.id)

        assert workflow_state.currentStage == "discovery"
        assert workflow_state.completedStages == []
        assert workflow_state.gateStatus == GateStatus.NOT_REQUIRED
        assert workflow_state.stageData["template"] == "bmad_method"
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_initialize_workflow_project_not_found(self, workflow_service, mock_db):
        """Test workflow initialization fails for non-existent project."""
        # Setup mock to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Should raise ValueError
        with pytest.raises(ValueError, match="not found"):
            await workflow_service.initialize_workflow(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_workflow_state(self, workflow_service, mock_db, mock_project):
        """Test getting workflow state from project."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        # Get workflow state
        workflow_state = await workflow_service.get_workflow_state(mock_project.id)

        assert workflow_state is not None
        assert workflow_state.currentStage == "discovery"
        assert workflow_state.completedStages == []

    @pytest.mark.asyncio
    async def test_get_available_transitions(self, workflow_service, mock_db, mock_project):
        """Test getting available next stages."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        # Get available transitions
        transitions = await workflow_service.get_available_transitions(mock_project.id)

        assert "market_research" in transitions
        assert len(transitions) >= 1

    @pytest.mark.asyncio
    async def test_advance_stage_valid_transition(self, workflow_service, mock_db, mock_project):
        """Test advancing to next stage with valid transition."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        user_id = uuid.uuid4()

        # Advance stage
        workflow_state = await workflow_service.advance_stage(
            project_id=mock_project.id,
            to_stage="market_research",
            user_id=user_id,
            notes="Moving to market research"
        )

        assert workflow_state.currentStage == "market_research"
        assert "discovery" in workflow_state.completedStages
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_advance_stage_invalid_transition(self, workflow_service, mock_db, mock_project):
        """Test advancing to invalid stage fails."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        user_id = uuid.uuid4()

        # Should raise ValueError for invalid transition
        with pytest.raises(ValueError, match="Cannot transition"):
            await workflow_service.advance_stage(
                project_id=mock_project.id,
                to_stage="development",  # Skip stages
                user_id=user_id
            )

    @pytest.mark.asyncio
    async def test_advance_stage_gate_not_approved(self, workflow_service, mock_db):
        """Test advancing from stage with unapproved gate fails."""
        # Setup mock project at prd_creation stage with pending gate
        project = MagicMock(spec=Project)
        project.id = uuid.uuid4()
        project.workflow_state = {
            "currentStage": "prd_creation",
            "completedStages": ["discovery", "market_research"],
            "stageData": {"template": "bmad_method"},
            "lastTransition": datetime.utcnow().isoformat(),
            "gateStatus": "pending"
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = project
        mock_db.execute.return_value = mock_result

        user_id = uuid.uuid4()

        # Should raise ValueError for gate not approved
        with pytest.raises(ValueError, match="gate approval required"):
            await workflow_service.advance_stage(
                project_id=project.id,
                to_stage="architecture",
                user_id=user_id
            )

    @pytest.mark.asyncio
    async def test_approve_gate(self, workflow_service, mock_db):
        """Test approving gate for current stage."""
        # Setup mock project at prd_creation stage
        project = MagicMock(spec=Project)
        project.id = uuid.uuid4()
        project.workflow_state = {
            "currentStage": "prd_creation",
            "completedStages": ["discovery", "market_research"],
            "stageData": {"template": "bmad_method"},
            "lastTransition": datetime.utcnow().isoformat(),
            "gateStatus": "pending"
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = project
        mock_db.execute.return_value = mock_result

        approver_id = uuid.uuid4()

        # Approve gate
        workflow_state = await workflow_service.approve_gate(
            project_id=project.id,
            approver_id=approver_id,
            feedback="PRD looks good"
        )

        assert workflow_state.gateStatus == GateStatus.APPROVED
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_reject_gate(self, workflow_service, mock_db):
        """Test rejecting gate for current stage."""
        # Setup mock project at architecture stage
        project = MagicMock(spec=Project)
        project.id = uuid.uuid4()
        project.workflow_state = {
            "currentStage": "architecture",
            "completedStages": ["discovery", "market_research", "prd_creation"],
            "stageData": {"template": "bmad_method"},
            "lastTransition": datetime.utcnow().isoformat(),
            "gateStatus": "pending"
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = project
        mock_db.execute.return_value = mock_result

        approver_id = uuid.uuid4()

        # Reject gate
        workflow_state = await workflow_service.reject_gate(
            project_id=project.id,
            approver_id=approver_id,
            feedback="Needs more detail"
        )

        assert workflow_state.gateStatus == GateStatus.REJECTED
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_approve_gate_not_required(self, workflow_service, mock_db, mock_project):
        """Test approving gate for stage that doesn't require gate fails."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_project
        mock_db.execute.return_value = mock_result

        approver_id = uuid.uuid4()

        # Should raise ValueError for no gate required
        with pytest.raises(ValueError, match="does not require gate"):
            await workflow_service.approve_gate(
                project_id=mock_project.id,
                approver_id=approver_id
            )
