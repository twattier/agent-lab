"""Unit tests for BMAdTemplateService."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import yaml

from services.bmad_template_service import BMAdTemplateService, WorkflowTemplate


@pytest.fixture
def service():
    """Fixture for BMAdTemplateService."""
    return BMAdTemplateService()


@pytest.fixture
def valid_template():
    """Fixture for valid BMAD template."""
    return {
        "template_name": "BMAD Standard Workflow",
        "version": "1.0",
        "stages": [
            {"id": "discovery", "name": "Discovery", "sequence_number": 1},
            {"id": "business_analysis", "name": "Business Analysis", "sequence_number": 2},
            {"id": "market_research", "name": "Market Research", "sequence_number": 3},
            {"id": "solution_design", "name": "Solution Design", "sequence_number": 4},
            {"id": "proof_of_concept", "name": "Proof of Concept", "sequence_number": 5},
            {"id": "value_estimation", "name": "Value Estimation", "sequence_number": 6},
            {"id": "implementation_planning", "name": "Implementation Planning", "sequence_number": 7},
            {"id": "production_monitoring", "name": "Production Monitoring", "sequence_number": 8},
        ],
        "gates": [
            {
                "id": "gate_discovery",
                "name": "Discovery Gate",
                "stage_id": "discovery",
                "criteria": {"required_documents": ["requirements.md"]},
            }
        ],
    }


@pytest.fixture
def temp_template_file(tmp_path, valid_template):
    """Fixture to create temporary template YAML file."""
    template_file = tmp_path / "test_template.yml"
    with open(template_file, "w") as f:
        yaml.dump(valid_template, f)
    return template_file


class TestParseTemplate:
    """Tests for parse_template method."""

    def test_parse_valid_yaml(self, service, temp_template_file, valid_template):
        """Test parsing valid YAML template."""
        result = service.parse_template(temp_template_file)
        assert result["template_name"] == valid_template["template_name"]
        assert len(result["stages"]) == 8

    def test_parse_valid_json(self, service, tmp_path, valid_template):
        """Test parsing valid JSON template."""
        template_file = tmp_path / "test_template.json"
        with open(template_file, "w") as f:
            json.dump(valid_template, f)

        result = service.parse_template(template_file)
        assert result["template_name"] == valid_template["template_name"]

    def test_parse_missing_file(self, service):
        """Test parsing non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            service.parse_template(Path("/nonexistent/template.yml"))

    def test_parse_malformed_yaml(self, service, tmp_path):
        """Test parsing malformed YAML raises YAMLError."""
        template_file = tmp_path / "malformed.yml"
        with open(template_file, "w") as f:
            # Use truly malformed YAML
            f.write("invalid:\n  - item1\n   - item2\n  bad indentation")

        with pytest.raises(yaml.YAMLError):
            service.parse_template(template_file)

    def test_parse_unsupported_format(self, service, tmp_path):
        """Test parsing unsupported format raises ValueError."""
        template_file = tmp_path / "template.txt"
        template_file.write_text("some text")

        with pytest.raises(ValueError, match="Unsupported file format"):
            service.parse_template(template_file)


class TestValidateTemplateStructure:
    """Tests for validate_template_structure method."""

    def test_validate_valid_template(self, service, valid_template):
        """Test validation of valid template structure."""
        is_valid, errors = service.validate_template_structure(valid_template)
        assert is_valid
        assert len(errors) == 0

    def test_validate_missing_required_fields(self, service):
        """Test validation fails with missing required fields."""
        template = {"template_name": "Test"}  # Missing version, stages, gates

        is_valid, errors = service.validate_template_structure(template)
        assert not is_valid
        assert any("version" in err for err in errors)
        assert any("stages" in err for err in errors)
        assert any("gates" in err for err in errors)

    def test_validate_invalid_stages(self, service):
        """Test validation fails with invalid stages structure."""
        template = {
            "template_name": "Test",
            "version": "1.0",
            "stages": [
                {"name": "Stage 1"}  # Missing id and sequence_number
            ],
            "gates": [],
        }

        is_valid, errors = service.validate_template_structure(template)
        assert not is_valid
        assert any("Stage 0" in err for err in errors)

    def test_validate_invalid_gate_reference(self, service):
        """Test validation fails when gate references non-existent stage."""
        template = {
            "template_name": "Test",
            "version": "1.0",
            "stages": [{"id": "stage1", "name": "Stage 1", "sequence_number": 1}],
            "gates": [
                {
                    "id": "gate1",
                    "name": "Gate 1",
                    "stage_id": "nonexistent",  # Invalid reference
                    "criteria": {},
                }
            ],
        }

        is_valid, errors = service.validate_template_structure(template)
        assert not is_valid
        assert any("nonexistent" in err for err in errors)


class TestValidateBMADStandards:
    """Tests for validate_bmad_standards method."""

    def test_validate_standard_template(self, service, valid_template):
        """Test validation of standard BMAD template."""
        is_valid, errors = service.validate_bmad_standards(valid_template, strict=True)
        assert is_valid
        assert len(errors) == 0

    def test_validate_missing_stages(self, service):
        """Test validation fails with missing required BMAD stages."""
        template = {
            "template_name": "Test",
            "version": "1.0",
            "stages": [
                {"id": "discovery", "name": "Discovery", "sequence_number": 1},
            ],
            "gates": [],
        }

        is_valid, errors = service.validate_bmad_standards(template, strict=True)
        assert not is_valid
        assert any("Missing required BMAD stages" in err for err in errors)

    def test_validate_skip_with_strict_false(self, service):
        """Test validation skipped when strict=False."""
        template = {"stages": []}  # Invalid template

        is_valid, errors = service.validate_bmad_standards(template, strict=False)
        assert is_valid  # Passes because strict=False

    def test_validate_invalid_sequence_numbers(self, service, valid_template):
        """Test validation fails with invalid sequence numbers."""
        # Modify sequence numbers to be invalid
        valid_template["stages"][0]["sequence_number"] = 10

        is_valid, errors = service.validate_bmad_standards(valid_template, strict=True)
        assert not is_valid


class TestSaveTemplate:
    """Tests for save_template method."""

    def test_save_template_creates_model(self, service, valid_template):
        """Test saving template creates WorkflowTemplate model."""
        result = service.save_template(valid_template)

        assert isinstance(result, WorkflowTemplate)
        assert result.template_name == valid_template["template_name"]
        assert result.version == valid_template["version"]
        assert len(result.stages) == 8
        assert len(result.gates) == 1

    def test_save_template_generates_uuids(self, service, valid_template):
        """Test saving template generates UUIDs for all entities."""
        result = service.save_template(valid_template)

        assert result.id is not None
        assert all(stage.id is not None for stage in result.stages)
        assert all(gate.id is not None for gate in result.gates)


class TestImportTemplate:
    """Tests for import_template method."""

    def test_import_valid_template(self, service, temp_template_file):
        """Test importing valid template succeeds."""
        workflow_template, errors = service.import_template(temp_template_file)

        assert workflow_template is not None
        assert len(errors) == 0
        assert workflow_template.template_name == "BMAD Standard Workflow"

    def test_import_invalid_template(self, service, tmp_path):
        """Test importing invalid template returns errors."""
        # Create invalid template (missing required fields)
        invalid_template = {"template_name": "Invalid"}
        template_file = tmp_path / "invalid.yml"
        with open(template_file, "w") as f:
            yaml.dump(invalid_template, f)

        workflow_template, errors = service.import_template(template_file)

        assert workflow_template is None
        assert len(errors) > 0

    def test_import_nonexistent_file(self, service):
        """Test importing non-existent file returns errors."""
        workflow_template, errors = service.import_template(Path("/nonexistent.yml"))

        assert workflow_template is None
        assert len(errors) > 0
        assert any("not found" in err.lower() for err in errors)
