"""
Workflow validation utilities for stage transitions and gate requirements.
"""
from typing import Tuple

from core.workflow_templates import WorkflowTemplate, get_stage
from models.schemas import GateStatus


def validate_stage_transition(
    current_stage: str,
    target_stage: str,
    gate_status: GateStatus,
    template: WorkflowTemplate
) -> Tuple[bool, str]:
    """
    Validate if a stage transition is allowed based on template rules.

    Args:
        current_stage: Current workflow stage ID
        target_stage: Target workflow stage ID
        gate_status: Current gate status
        template: Workflow template to validate against

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Get current stage from template
    stage = get_stage(template, current_stage)
    if not stage:
        return False, f"Invalid current stage: {current_stage}"

    # Check if target stage exists in template
    if target_stage not in template.stages:
        return False, f"Invalid target stage: {target_stage}"

    # Check if target is in allowed next stages
    if target_stage not in stage.next_stages:
        return False, f"Cannot transition from {current_stage} to {target_stage}. Allowed next stages: {', '.join(stage.next_stages)}"

    # Check gate requirement if current stage requires a gate
    if stage.gate_required and gate_status != GateStatus.APPROVED:
        return False, f"Cannot advance from {current_stage}: gate approval required (current status: {gate_status.value})"

    return True, ""


def validate_gate_requirement(
    current_stage: str,
    template: WorkflowTemplate
) -> Tuple[bool, str]:
    """
    Validate if the current stage requires gate approval.

    Args:
        current_stage: Current workflow stage ID
        template: Workflow template to validate against

    Returns:
        Tuple of (gate_required: bool, error_message: str)
    """
    stage = get_stage(template, current_stage)
    if not stage:
        return False, f"Invalid stage: {current_stage}"

    if not stage.gate_required:
        return False, f"Stage {current_stage} does not require gate approval"

    return True, ""
