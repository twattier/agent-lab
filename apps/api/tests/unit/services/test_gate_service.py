"""Unit tests for GateService (Story 3.2 AC14)."""
import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from services.gate_service import GateService
from models.database import WorkflowGate, GateReviewer, Contact, WorkflowEvent
from tests.mocks.workflow.progression_engine_mock import MockWorkflowProgressionEngine


@pytest.fixture
def mock_session():
    """Mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.begin_nested = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_progression_engine():
    """Mock progression engine."""
    return MockWorkflowProgressionEngine()


@pytest.fixture
def gate_service(mock_session, mock_progression_engine):
    """GateService instance with mocks."""
    return GateService(
        session=mock_session,
        progression_engine=mock_progression_engine
    )


class TestValidateGateDependencies:
    """Test validate_gate_dependencies method."""

    @pytest.mark.asyncio
    async def test_all_dependencies_met(self, gate_service, mock_session):
        """Test when all dependencies are met."""
        gate_id = uuid4()
        template_id = uuid4()

        # Mock gate with dependencies
        gate = WorkflowGate(
            id=gate_id,
            template_id=template_id,
            gate_id="gate_2",
            name="Gate 2",
            stage_id="stage_1",
            criteria={"required_gates": ["gate_1"]},
            status="pending"
        )

        # Mock required gate (approved)
        required_gate = WorkflowGate(
            id=uuid4(),
            template_id=template_id,
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={},
            status="approved"
        )

        # Setup mock returns
        mock_result_1 = MagicMock()
        mock_result_1.scalar_one_or_none.return_value = gate
        mock_result_2 = MagicMock()
        mock_result_2.scalar_one_or_none.return_value = required_gate

        mock_session.execute.side_effect = [mock_result_1, mock_result_2]

        # Execute
        can_approve, blocked = await gate_service.validate_gate_dependencies(gate_id)

        # Assert
        assert can_approve is True
        assert blocked == []

    @pytest.mark.asyncio
    async def test_some_dependencies_blocked(self, gate_service, mock_session):
        """Test when some dependencies are not met."""
        gate_id = uuid4()
        template_id = uuid4()

        # Mock gate with dependencies
        gate = WorkflowGate(
            id=gate_id,
            template_id=template_id,
            gate_id="gate_3",
            name="Gate 3",
            stage_id="stage_2",
            criteria={"required_gates": ["gate_1", "gate_2"]},
            status="pending"
        )

        # Mock required gates (one approved, one pending)
        required_gate_1 = WorkflowGate(
            id=uuid4(),
            template_id=template_id,
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={},
            status="approved"
        )

        required_gate_2 = WorkflowGate(
            id=uuid4(),
            template_id=template_id,
            gate_id="gate_2",
            name="Gate 2",
            stage_id="stage_1",
            criteria={},
            status="pending"  # Not approved
        )

        # Setup mock returns
        mock_result_1 = MagicMock()
        mock_result_1.scalar_one_or_none.return_value = gate
        mock_result_2 = MagicMock()
        mock_result_2.scalar_one_or_none.return_value = required_gate_1
        mock_result_3 = MagicMock()
        mock_result_3.scalar_one_or_none.return_value = required_gate_2

        mock_session.execute.side_effect = [mock_result_1, mock_result_2, mock_result_3]

        # Execute
        can_approve, blocked = await gate_service.validate_gate_dependencies(gate_id)

        # Assert
        assert can_approve is False
        assert "gate_2" in blocked

    @pytest.mark.asyncio
    async def test_no_dependencies(self, gate_service, mock_session):
        """Test gate with no dependencies."""
        gate_id = uuid4()

        # Mock gate without dependencies
        gate = WorkflowGate(
            id=gate_id,
            template_id=uuid4(),
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={},  # No required_gates
            status="pending"
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = gate
        mock_session.execute.return_value = mock_result

        # Execute
        can_approve, blocked = await gate_service.validate_gate_dependencies(gate_id)

        # Assert
        assert can_approve is True
        assert blocked == []


class TestCheckGateSequence:
    """Test check_gate_sequence method."""

    @pytest.mark.asyncio
    async def test_correct_sequence(self, gate_service, mock_session):
        """Test gate in correct sequence."""
        gate_id = uuid4()
        template_id = uuid4()

        # Mock current gate (sequence 2)
        gate = WorkflowGate(
            id=gate_id,
            template_id=template_id,
            gate_id="gate_2",
            name="Gate 2",
            stage_id="stage_1",
            criteria={"sequence_number": 2},
            status="pending"
        )

        # Mock previous gate (sequence 1, approved)
        previous_gate = WorkflowGate(
            id=uuid4(),
            template_id=template_id,
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={"sequence_number": 1},
            status="approved"
        )

        mock_result_1 = MagicMock()
        mock_result_1.scalar_one_or_none.return_value = gate
        mock_result_2 = MagicMock()
        mock_result_2.scalars.return_value.all.return_value = [previous_gate]

        mock_session.execute.side_effect = [mock_result_1, mock_result_2]

        # Execute
        is_valid, error = await gate_service.check_gate_sequence(gate_id)

        # Assert
        assert is_valid is True
        assert error == ''

    @pytest.mark.asyncio
    async def test_out_of_sequence_violation(self, gate_service, mock_session):
        """Test gate out of sequence."""
        gate_id = uuid4()
        template_id = uuid4()

        # Mock current gate (sequence 2)
        gate = WorkflowGate(
            id=gate_id,
            template_id=template_id,
            gate_id="gate_2",
            name="Gate 2",
            stage_id="stage_1",
            criteria={"sequence_number": 2},
            status="pending"
        )

        # Mock previous gate (sequence 1, NOT approved)
        previous_gate = WorkflowGate(
            id=uuid4(),
            template_id=template_id,
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={"sequence_number": 1},
            status="pending"  # Not approved
        )

        mock_result_1 = MagicMock()
        mock_result_1.scalar_one_or_none.return_value = gate
        mock_result_2 = MagicMock()
        mock_result_2.scalars.return_value.all.return_value = [previous_gate]

        mock_session.execute.side_effect = [mock_result_1, mock_result_2]

        # Execute
        is_valid, error = await gate_service.check_gate_sequence(gate_id)

        # Assert
        assert is_valid is False
        assert "Gate 1" in error


class TestApproveGate:
    """Test approve_gate method."""

    @pytest.mark.asyncio
    async def test_successful_approval(self, gate_service, mock_session, mock_progression_engine):
        """Test successful gate approval."""
        gate_id = uuid4()
        user_id = uuid4()
        comment = "Approved after review"

        # Mock gate
        gate = WorkflowGate(
            id=gate_id,
            template_id=uuid4(),
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={},
            status="pending"
        )

        # Mock execute returns
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = gate

        # First call validates dependencies, second gets gate
        mock_session.execute.side_effect = [
            mock_result,  # validate_gate_dependencies
            mock_result,  # check_gate_sequence - get gate
            MagicMock(),  # check_gate_sequence - get previous gates
            mock_result,  # approve_gate - get gate
        ]

        # Execute
        result = await gate_service.approve_gate(gate_id, user_id, comment)

        # Assert
        assert gate.status == 'approved'
        assert mock_progression_engine.advance_called
        assert mock_progression_engine.last_gate_id == gate_id
        assert mock_session.commit.called


class TestRejectGate:
    """Test reject_gate method."""

    @pytest.mark.asyncio
    async def test_successful_rejection(self, gate_service, mock_session):
        """Test successful gate rejection."""
        gate_id = uuid4()
        user_id = uuid4()
        reason = "Requirements not met - need more detail"

        # Mock gate
        gate = WorkflowGate(
            id=gate_id,
            template_id=uuid4(),
            gate_id="gate_1",
            name="Gate 1",
            stage_id="stage_1",
            criteria={},
            status="pending"
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = gate
        mock_session.execute.return_value = mock_result

        # Execute
        result = await gate_service.reject_gate(gate_id, user_id, reason)

        # Assert
        assert gate.status == 'rejected'
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_rejection_short_reason(self, gate_service, mock_session):
        """Test rejection with short reason fails."""
        gate_id = uuid4()
        user_id = uuid4()
        reason = "Too short"  # Less than 10 chars

        # Execute & Assert
        with pytest.raises(ValueError, match="at least 10 characters"):
            await gate_service.reject_gate(gate_id, user_id, reason)


class TestAssignReviewer:
    """Test assign_reviewer method."""

    @pytest.mark.asyncio
    async def test_successful_assignment(self, gate_service, mock_session):
        """Test successful reviewer assignment."""
        gate_id = uuid4()
        contact_id = uuid4()
        reviewer_role = "technical_reviewer"

        # Mock contact (active)
        contact = Contact(
            id=contact_id,
            name="John Doe",
            email="john@example.com",
            is_active=True
        )

        # Mock no existing assignment
        mock_contact_result = MagicMock()
        mock_contact_result.scalar_one_or_none.return_value = contact

        mock_existing_result = MagicMock()
        mock_existing_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [mock_contact_result, mock_existing_result]

        # Execute
        result = await gate_service.assign_reviewer(gate_id, contact_id, reviewer_role)

        # Assert
        assert mock_session.commit.called


class TestGetGateMetrics:
    """Test get_gate_metrics method."""

    @pytest.mark.asyncio
    async def test_get_metrics(self, gate_service, mock_session):
        """Test getting gate metrics."""
        project_id = uuid4()

        # Mock status counts
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [
            ('pending', 5),
            ('approved', 3),
            ('rejected', 1),
            ('blocked', 2)
        ]
        mock_session.execute.return_value = mock_result

        # Execute
        metrics = await gate_service.get_gate_metrics(project_id)

        # Assert
        assert metrics['total_gates'] == 11
        assert metrics['approved_count'] == 3
        assert metrics['rejected_count'] == 1
        assert metrics['pending_count'] == 5
        assert metrics['blocked_count'] == 2
