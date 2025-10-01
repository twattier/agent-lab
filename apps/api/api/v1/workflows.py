"""
Workflow management API endpoints for project workflow state transitions.
Story 2.3 Implementation.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.schemas import (
    WorkflowStateResponse,
    WorkflowEventResponse,
    WorkflowAdvanceRequest,
    GateApprovalRequest,
)
from services.workflow_service import WorkflowService
from repositories.workflow_event_repository import WorkflowEventRepository
from core.workflow_templates import load_workflow_template

router = APIRouter()


@router.get(
    "/projects/{project_id}/workflow",
    response_model=WorkflowStateResponse,
    status_code=status.HTTP_200_OK
)
async def get_workflow_state(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> WorkflowStateResponse:
    """
    Get current workflow state for a project.

    Returns:
    - **currentStage**: Current workflow stage ID
    - **completedStages**: Array of completed stage IDs
    - **stageData**: Stage-specific metadata
    - **lastTransition**: Timestamp of last transition
    - **gateStatus**: Current gate status (pending/approved/rejected/not_required)
    - **availableTransitions**: List of valid next stages

    Raises:
    - **404**: Project not found or workflow state not initialized
    """
    workflow_service = WorkflowService(db)

    # Get workflow state
    workflow_state = await workflow_service.get_workflow_state(project_id)
    if not workflow_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found or workflow state not initialized"
        )

    # Get available transitions
    template_name = workflow_state.stageData.get("template", "bmad_method")
    available_transitions = await workflow_service.get_available_transitions(
        project_id,
        template_name
    )

    # Return with available transitions
    response = WorkflowStateResponse(
        **workflow_state.model_dump(),
        availableTransitions=available_transitions
    )
    return response


@router.post(
    "/projects/{project_id}/workflow/advance",
    response_model=WorkflowStateResponse,
    status_code=status.HTTP_200_OK
)
async def advance_workflow_stage(
    project_id: uuid.UUID,
    request: WorkflowAdvanceRequest,
    db: AsyncSession = Depends(get_db)
) -> WorkflowStateResponse:
    """
    Advance workflow to next stage.

    Request Body:
    - **toStage**: Target stage ID (required)
    - **notes**: Optional notes for the transition
    - **stageData**: Optional additional stage metadata

    Returns:
    - Updated workflow state with available transitions

    Raises:
    - **400**: Invalid transition (gate not approved, invalid toStage, etc.)
    - **404**: Project not found
    """
    workflow_service = WorkflowService(db)

    # Use a placeholder user_id (in production, get from auth context)
    # For now, generate a UUID
    user_id = uuid.uuid4()

    try:
        # Advance stage
        workflow_state = await workflow_service.advance_stage(
            project_id=project_id,
            to_stage=request.toStage,
            user_id=user_id,
            notes=request.notes,
            stage_data=request.stageData
        )

        # Get available transitions for response
        template_name = workflow_state.stageData.get("template", "bmad_method")
        available_transitions = await workflow_service.get_available_transitions(
            project_id,
            template_name
        )

        response = WorkflowStateResponse(
            **workflow_state.model_dump(),
            availableTransitions=available_transitions
        )
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/projects/{project_id}/workflow/gate-approval",
    response_model=WorkflowStateResponse,
    status_code=status.HTTP_200_OK
)
async def handle_gate_approval(
    project_id: uuid.UUID,
    request: GateApprovalRequest,
    db: AsyncSession = Depends(get_db)
) -> WorkflowStateResponse:
    """
    Approve or reject gate for current stage.

    Request Body:
    - **action**: 'approve' or 'reject' (required)
    - **feedback**: Optional feedback message
    - **approverId**: UUID of user approving/rejecting (required)

    Returns:
    - Updated workflow state with available transitions

    Raises:
    - **400**: Current stage does not require gate approval
    - **404**: Project not found
    """
    workflow_service = WorkflowService(db)

    try:
        if request.action == "approve":
            workflow_state = await workflow_service.approve_gate(
                project_id=project_id,
                approver_id=request.approverId,
                feedback=request.feedback
            )
        else:  # reject
            workflow_state = await workflow_service.reject_gate(
                project_id=project_id,
                approver_id=request.approverId,
                feedback=request.feedback
            )

        # Get available transitions for response
        template_name = workflow_state.stageData.get("template", "bmad_method")
        available_transitions = await workflow_service.get_available_transitions(
            project_id,
            template_name
        )

        response = WorkflowStateResponse(
            **workflow_state.model_dump(),
            availableTransitions=available_transitions
        )
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/projects/{project_id}/workflow/history",
    response_model=List[WorkflowEventResponse],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK
)
async def get_workflow_history(
    project_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(50, ge=1, le=100, description="Events per page"),
    db: AsyncSession = Depends(get_db)
) -> List[WorkflowEventResponse]:
    """
    Get workflow event history for a project.

    Query Parameters:
    - **page**: Page number (default: 1)
    - **limit**: Events per page (default: 50, max: 100)

    Returns:
    - Array of workflow events sorted by timestamp (most recent first)

    Raises:
    - **404**: Project not found
    """
    # Verify project exists
    workflow_service = WorkflowService(db)
    project = await workflow_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Get workflow events
    workflow_event_repo = WorkflowEventRepository(db)
    offset = (page - 1) * limit

    events = await workflow_event_repo.get_project_history(
        project_id=project_id,
        limit=limit,
        offset=offset
    )

    # Convert to response schema
    return [WorkflowEventResponse.model_validate(event) for event in events]
