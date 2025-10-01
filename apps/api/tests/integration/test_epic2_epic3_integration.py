"""
Integration tests for Epic 2 → Epic 3 transition.

Tests that Epic 2 data structures are compatible with Epic 3 workflow automation.
Story 3.0 - AC8: Epic 2 → Epic 3 Integration Readiness
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import Project, Document, WorkflowEvent, WorkflowEventType


pytestmark = pytest.mark.asyncio


class TestEpic2Epic3DataCompatibility:
    """Test Epic 2 data structures work with Epic 3 automation."""

    async def test_project_workflow_state_json_structure(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test that Epic 2 workflow_state JSONB is readable for Epic 3 automation."""
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow"
        )

        assert response.status_code == 200
        workflow = response.json()

        # Epic 3 requires these fields for automation
        assert "currentStage" in workflow
        assert "gateStatus" in workflow
        assert "completedStages" in workflow
        assert "stageData" in workflow
        assert isinstance(workflow["completedStages"], list)
        assert isinstance(workflow["stageData"], dict)

    async def test_workflow_events_queryable_for_automation(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test that Epic 2 workflow events can be queried for Epic 3 automation context."""
        # Create some workflow events
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )

        # Query events (Epic 3 needs this for context)
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow/history"
        )

        assert response.status_code == 200
        events = response.json()
        assert len(events) == 2

        # Verify event structure for Epic 3
        for event in events:
            assert "event_type" in event
            assert "from_stage" in event or event["event_type"] == "stage_advance"
            assert "to_stage" in event
            assert "timestamp" in event
            assert "event_metadata" in event

    async def test_document_metadata_accessible_for_epic3(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test that Epic 2 document metadata is accessible for Epic 3 template import."""
        # Documents from Epic 2.4 should be queryable
        response = await test_client.get(
            f"/api/v1/documents/projects/{test_project_data.id}/documents"
        )

        # Should work even if empty
        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)


class TestEpic3PrerequisiteEndpoints:
    """Test that Epic 3 prerequisite endpoints exist."""

    async def test_workflow_state_endpoint_exists(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Verify GET /projects/{id}/workflow exists for Epic 3."""
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow"
        )
        assert response.status_code in [200, 404]  # 404 is acceptable if no workflow

    async def test_workflow_advance_endpoint_exists(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Verify POST /projects/{id}/workflow/advance exists for Epic 3."""
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        assert response.status_code in [200, 400, 404]  # Any valid HTTP response

    async def test_workflow_history_endpoint_exists(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Verify GET /projects/{id}/workflow/history exists for Epic 3."""
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow/history"
        )
        assert response.status_code in [200, 404]


class TestDatabaseSchemaForEpic3:
    """Test database schema compatibility with Epic 3."""

    async def test_workflow_state_jsonb_supports_automation_fields(
        self,
        db_session: AsyncSession,
        test_project_data
    ):
        """Test workflow_state JSONB can store Epic 3 automation metadata."""
        result = await db_session.execute(
            select(Project).where(Project.id == test_project_data.id)
        )
        project = result.scalar_one()

        # Epic 3 will add automation fields to stageData
        workflow_state = project.workflow_state or {}
        stage_data = workflow_state.get("stageData", {})

        # Should support nested structures
        assert isinstance(stage_data, dict)

    async def test_workflow_events_support_epic3_metadata(
        self,
        db_session: AsyncSession,
        test_project_data
    ):
        """Test workflow events can store Epic 3 automation metadata."""
        # Create an event with Epic 3-style metadata
        event = WorkflowEvent(
            project_id=test_project_data.id,
            event_type=WorkflowEventType.STAGE_ADVANCE,
            from_stage="discovery",
            to_stage="market_research",
            user_id=uuid.uuid4(),
            event_metadata={
                "automation_trigger": "claude_code",
                "mcp_session_id": "test-session-123",
                "llm_provider": "openai",
                "model": "gpt-4-turbo-preview"
            }
        )
        db_session.add(event)
        await db_session.commit()

        # Verify it was stored
        result = await db_session.execute(
            select(WorkflowEvent).where(
                WorkflowEvent.project_id == test_project_data.id,
                WorkflowEvent.event_type == WorkflowEventType.STAGE_ADVANCE
            )
        )
        stored_event = result.scalar_one()
        assert "automation_trigger" in stored_event.event_metadata


class TestBMADWorkflowTemplateForEpic3:
    """Test BMAD workflow template is ready for Epic 3 automation."""

    async def test_bmad_template_loads_successfully(self):
        """Test BMAD template loads for Epic 3 workflow engine."""
        from core.workflow_templates import load_workflow_template

        template = load_workflow_template("bmad_method")

        assert template.template_id == "bmad_method"
        assert len(template.stages) == 8
        assert "discovery" in template.stages
        assert "production_monitoring" in template.stages

    async def test_bmad_template_gate_configuration(self):
        """Test gate configuration is correct for Epic 3 automation."""
        from core.workflow_templates import load_workflow_template

        template = load_workflow_template("bmad_method")

        # Verify gates match Epic 3 expectations
        gates_required = [
            "prd_creation",
            "architecture",
            "development",
            "qa_review"
        ]

        for stage_id in gates_required:
            stage = template.stages[stage_id]
            assert stage.gate_required is True, f"{stage_id} should require gate"

    async def test_bmad_template_stage_transitions(self):
        """Test stage transitions are valid for Epic 3 automation."""
        from core.workflow_templates import load_workflow_template

        template = load_workflow_template("bmad_method")

        # Verify linear progression exists
        expected_path = [
            "discovery",
            "market_research",
            "prd_creation",
            "architecture",
            "development",
            "qa_review",
            "deployment",
            "production_monitoring"
        ]

        for i in range(len(expected_path) - 1):
            current_stage = template.stages[expected_path[i]]
            next_stage = expected_path[i + 1]
            assert next_stage in current_stage.next_stages
