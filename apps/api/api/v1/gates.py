"""Gate management API endpoints for Story 3.2."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.gate import (
    Gate,
    GateApprovalRequest,
    GateRejectionRequest,
    AssignReviewerRequest,
    GateReviewer,
    GateResetRequest
)
from services.gate_service import GateService
from tests.mocks.workflow.progression_engine_mock import MockWorkflowProgressionEngine

router = APIRouter(prefix="/projects", tags=["gates"])


def get_gate_service(session: AsyncSession = Depends(get_db)) -> GateService:
    """Dependency to get GateService instance."""
    # Use mock progression engine until Story 3.3 is complete
    progression_engine = MockWorkflowProgressionEngine()
    return GateService(session=session, progression_engine=progression_engine)


@router.get("/{projectId}/gates", response_model=List[Gate])
async def get_project_gates(
    projectId: UUID,
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected|blocked)$"),
    service: GateService = Depends(get_gate_service)
) -> List[Gate]:
    """Get all gates for a project.

    Args:
        projectId: Project UUID
        status: Optional status filter
        service: GateService dependency

    Returns:
        List of gates
    """
    try:
        gates = await service.get_project_gates(projectId, status_filter=status)
        return gates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve gates: {str(e)}"
        )


@router.get("/{projectId}/gates/{gateId}/history")
async def get_gate_history(
    projectId: UUID,
    gateId: UUID,
    service: GateService = Depends(get_gate_service)
) -> List[Dict[str, Any]]:
    """Get gate approval/rejection history.

    Args:
        projectId: Project UUID
        gateId: Gate UUID
        service: GateService dependency

    Returns:
        List of workflow events
    """
    try:
        history = await service.get_gate_history(gateId)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gate {gateId} not found"
            )
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve gate history: {str(e)}"
        )


@router.post("/{projectId}/gates/{gateId}/approve", response_model=Gate)
async def approve_gate(
    projectId: UUID,
    gateId: UUID,
    request: GateApprovalRequest,
    service: GateService = Depends(get_gate_service),
    # TODO: Add authentication dependency: current_user: User = Depends(require_role('product_owner'))
) -> Gate:
    """Approve a gate (human-only action).

    Args:
        projectId: Project UUID
        gateId: Gate UUID
        request: Approval request with comment
        service: GateService dependency

    Returns:
        Updated gate

    Raises:
        400: Dependencies not met or validation fails
        403: User lacks approval permissions
        404: Gate not found
    """
    try:
        # TODO: Get user_id from current_user (authentication)
        user_id = UUID('00000000-0000-0000-0000-000000000001')  # Placeholder

        gate = await service.approve_gate(
            gate_id=gateId,
            user_id=user_id,
            comment=request.comment,
            metadata=request.metadata
        )
        return gate
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve gate: {str(e)}"
        )


@router.post("/{projectId}/gates/{gateId}/reject", response_model=Gate)
async def reject_gate(
    projectId: UUID,
    gateId: UUID,
    request: GateRejectionRequest,
    service: GateService = Depends(get_gate_service),
    # TODO: Add authentication dependency: current_user: User = Depends(require_role('product_owner'))
) -> Gate:
    """Reject a gate (human-only action).

    Args:
        projectId: Project UUID
        gateId: Gate UUID
        request: Rejection request with reason
        service: GateService dependency

    Returns:
        Updated gate

    Raises:
        400: Validation fails
        403: User lacks rejection permissions
        404: Gate not found
    """
    try:
        # TODO: Get user_id from current_user (authentication)
        user_id = UUID('00000000-0000-0000-0000-000000000001')  # Placeholder

        gate = await service.reject_gate(
            gate_id=gateId,
            user_id=user_id,
            reason=request.reason,
            recommendations=request.recommendations
        )
        return gate
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject gate: {str(e)}"
        )


@router.post("/{projectId}/gates/{gateId}/reviewers", status_code=status.HTTP_201_CREATED, response_model=GateReviewer)
async def assign_reviewer(
    projectId: UUID,
    gateId: UUID,
    request: AssignReviewerRequest,
    service: GateService = Depends(get_gate_service)
) -> GateReviewer:
    """Assign reviewer to gate.

    Args:
        projectId: Project UUID
        gateId: Gate UUID
        request: Reviewer assignment request
        service: GateService dependency

    Returns:
        Gate reviewer assignment

    Raises:
        400: Contact invalid or already assigned
        404: Gate not found
    """
    try:
        reviewer = await service.assign_reviewer(
            gate_id=gateId,
            contact_id=request.contact_id,
            reviewer_role=request.reviewer_role
        )
        return reviewer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign reviewer: {str(e)}"
        )


@router.get("/{projectId}/gates/{gateId}/reviewers", response_model=List[GateReviewer])
async def get_gate_reviewers(
    projectId: UUID,
    gateId: UUID,
    service: GateService = Depends(get_gate_service)
) -> List[GateReviewer]:
    """Get reviewers for a gate.

    Args:
        projectId: Project UUID
        gateId: Gate UUID
        service: GateService dependency

    Returns:
        List of gate reviewers

    Raises:
        404: Gate not found
    """
    try:
        reviewers = await service.get_gate_reviewers(gateId)
        return reviewers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reviewers: {str(e)}"
        )


@router.get("/{projectId}/workflow/history")
async def get_workflow_history(
    projectId: UUID,
    event_type: Optional[str] = None,
    gate_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: GateService = Depends(get_gate_service)
) -> List[Dict[str, Any]]:
    """Get workflow history for a project.

    Args:
        projectId: Project UUID
        event_type: Optional event type filter
        gate_id: Optional gate ID filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        offset: Pagination offset
        limit: Pagination limit (max 200)
        service: GateService dependency

    Returns:
        Paginated list of workflow events

    Raises:
        404: Project not found
    """
    try:
        filters = {
            'offset': offset,
            'limit': limit
        }

        if event_type:
            filters['event_type'] = event_type
        if gate_id:
            filters['gate_id'] = gate_id
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to

        history = await service.get_workflow_history(projectId, filters=filters)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workflow history: {str(e)}"
        )


@router.get("/{projectId}/gates/metrics")
async def get_gate_metrics(
    projectId: UUID,
    service: GateService = Depends(get_gate_service)
) -> Dict[str, Any]:
    """Get gate analytics and metrics for a project.

    Args:
        projectId: Project UUID
        service: GateService dependency

    Returns:
        Gate metrics

    Raises:
        404: Project not found
    """
    try:
        metrics = await service.get_gate_metrics(projectId)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve gate metrics: {str(e)}"
        )


@router.post("/{projectId}/gates/{gateId}/reset", response_model=Gate)
async def reset_gate(
    projectId: UUID,
    gateId: UUID,
    service: GateService = Depends(get_gate_service),
    # TODO: Add authentication dependency: current_user: User = Depends(require_role('admin'))
) -> Gate:
    """Reset gate status to pending (admin only).

    Args:
        projectId: Project UUID
        gateId: Gate UUID
        service: GateService dependency

    Returns:
        Updated gate

    Raises:
        403: User not admin
        404: Gate not found
    """
    try:
        # TODO: Get user_id from current_user (authentication)
        user_id = UUID('00000000-0000-0000-0000-000000000001')  # Placeholder

        gate = await service.reset_gate(
            gate_id=gateId,
            user_id=user_id
        )
        return gate
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset gate: {str(e)}"
        )
