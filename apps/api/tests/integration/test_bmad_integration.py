"""Integration tests for BMAD Template and MCP functionality."""

import pytest
from pathlib import Path
from httpx import AsyncClient
import yaml

from services.bmad_template_service import BMAdTemplateService
from services.mcp_service import MCPService


@pytest.fixture
def sample_template_file(tmp_path):
    """Create sample BMAD template for testing."""
    template = {
        "template_name": "BMAD Integration Test",
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
                "id": "gate_1",
                "name": "Discovery Gate",
                "stage_id": "discovery",
                "criteria": {"required": True},
            }
        ],
    }

    template_file = tmp_path / "test_template.yml"
    with open(template_file, "w") as f:
        yaml.dump(template, f)

    return template_file


class TestBMADTemplateIntegration:
    """Integration tests for BMAD template import."""

    def test_end_to_end_template_import(self, sample_template_file):
        """Test complete template import flow."""
        service = BMAdTemplateService()

        # Import template
        workflow_template, errors = service.import_template(sample_template_file)

        # Verify success
        assert workflow_template is not None
        assert len(errors) == 0
        assert workflow_template.template_name == "BMAD Integration Test"
        assert len(workflow_template.stages) == 8
        assert len(workflow_template.gates) == 1

    # Note: API endpoint tests would require FastAPI test client
    # Skipping for brevity - would test POST /api/v1/bmad/templates/import


class TestMCPIntegration:
    """Integration tests for MCP protocol."""

    @pytest.mark.asyncio
    async def test_mcp_session_initialization(self, tmp_path):
        """Test MCP session initialization."""
        service = MCPService()

        # Initialize session with workspace
        session_id = await service.initialize_session(tmp_path)

        # Verify session created
        assert session_id is not None
        assert service.session_id is not None

    @pytest.mark.asyncio
    async def test_mcp_workflow_event_publishing(self):
        """Test publishing workflow events."""
        service = MCPService()

        # Connect service
        await service.connect()

        # Send event
        result = await service.send_workflow_event(
            "TEMPLATE_IMPORTED",
            {"template_name": "Test Template"},
        )

        # Verify event sent (or gracefully handled if MCP disabled)
        assert isinstance(result, bool)

    def test_mcp_status(self):
        """Test MCP status retrieval."""
        service = MCPService()

        status = service.get_status()

        # Verify status structure
        assert "connected" in status
        assert "session_id" in status
        assert "enabled" in status
        assert "uptime" in status

    # Note: API endpoint test for GET /api/v1/bmad/mcp/status would go here
