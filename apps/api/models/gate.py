"""Gate management Pydantic models."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class GateApprovalRequest(BaseModel):
    """Request model for gate approval."""
    comment: str = Field(..., min_length=1, description="Approval comment (required)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class GateRejectionRequest(BaseModel):
    """Request model for gate rejection."""
    reason: str = Field(..., min_length=10, description="Rejection reason (min 10 chars)")
    recommendations: Optional[str] = Field(default=None, description="Recommendations for improvement")


class AssignReviewerRequest(BaseModel):
    """Request model for assigning reviewer to gate."""
    contact_id: UUID = Field(..., description="Contact UUID to assign as reviewer")
    reviewer_role: str = Field(..., min_length=1, description="Role of the reviewer")


class Contact(BaseModel):
    """Contact model for reviewers."""
    id: UUID
    name: str
    email: str
    role: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class GateReviewer(BaseModel):
    """Gate reviewer assignment model."""
    id: UUID
    gate_id: UUID
    contact_id: UUID
    reviewer_role: str
    assigned_at: datetime
    contact: Optional[Contact] = None

    class Config:
        from_attributes = True


class Gate(BaseModel):
    """Gate model with workflow information."""
    id: UUID
    template_id: UUID
    gate_id: str
    name: str
    stage_id: str
    criteria: Dict[str, Any]
    status: str
    sequence_number: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GateResetRequest(BaseModel):
    """Request model for resetting a gate."""
    pass  # No body required for reset
