"""BMAD Template Service for importing and managing workflow templates."""

import json
from pathlib import Path
from typing import Tuple
import uuid

import yaml
from pydantic import BaseModel, Field


class WorkflowGate(BaseModel):
    """Workflow gate model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    gate_id: str
    name: str
    stage_id: str
    criteria: dict


class WorkflowStage(BaseModel):
    """Workflow stage model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    stage_id: str
    name: str
    sequence_number: int


class WorkflowTemplate(BaseModel):
    """Workflow template model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    template_name: str
    version: str
    configuration: dict
    stages: list[WorkflowStage] = []
    gates: list[WorkflowGate] = []


class BMAdTemplateService:
    """Service for managing BMAD workflow templates."""

    # Required BMAD Method stages in order
    REQUIRED_BMAD_STAGES = [
        "discovery",
        "business_analysis",
        "market_research",
        "solution_design",
        "proof_of_concept",
        "value_estimation",
        "implementation_planning",
        "production_monitoring",
    ]

    def parse_template(self, file_path: Path) -> dict:
        """Parse YAML or JSON template file.

        Args:
            file_path: Path to template file (.yml, .yaml, or .json)

        Returns:
            Parsed template as dictionary

        Raises:
            FileNotFoundError: If file does not exist
            yaml.YAMLError: If YAML parsing fails
            json.JSONDecodeError: If JSON parsing fails
            ValueError: If file extension not supported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")

        file_ext = file_path.suffix.lower()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_ext in [".yml", ".yaml"]:
                    return yaml.safe_load(f)
                elif file_ext == ".json":
                    return json.load(f)
                else:
                    raise ValueError(
                        f"Unsupported file format: {file_ext}. Use .yml, .yaml, or .json"
                    )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML template: {str(e)}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse JSON template: {str(e)}", e.doc, e.pos
            )

    def validate_template_structure(self, template: dict) -> Tuple[bool, list[str]]:
        """Validate template has required structure.

        Args:
            template: Parsed template dictionary

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Validate required top-level fields
        required_fields = ["template_name", "version", "stages", "gates"]
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")

        # Validate stages is a list
        if "stages" in template:
            if not isinstance(template["stages"], list):
                errors.append("'stages' must be a list")
            else:
                # Validate each stage structure
                for idx, stage in enumerate(template["stages"]):
                    if not isinstance(stage, dict):
                        errors.append(f"Stage {idx} must be a dictionary")
                        continue

                    stage_required = ["id", "name", "sequence_number"]
                    for field in stage_required:
                        if field not in stage:
                            errors.append(f"Stage {idx}: missing required field '{field}'")

        # Validate gates is a list
        if "gates" in template:
            if not isinstance(template["gates"], list):
                errors.append("'gates' must be a list")
            else:
                # Validate each gate structure
                stage_ids = {s.get("id") for s in template.get("stages", [])}
                for idx, gate in enumerate(template["gates"]):
                    if not isinstance(gate, dict):
                        errors.append(f"Gate {idx} must be a dictionary")
                        continue

                    gate_required = ["id", "name", "stage_id", "criteria"]
                    for field in gate_required:
                        if field not in gate:
                            errors.append(f"Gate {idx}: missing required field '{field}'")

                    # Validate gate references existing stage
                    if "stage_id" in gate and gate["stage_id"] not in stage_ids:
                        errors.append(
                            f"Gate {idx}: references non-existent stage_id '{gate['stage_id']}'"
                        )

                    # Validate criteria is a dict/object
                    if "criteria" in gate and not isinstance(gate["criteria"], dict):
                        errors.append(f"Gate {idx}: 'criteria' must be an object/dict")

        return (len(errors) == 0, errors)

    def validate_bmad_standards(
        self, template: dict, strict: bool = True
    ) -> Tuple[bool, list[str]]:
        """Validate template conforms to BMAD Method standards.

        Args:
            template: Parsed template dictionary
            strict: If True, enforce strict BMAD compliance

        Returns:
            Tuple of (is_valid, list of error/warning messages)
        """
        errors = []

        if not strict:
            return (True, ["Skipping BMAD standards validation (strict=False)"])

        stages = template.get("stages", [])
        stage_ids = [s.get("id") for s in stages]

        # Validate 8 required stages present
        missing_stages = [
            stage for stage in self.REQUIRED_BMAD_STAGES if stage not in stage_ids
        ]
        if missing_stages:
            errors.append(
                f"Missing required BMAD stages: {', '.join(missing_stages)}"
            )

        # Validate stage sequence numbers are 1-8
        sequence_numbers = sorted([s.get("sequence_number", 0) for s in stages])
        if sequence_numbers != list(range(1, 9)):
            errors.append(
                f"Stage sequence numbers must be 1-8 consecutively, got: {sequence_numbers}"
            )

        # Validate stages are in correct order
        for idx, stage in enumerate(stages):
            expected_id = self.REQUIRED_BMAD_STAGES[idx] if idx < 8 else None
            actual_id = stage.get("id")
            sequence_num = stage.get("sequence_number")

            if expected_id and actual_id != expected_id:
                errors.append(
                    f"Stage {sequence_num}: expected id '{expected_id}', got '{actual_id}'"
                )

        return (len(errors) == 0, errors)

    def save_template(self, template: dict) -> WorkflowTemplate:
        """Save template to database.

        Args:
            template: Validated template dictionary

        Returns:
            WorkflowTemplate model with generated UUIDs

        Note:
            This is a placeholder implementation. Actual database persistence
            will be implemented with SQLAlchemy async session.
        """
        # Create WorkflowTemplate model
        workflow_template = WorkflowTemplate(
            template_name=template["template_name"],
            version=template["version"],
            configuration=template,
        )

        # Create WorkflowStage models
        for stage_data in template.get("stages", []):
            stage = WorkflowStage(
                stage_id=stage_data["id"],
                name=stage_data["name"],
                sequence_number=stage_data["sequence_number"],
            )
            workflow_template.stages.append(stage)

        # Create WorkflowGate models
        for gate_data in template.get("gates", []):
            gate = WorkflowGate(
                gate_id=gate_data["id"],
                name=gate_data["name"],
                stage_id=gate_data["stage_id"],
                criteria=gate_data["criteria"],
            )
            workflow_template.gates.append(gate)

        # TODO: Persist to database using SQLAlchemy async session
        # async with session.begin():
        #     session.add(workflow_template)
        #     await session.commit()

        return workflow_template

    def import_template(
        self, file_path: Path, strict_validation: bool = True
    ) -> Tuple[WorkflowTemplate | None, list[str]]:
        """Import template from file with full validation.

        Args:
            file_path: Path to template file
            strict_validation: Enforce strict BMAD compliance

        Returns:
            Tuple of (WorkflowTemplate or None, list of errors)
        """
        all_errors = []

        try:
            # Step 1: Parse template
            template = self.parse_template(file_path)

            # Step 2: Validate structure
            is_valid, errors = self.validate_template_structure(template)
            if not is_valid:
                all_errors.extend(errors)
                return (None, all_errors)

            # Step 3: Validate BMAD standards
            is_valid, errors = self.validate_bmad_standards(template, strict_validation)
            if not is_valid:
                all_errors.extend(errors)
                return (None, all_errors)

            # Step 4: Save to database
            workflow_template = self.save_template(template)
            return (workflow_template, [])

        except (FileNotFoundError, yaml.YAMLError, json.JSONDecodeError, ValueError) as e:
            all_errors.append(str(e))
            return (None, all_errors)
