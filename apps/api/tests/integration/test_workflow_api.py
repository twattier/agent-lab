"""
Integration tests for workflow API endpoints.
Story 2.3 - BMAD Workflow State Management
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Project, Client, Service, WorkflowEvent
from repositories.project_repository import ProjectRepository
from repositories.client_repository import ClientRepository
from repositories.service_repository import ServiceRepository


pytestmark = pytest.mark.asyncio


# Helper fixtures
@pytest.fixture
async def test_client_data(db_session: AsyncSession):
    """Create test client."""
    client_repo = ClientRepository(db_session)
    client = await client_repo.create(
        name="Test Client",
        business_domain="technology"
    )
    return client


@pytest.fixture
async def test_service_data(db_session: AsyncSession, test_client_data):
    """Create test service."""
    service_repo = ServiceRepository(db_session)
    service = await service_repo.create(
        name="Test Service",
        description="Test service description",
        client_id=test_client_data.id
    )
    return service


@pytest.fixture
async def test_project_data(db_session: AsyncSession, test_service_data):
    """Create test project with initialized workflow."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create_project({
        "name": "Test Project",
        "description": "Test project description",
        "service_id": test_service_data.id,
        "project_type": "new",
        "status": "active"
    })
    return project


class TestWorkflowStateAPI:
    """Test GET /projects/{id}/workflow endpoint."""

    async def test_get_workflow_state_success(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test getting workflow state for existing project."""
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["currentStage"] == "discovery"
        assert data["completedStages"] == []
        assert data["gateStatus"] == "not_required"
        assert "availableTransitions" in data
        assert "market_research" in data["availableTransitions"]

    async def test_get_workflow_state_not_found(self, test_client: AsyncClient):
        """Test getting workflow state for non-existent project."""
        fake_id = uuid.uuid4()
        response = await test_client.get(
            f"/api/v1/projects/{fake_id}/workflow"
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestWorkflowAdvanceAPI:
    """Test POST /projects/{id}/workflow/advance endpoint."""

    async def test_advance_stage_valid_transition(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test advancing to next valid stage."""
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={
                "toStage": "market_research",
                "notes": "Moving to market research phase"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["currentStage"] == "market_research"
        assert "discovery" in data["completedStages"]
        assert "prd_creation" in data["availableTransitions"]

        # Verify WorkflowEvent was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(WorkflowEvent).where(
                WorkflowEvent.project_id == test_project_data.id
            )
        )
        events = result.scalars().all()
        assert len(events) == 1
        assert events[0].event_type.value == "stage_advance"
        assert events[0].from_stage == "discovery"
        assert events[0].to_stage == "market_research"

    async def test_advance_stage_invalid_transition(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test advancing to invalid stage (skip stages)."""
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={
                "toStage": "development"  # Skip multiple stages
            }
        )

        assert response.status_code == 400
        assert "cannot transition" in response.json()["detail"].lower()

    async def test_advance_stage_gate_not_approved(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test advancing from stage with unapproved gate fails."""
        # Advance to prd_creation stage (requires gate)
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )

        # Try to advance without gate approval
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "architecture"}
        )

        assert response.status_code == 400
        assert "gate approval required" in response.json()["detail"].lower()

    async def test_advance_stage_project_not_found(self, test_client: AsyncClient):
        """Test advancing stage for non-existent project."""
        fake_id = uuid.uuid4()
        response = await test_client.post(
            f"/api/v1/projects/{fake_id}/workflow/advance",
            json={"toStage": "market_research"}
        )

        assert response.status_code == 400


class TestGateApprovalAPI:
    """Test POST /projects/{id}/workflow/gate-approval endpoint."""

    async def test_approve_gate_success(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test approving gate for stage that requires it."""
        # Advance to prd_creation stage (requires gate)
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )

        # Approve gate
        approver_id = str(uuid.uuid4())
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={
                "action": "approve",
                "feedback": "PRD looks good",
                "approverId": approver_id
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["gateStatus"] == "approved"
        assert data["currentStage"] == "prd_creation"

        # Verify WorkflowEvent was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(WorkflowEvent).where(
                WorkflowEvent.project_id == test_project_data.id,
                WorkflowEvent.event_type == "gate_approved"
            )
        )
        events = result.scalars().all()
        assert len(events) == 1
        assert events[0].event_metadata.get("feedback") == "PRD looks good"

    async def test_reject_gate_success(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test rejecting gate for stage that requires it."""
        # Advance to architecture stage (requires gate)
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )
        # Approve PRD gate
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={
                "action": "approve",
                "approverId": str(uuid.uuid4())
            }
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "architecture"}
        )

        # Reject architecture gate
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={
                "action": "reject",
                "feedback": "Needs more detail on scalability",
                "approverId": str(uuid.uuid4())
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["gateStatus"] == "rejected"
        assert data["currentStage"] == "architecture"

    async def test_approve_gate_not_required(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test approving gate for stage that doesn't require it fails."""
        # discovery stage doesn't require gate
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={
                "action": "approve",
                "approverId": str(uuid.uuid4())
            }
        )

        assert response.status_code == 400
        assert "does not require gate" in response.json()["detail"].lower()

    async def test_gate_approval_enables_advancement(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test that gate approval enables stage advancement."""
        # Advance to prd_creation
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )

        # Approve gate
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={
                "action": "approve",
                "approverId": str(uuid.uuid4())
            }
        )

        # Now should be able to advance
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "architecture"}
        )

        assert response.status_code == 200
        assert response.json()["currentStage"] == "architecture"

    async def test_gate_rejection_blocks_advancement(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test that gate rejection blocks stage advancement."""
        # Advance to development
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={"action": "approve", "approverId": str(uuid.uuid4())}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "architecture"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={"action": "approve", "approverId": str(uuid.uuid4())}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "development"}
        )

        # Reject development gate
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={
                "action": "reject",
                "feedback": "Code quality issues",
                "approverId": str(uuid.uuid4())
            }
        )

        # Try to advance - should fail
        response = await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "qa_review"}
        )

        assert response.status_code == 400
        assert "gate approval required" in response.json()["detail"].lower()


class TestWorkflowHistoryAPI:
    """Test GET /projects/{id}/workflow/history endpoint."""

    async def test_get_workflow_history_success(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test getting workflow event history."""
        # Create some workflow events
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "prd_creation"}
        )
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
            json={"action": "approve", "approverId": str(uuid.uuid4())}
        )

        # Get history
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow/history"
        )

        assert response.status_code == 200
        events = response.json()

        assert len(events) == 3
        # Events should be ordered by timestamp DESC (most recent first)
        assert events[0]["event_type"] == "gate_approved"
        assert events[1]["event_type"] == "stage_advance"
        assert events[2]["event_type"] == "stage_advance"

    async def test_get_workflow_history_pagination(
        self,
        test_client: AsyncClient,
        test_project_data
    ):
        """Test workflow history pagination."""
        # Create multiple events
        for stage in ["market_research", "prd_creation"]:
            await test_client.post(
                f"/api/v1/projects/{test_project_data.id}/workflow/advance",
                json={"toStage": stage}
            )

        # Get first page with limit 1
        response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow/history?page=1&limit=1"
        )

        assert response.status_code == 200
        events = response.json()
        assert len(events) == 1

    async def test_get_workflow_history_project_not_found(
        self,
        test_client: AsyncClient
    ):
        """Test getting history for non-existent project."""
        fake_id = uuid.uuid4()
        response = await test_client.get(
            f"/api/v1/projects/{fake_id}/workflow/history"
        )

        assert response.status_code == 404


class TestCompleteWorkflowProgression:
    """Test complete workflow progression from discovery to production."""

    async def test_complete_workflow_lifecycle(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test progressing through entire BMAD workflow."""
        stages = [
            ("market_research", False),
            ("prd_creation", True),
            ("architecture", True),
            ("development", True),
            ("qa_review", True),
            ("deployment", False),
            ("production_monitoring", False),
        ]

        for stage, requires_gate in stages:
            # Approve gate if needed before advancing
            if requires_gate:
                current_response = await test_client.get(
                    f"/api/v1/projects/{test_project_data.id}/workflow"
                )
                if current_response.json()["gateStatus"] == "pending":
                    await test_client.post(
                        f"/api/v1/projects/{test_project_data.id}/workflow/gate-approval",
                        json={
                            "action": "approve",
                            "approverId": str(uuid.uuid4())
                        }
                    )

            # Advance to stage
            response = await test_client.post(
                f"/api/v1/projects/{test_project_data.id}/workflow/advance",
                json={"toStage": stage}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["currentStage"] == stage

        # Verify final state
        final_response = await test_client.get(
            f"/api/v1/projects/{test_project_data.id}/workflow"
        )
        final_data = final_response.json()

        assert final_data["currentStage"] == "production_monitoring"
        assert len(final_data["completedStages"]) == 7
        assert final_data["availableTransitions"] == []


class TestWorkflowEventCascadeDelete:
    """Test CASCADE delete behavior."""

    async def test_cascade_delete_project_deletes_events(
        self,
        test_client: AsyncClient,
        test_project_data,
        db_session: AsyncSession
    ):
        """Test that deleting project cascades to workflow events."""
        # Create some workflow events
        await test_client.post(
            f"/api/v1/projects/{test_project_data.id}/workflow/advance",
            json={"toStage": "market_research"}
        )

        # Verify event exists
        from sqlalchemy import select
        result = await db_session.execute(
            select(WorkflowEvent).where(
                WorkflowEvent.project_id == test_project_data.id
            )
        )
        events_before = result.scalars().all()
        assert len(events_before) > 0

        # Delete project
        project_repo = ProjectRepository(db_session)
        deleted = await project_repo.delete_project(test_project_data.id)
        assert deleted is True

        # Verify events are deleted
        result = await db_session.execute(
            select(WorkflowEvent).where(
                WorkflowEvent.project_id == test_project_data.id
            )
        )
        events_after = result.scalars().all()
        assert len(events_after) == 0
