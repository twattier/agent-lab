"""
Unit tests for workflow validators.
"""
import pytest
from core.workflow_templates import load_workflow_template
from models.schemas import GateStatus
from services.workflow_validators import (
    validate_stage_transition,
    validate_gate_requirement
)


class TestWorkflowValidators:
    """Test workflow validation logic."""

    def test_validate_valid_transition(self):
        """Test validation of valid stage transition."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="discovery",
            target_stage="market_research",
            gate_status=GateStatus.NOT_REQUIRED,
            template=template
        )

        assert is_valid is True
        assert error_msg == ""

    def test_validate_invalid_current_stage(self):
        """Test validation with invalid current stage."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="nonexistent",
            target_stage="market_research",
            gate_status=GateStatus.NOT_REQUIRED,
            template=template
        )

        assert is_valid is False
        assert "invalid current stage" in error_msg.lower()

    def test_validate_invalid_target_stage(self):
        """Test validation with invalid target stage."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="discovery",
            target_stage="nonexistent",
            gate_status=GateStatus.NOT_REQUIRED,
            template=template
        )

        assert is_valid is False
        assert "invalid target stage" in error_msg.lower()

    def test_validate_transition_not_in_next_stages(self):
        """Test validation when target not in next_stages."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="discovery",
            target_stage="development",  # Skip stages
            gate_status=GateStatus.NOT_REQUIRED,
            template=template
        )

        assert is_valid is False
        assert "cannot transition" in error_msg.lower()

    def test_validate_transition_gate_not_approved(self):
        """Test validation when gate required but not approved."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="prd_creation",  # Requires gate
            target_stage="architecture",
            gate_status=GateStatus.PENDING,
            template=template
        )

        assert is_valid is False
        assert "gate approval required" in error_msg.lower()

    def test_validate_transition_gate_approved(self):
        """Test validation when gate required and approved."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="prd_creation",
            target_stage="architecture",
            gate_status=GateStatus.APPROVED,
            template=template
        )

        assert is_valid is True
        assert error_msg == ""

    def test_validate_transition_gate_rejected(self):
        """Test validation when gate rejected."""
        template = load_workflow_template("bmad_method")

        is_valid, error_msg = validate_stage_transition(
            current_stage="architecture",  # Requires gate
            target_stage="development",
            gate_status=GateStatus.REJECTED,
            template=template
        )

        assert is_valid is False
        assert "gate approval required" in error_msg.lower()

    def test_validate_gate_requirement_required(self):
        """Test gate requirement validation for stage requiring gate."""
        template = load_workflow_template("bmad_method")

        gate_required, error_msg = validate_gate_requirement(
            current_stage="prd_creation",
            template=template
        )

        assert gate_required is True
        assert error_msg == ""

    def test_validate_gate_requirement_not_required(self):
        """Test gate requirement validation for stage not requiring gate."""
        template = load_workflow_template("bmad_method")

        gate_required, error_msg = validate_gate_requirement(
            current_stage="discovery",
            template=template
        )

        assert gate_required is False
        assert "does not require gate" in error_msg.lower()

    def test_validate_gate_requirement_invalid_stage(self):
        """Test gate requirement validation with invalid stage."""
        template = load_workflow_template("bmad_method")

        gate_required, error_msg = validate_gate_requirement(
            current_stage="nonexistent",
            template=template
        )

        assert gate_required is False
        assert "invalid stage" in error_msg.lower()
