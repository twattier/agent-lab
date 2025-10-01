"""
Unit tests for workflow template configuration.
"""
import pytest
from core.workflow_templates import (
    load_workflow_template,
    validate_template,
    detect_cycles,
    get_stage,
    WorkflowTemplate,
    WorkflowStage
)


class TestWorkflowTemplates:
    """Test workflow template loading and validation."""

    def test_load_bmad_template(self):
        """Test loading default BMAD Method template."""
        template = load_workflow_template("bmad_method")

        assert template.template_id == "bmad_method"
        assert template.template_name == "BMAD Method Workflow"
        assert len(template.stages) == 8

        # Verify all expected stages exist
        expected_stages = [
            "discovery",
            "market_research",
            "prd_creation",
            "architecture",
            "development",
            "qa_review",
            "deployment",
            "production_monitoring"
        ]
        for stage_id in expected_stages:
            assert stage_id in template.stages

    def test_template_stage_progression(self):
        """Test BMAD template stage progression."""
        template = load_workflow_template("bmad_method")

        # Verify progression chain
        assert "market_research" in template.stages["discovery"].next_stages
        assert "prd_creation" in template.stages["market_research"].next_stages
        assert "architecture" in template.stages["prd_creation"].next_stages
        assert "development" in template.stages["architecture"].next_stages
        assert "qa_review" in template.stages["development"].next_stages
        assert "deployment" in template.stages["qa_review"].next_stages
        assert "production_monitoring" in template.stages["deployment"].next_stages

        # Production monitoring is final stage
        assert template.stages["production_monitoring"].next_stages == []

    def test_template_gate_requirements(self):
        """Test gate requirements per stage."""
        template = load_workflow_template("bmad_method")

        # Stages requiring gates
        assert template.stages["prd_creation"].gate_required is True
        assert template.stages["architecture"].gate_required is True
        assert template.stages["development"].gate_required is True
        assert template.stages["qa_review"].gate_required is True

        # Stages not requiring gates
        assert template.stages["discovery"].gate_required is False
        assert template.stages["market_research"].gate_required is False
        assert template.stages["deployment"].gate_required is False
        assert template.stages["production_monitoring"].gate_required is False

    def test_load_unknown_template(self):
        """Test loading unknown template raises error."""
        with pytest.raises(ValueError, match="Unknown workflow template"):
            load_workflow_template("unknown_template")

    def test_get_stage(self):
        """Test getting specific stage from template."""
        template = load_workflow_template("bmad_method")

        stage = get_stage(template, "development")
        assert stage is not None
        assert stage.stage_id == "development"
        assert stage.stage_name == "Development"
        assert stage.gate_required is True

        # Non-existent stage
        stage = get_stage(template, "nonexistent")
        assert stage is None

    def test_validate_valid_template(self):
        """Test validation of valid template."""
        template = load_workflow_template("bmad_method")
        is_valid, error_msg = validate_template(template)

        assert is_valid is True
        assert error_msg is None

    def test_validate_empty_template(self):
        """Test validation of empty template."""
        template = WorkflowTemplate(
            template_id="empty",
            template_name="Empty Template",
            stages={}
        )

        is_valid, error_msg = validate_template(template)
        assert is_valid is False
        assert "at least one stage" in error_msg

    def test_validate_invalid_next_stage(self):
        """Test validation with invalid next_stages reference."""
        template = WorkflowTemplate(
            template_id="invalid",
            template_name="Invalid Template",
            stages={
                "stage1": WorkflowStage("stage1", "Stage 1", False, ["nonexistent"]),
            }
        )

        is_valid, error_msg = validate_template(template)
        assert is_valid is False
        assert "invalid next stage" in error_msg.lower()

    def test_detect_cycles_no_cycle(self):
        """Test cycle detection with valid template."""
        template = load_workflow_template("bmad_method")
        has_cycle = detect_cycles(template)

        assert has_cycle is False

    def test_detect_cycles_with_cycle(self):
        """Test cycle detection with circular dependency."""
        template = WorkflowTemplate(
            template_id="circular",
            template_name="Circular Template",
            stages={
                "stage1": WorkflowStage("stage1", "Stage 1", False, ["stage2"]),
                "stage2": WorkflowStage("stage2", "Stage 2", False, ["stage3"]),
                "stage3": WorkflowStage("stage3", "Stage 3", False, ["stage1"]),  # Circular
            }
        )

        has_cycle = detect_cycles(template)
        assert has_cycle is True

    def test_template_caching(self):
        """Test that template loading is cached."""
        template1 = load_workflow_template("bmad_method")
        template2 = load_workflow_template("bmad_method")

        # Should return same object due to lru_cache
        assert template1 is template2
