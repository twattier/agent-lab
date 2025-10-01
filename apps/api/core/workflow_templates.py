"""
Workflow template configuration for BMAD Method and other workflow templates.
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Set, Optional


@dataclass
class WorkflowStage:
    """Represents a single stage in a workflow template."""
    stage_id: str
    stage_name: str
    gate_required: bool
    next_stages: List[str]


@dataclass
class WorkflowTemplate:
    """Represents a complete workflow template with multiple stages."""
    template_id: str
    template_name: str
    stages: Dict[str, WorkflowStage]


def detect_cycles(template: WorkflowTemplate) -> bool:
    """
    Detect circular dependencies in workflow template.

    Args:
        template: WorkflowTemplate to validate

    Returns:
        True if circular dependencies detected, False otherwise
    """
    def has_cycle_dfs(stage_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
        """DFS-based cycle detection."""
        visited.add(stage_id)
        rec_stack.add(stage_id)

        stage = template.stages.get(stage_id)
        if stage:
            for next_stage in stage.next_stages:
                if next_stage not in visited:
                    if has_cycle_dfs(next_stage, visited, rec_stack):
                        return True
                elif next_stage in rec_stack:
                    return True

        rec_stack.remove(stage_id)
        return False

    visited: Set[str] = set()
    rec_stack: Set[str] = set()

    for stage_id in template.stages:
        if stage_id not in visited:
            if has_cycle_dfs(stage_id, visited, rec_stack):
                return True

    return False


def validate_template(template: WorkflowTemplate) -> tuple[bool, Optional[str]]:
    """
    Validate workflow template structure and rules.

    Args:
        template: WorkflowTemplate to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    # Check for duplicate stage IDs (should be unique by dict nature, but verify)
    if len(template.stages) == 0:
        return False, "Template must have at least one stage"

    # Validate next_stages references
    for stage_id, stage in template.stages.items():
        for next_stage in stage.next_stages:
            if next_stage not in template.stages:
                return False, f"Stage '{stage_id}' references invalid next stage '{next_stage}'"

    # Check for circular dependencies
    if detect_cycles(template):
        return False, "Template contains circular dependencies"

    return True, None


@lru_cache(maxsize=10)
def load_workflow_template(template_name: str = "bmad_method") -> WorkflowTemplate:
    """
    Load workflow template by name. Cached for performance.

    Args:
        template_name: Name of the template to load (default: "bmad_method")

    Returns:
        WorkflowTemplate instance

    Raises:
        ValueError: If template name is unknown
    """
    if template_name == "bmad_method":
        template = WorkflowTemplate(
            template_id="bmad_method",
            template_name="BMAD Method Workflow",
            stages={
                "discovery": WorkflowStage(
                    stage_id="discovery",
                    stage_name="Discovery",
                    gate_required=False,
                    next_stages=["market_research"]
                ),
                "market_research": WorkflowStage(
                    stage_id="market_research",
                    stage_name="Market Research",
                    gate_required=False,
                    next_stages=["prd_creation"]
                ),
                "prd_creation": WorkflowStage(
                    stage_id="prd_creation",
                    stage_name="PRD Creation",
                    gate_required=True,
                    next_stages=["architecture"]
                ),
                "architecture": WorkflowStage(
                    stage_id="architecture",
                    stage_name="Architecture Design",
                    gate_required=True,
                    next_stages=["development"]
                ),
                "development": WorkflowStage(
                    stage_id="development",
                    stage_name="Development",
                    gate_required=True,
                    next_stages=["qa_review"]
                ),
                "qa_review": WorkflowStage(
                    stage_id="qa_review",
                    stage_name="QA Review",
                    gate_required=True,
                    next_stages=["deployment"]
                ),
                "deployment": WorkflowStage(
                    stage_id="deployment",
                    stage_name="Deployment",
                    gate_required=False,
                    next_stages=["production_monitoring"]
                ),
                "production_monitoring": WorkflowStage(
                    stage_id="production_monitoring",
                    stage_name="Production Monitoring",
                    gate_required=False,
                    next_stages=[]
                )
            }
        )

        # Validate template on load
        is_valid, error_msg = validate_template(template)
        if not is_valid:
            raise ValueError(f"Invalid BMAD template: {error_msg}")

        return template

    raise ValueError(f"Unknown workflow template: {template_name}")


def get_stage(template: WorkflowTemplate, stage_id: str) -> Optional[WorkflowStage]:
    """
    Get a specific stage from a workflow template.

    Args:
        template: WorkflowTemplate to query
        stage_id: ID of the stage to retrieve

    Returns:
        WorkflowStage if found, None otherwise
    """
    return template.stages.get(stage_id)
