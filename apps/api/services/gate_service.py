"""Gate management service for Story 3.2."""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import (
    WorkflowGate,
    GateReviewer,
    Contact,
    WorkflowEvent,
    WorkflowEventType,
    Project
)
from models.gate import (
    Gate,
    GateReviewer as GateReviewerSchema,
    Contact as ContactSchema
)
from services.interfaces.workflow_progression_interface import IWorkflowProgressionEngine

logger = logging.getLogger(__name__)


class GateService:
    """Service for managing workflow gates, approvals, and reviewers."""

    def __init__(
        self,
        session: AsyncSession,
        progression_engine: Optional[IWorkflowProgressionEngine] = None
    ):
        """Initialize GateService.

        Args:
            session: Database session
            progression_engine: Workflow progression engine (Story 3.3 integration)
        """
        self.session = session
        self.progression_engine = progression_engine

    async def get_project_gates(
        self,
        project_id: UUID,
        status_filter: Optional[str] = None
    ) -> List[Gate]:
        """Get all gates for a project.

        Args:
            project_id: Project UUID
            status_filter: Optional status filter ('pending', 'approved', 'rejected', 'blocked')

        Returns:
            List of Gate models
        """
        # First verify project exists
        project_result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            return []

        # Query gates (Note: assuming project has template_id in workflow_state)
        # For now, return all gates as we don't have direct project-template relationship
        query = select(WorkflowGate)

        if status_filter:
            query = query.where(WorkflowGate.status == status_filter)

        result = await self.session.execute(query)
        gates = result.scalars().all()

        return [Gate.model_validate(gate) for gate in gates]

    async def validate_gate_dependencies(
        self,
        gate_id: UUID
    ) -> Tuple[bool, List[str]]:
        """Validate gate dependencies are met.

        Args:
            gate_id: Gate UUID

        Returns:
            Tuple of (can_approve: bool, blocked_gates: list[str])
        """
        result = await self.session.execute(
            select(WorkflowGate).where(WorkflowGate.id == gate_id)
        )
        gate = result.scalar_one_or_none()

        if not gate:
            return False, []

        # Parse required_gates from criteria JSONB
        criteria = gate.criteria or {}
        required_gates = criteria.get('required_gates', [])

        if not required_gates:
            return True, []

        # Check if all required gates are approved
        blocked_gates = []
        for required_gate_id in required_gates:
            gate_result = await self.session.execute(
                select(WorkflowGate).where(
                    and_(
                        WorkflowGate.gate_id == required_gate_id,
                        WorkflowGate.template_id == gate.template_id
                    )
                )
            )
            required_gate = gate_result.scalar_one_or_none()

            if not required_gate or required_gate.status != 'approved':
                blocked_gates.append(required_gate_id)

        return len(blocked_gates) == 0, blocked_gates

    async def check_gate_sequence(
        self,
        gate_id: UUID
    ) -> Tuple[bool, str]:
        """Check gate sequence enforcement.

        Args:
            gate_id: Gate UUID

        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        result = await self.session.execute(
            select(WorkflowGate).where(WorkflowGate.id == gate_id)
        )
        gate = result.scalar_one_or_none()

        if not gate:
            return False, "Gate not found"

        # Get sequence_number from criteria (if exists)
        criteria = gate.criteria or {}
        sequence_number = criteria.get('sequence_number')

        if sequence_number is None:
            # No sequence enforcement
            return True, ''

        # Query previous gates in same stage
        previous_gates_result = await self.session.execute(
            select(WorkflowGate).where(
                and_(
                    WorkflowGate.template_id == gate.template_id,
                    WorkflowGate.stage_id == gate.stage_id,
                    WorkflowGate.id != gate_id
                )
            )
        )
        previous_gates = previous_gates_result.scalars().all()

        # Check all previous gates (lower sequence) are approved
        for prev_gate in previous_gates:
            prev_seq = prev_gate.criteria.get('sequence_number')
            if prev_seq and prev_seq < sequence_number:
                if prev_gate.status != 'approved':
                    return False, f"Gate '{prev_gate.name}' must be approved first"

        return True, ''

    async def approve_gate(
        self,
        gate_id: UUID,
        user_id: UUID,
        comment: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Gate:
        """Approve a gate.

        Args:
            gate_id: Gate UUID
            user_id: User UUID performing approval
            comment: Approval comment
            metadata: Optional metadata

        Returns:
            Updated Gate model

        Raises:
            ValueError: If dependencies not met or validation fails
        """
        # Validate dependencies
        can_approve, blocked_gates = await self.validate_gate_dependencies(gate_id)
        if not can_approve:
            raise ValueError(
                f"Cannot approve gate: dependencies not met. "
                f"Blocked gates: {', '.join(blocked_gates)}"
            )

        # Check sequence
        is_valid_sequence, error_msg = await self.check_gate_sequence(gate_id)
        if not is_valid_sequence:
            raise ValueError(f"Cannot approve gate: {error_msg}")

        # Get gate
        result = await self.session.execute(
            select(WorkflowGate).where(WorkflowGate.id == gate_id)
        )
        gate = result.scalar_one_or_none()

        if not gate:
            raise ValueError(f"Gate {gate_id} not found")

        # Update gate status in transaction
        async with self.session.begin_nested():
            gate.status = 'approved'

            # Create workflow event
            event = WorkflowEvent(
                project_id=user_id,  # TODO: Get actual project_id from gate/context
                event_type=WorkflowEventType.GATE_APPROVED,
                to_stage=gate.stage_id,
                user_id=user_id,
                event_metadata={
                    'gate_id': str(gate_id),
                    'gate_name': gate.name,
                    'comment': comment,
                    **(metadata or {})
                }
            )
            self.session.add(event)

            await self.session.flush()

        # Call progression engine if available
        if self.progression_engine:
            try:
                # TODO: Get actual project_id
                await self.progression_engine.advance_workflow_stage(
                    project_id=user_id,  # Placeholder
                    gate_id=gate_id
                )
            except Exception as e:
                logger.warning(f"Workflow progression failed: {e}")

        await self.session.commit()

        return Gate.model_validate(gate)

    async def reject_gate(
        self,
        gate_id: UUID,
        user_id: UUID,
        reason: str,
        recommendations: Optional[str] = None
    ) -> Gate:
        """Reject a gate.

        Args:
            gate_id: Gate UUID
            user_id: User UUID performing rejection
            reason: Rejection reason (min 10 chars)
            recommendations: Optional recommendations

        Returns:
            Updated Gate model

        Raises:
            ValueError: If validation fails
        """
        if len(reason) < 10:
            raise ValueError("Rejection reason must be at least 10 characters")

        # Get gate
        result = await self.session.execute(
            select(WorkflowGate).where(WorkflowGate.id == gate_id)
        )
        gate = result.scalar_one_or_none()

        if not gate:
            raise ValueError(f"Gate {gate_id} not found")

        # Update gate status in transaction
        async with self.session.begin_nested():
            gate.status = 'rejected'

            # Create workflow event
            event = WorkflowEvent(
                project_id=user_id,  # TODO: Get actual project_id
                event_type=WorkflowEventType.GATE_REJECTED,
                to_stage=gate.stage_id,
                user_id=user_id,
                event_metadata={
                    'gate_id': str(gate_id),
                    'gate_name': gate.name,
                    'reason': reason,
                    'recommendations': recommendations
                }
            )
            self.session.add(event)

            await self.session.flush()

        # Log notification
        await self._log_gate_notification(gate_id, 'gate_rejected')

        await self.session.commit()

        return Gate.model_validate(gate)

    async def assign_reviewer(
        self,
        gate_id: UUID,
        contact_id: UUID,
        reviewer_role: str
    ) -> GateReviewerSchema:
        """Assign reviewer to gate.

        Args:
            gate_id: Gate UUID
            contact_id: Contact UUID
            reviewer_role: Role of reviewer

        Returns:
            GateReviewer model

        Raises:
            ValueError: If contact invalid or already assigned
        """
        # Validate contact exists and is active
        contact_result = await self.session.execute(
            select(Contact).where(
                and_(
                    Contact.id == contact_id,
                    Contact.is_active == True
                )
            )
        )
        contact = contact_result.scalar_one_or_none()

        if not contact:
            raise ValueError(f"Contact {contact_id} not found or inactive")

        # Check if already assigned
        existing_result = await self.session.execute(
            select(GateReviewer).where(
                and_(
                    GateReviewer.gate_id == gate_id,
                    GateReviewer.contact_id == contact_id
                )
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Contact {contact_id} already assigned to gate {gate_id}")

        # Create reviewer assignment
        reviewer = GateReviewer(
            gate_id=gate_id,
            contact_id=contact_id,
            reviewer_role=reviewer_role
        )
        self.session.add(reviewer)

        # Create workflow event
        # TODO: Get actual project_id
        event = WorkflowEvent(
            project_id=contact_id,  # Placeholder
            event_type=WorkflowEventType.REVIEWER_ASSIGNED,
            to_stage='',  # Will update with actual stage
            user_id=contact_id,  # TODO: Get actual user_id from context
            event_metadata={
                'gate_id': str(gate_id),
                'contact_id': str(contact_id),
                'reviewer_role': reviewer_role
            }
        )
        self.session.add(event)

        await self.session.commit()

        return GateReviewerSchema.model_validate(reviewer)

    async def get_gate_reviewers(
        self,
        gate_id: UUID
    ) -> List[GateReviewerSchema]:
        """Get reviewers for a gate.

        Args:
            gate_id: Gate UUID

        Returns:
            List of GateReviewer models
        """
        result = await self.session.execute(
            select(GateReviewer).options(
                selectinload(GateReviewer.contact)
            ).where(
                GateReviewer.gate_id == gate_id
            )
        )
        reviewers = result.scalars().all()

        # Filter out inactive contacts
        active_reviewers = [
            r for r in reviewers
            if r.contact and r.contact.is_active
        ]

        return [GateReviewerSchema.model_validate(r) for r in active_reviewers]

    async def _log_gate_notification(
        self,
        gate_id: UUID,
        event_type: str
    ) -> None:
        """Log gate notification event.

        Args:
            gate_id: Gate UUID
            event_type: Type of notification event
        """
        # Get reviewers
        reviewers = await self.get_gate_reviewers(gate_id)
        recipient_emails = [r.contact.email for r in reviewers if r.contact]

        log_level = logging.WARNING if event_type == 'gate_rejected' else logging.INFO

        logger.log(
            log_level,
            f"Gate notification: {event_type} for gate {gate_id} "
            f"to {len(recipient_emails)} recipients"
        )

    async def get_gate_history(
        self,
        gate_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get gate approval/rejection history.

        Args:
            gate_id: Gate UUID

        Returns:
            List of workflow events for the gate
        """
        # Query workflow events filtered by gate_id in metadata
        # Note: This is a JSONB query which may need proper indexing
        result = await self.session.execute(
            select(WorkflowEvent).where(
                WorkflowEvent.event_metadata['gate_id'].astext == str(gate_id)
            ).order_by(WorkflowEvent.timestamp.desc())
        )
        events = result.scalars().all()

        return [
            {
                'id': str(event.id),
                'event_type': event.event_type.value,
                'user_id': str(event.user_id),
                'timestamp': event.timestamp.isoformat(),
                'metadata': event.event_metadata
            }
            for event in events
        ]

    async def get_workflow_history(
        self,
        project_id: UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get workflow history for a project.

        Args:
            project_id: Project UUID
            filters: Optional filters (event_type, date_range, gate_id)

        Returns:
            List of workflow events with pagination
        """
        filters = filters or {}

        query = select(WorkflowEvent).where(
            WorkflowEvent.project_id == project_id
        )

        # Apply filters
        if 'event_type' in filters:
            query = query.where(WorkflowEvent.event_type == filters['event_type'])

        if 'gate_id' in filters:
            query = query.where(
                WorkflowEvent.event_metadata['gate_id'].astext == filters['gate_id']
            )

        if 'date_from' in filters:
            query = query.where(WorkflowEvent.timestamp >= filters['date_from'])

        if 'date_to' in filters:
            query = query.where(WorkflowEvent.timestamp <= filters['date_to'])

        # Apply pagination
        offset = filters.get('offset', 0)
        limit = min(filters.get('limit', 50), 200)  # Max 200

        query = query.order_by(WorkflowEvent.timestamp.desc()).offset(offset).limit(limit)

        result = await self.session.execute(query)
        events = result.scalars().all()

        return [
            {
                'id': str(event.id),
                'event_type': event.event_type.value,
                'user_id': str(event.user_id),
                'timestamp': event.timestamp.isoformat(),
                'from_stage': event.from_stage,
                'to_stage': event.to_stage,
                'metadata': event.event_metadata
            }
            for event in events
        ]

    async def get_gate_metrics(
        self,
        project_id: UUID
    ) -> Dict[str, Any]:
        """Get gate metrics for a project.

        Args:
            project_id: Project UUID

        Returns:
            Dict with gate metrics
        """
        # Count gates by status
        # Note: This is a simplified version - proper implementation would need
        # project-template relationship
        status_counts = await self.session.execute(
            select(
                WorkflowGate.status,
                func.count(WorkflowGate.id)
            ).group_by(WorkflowGate.status)
        )

        counts = {status: count for status, count in status_counts}

        # Calculate average approval time
        # This requires joining with workflow_events
        # Simplified for now
        avg_approval_time = 0  # TODO: Calculate from events

        return {
            'total_gates': sum(counts.values()),
            'approved_count': counts.get('approved', 0),
            'rejected_count': counts.get('rejected', 0),
            'pending_count': counts.get('pending', 0),
            'blocked_count': counts.get('blocked', 0),
            'average_approval_time_hours': avg_approval_time
        }

    async def reset_gate(
        self,
        gate_id: UUID,
        user_id: UUID
    ) -> Gate:
        """Reset gate status to pending (admin only).

        Args:
            gate_id: Gate UUID
            user_id: User UUID performing reset

        Returns:
            Updated Gate model

        Raises:
            ValueError: If gate not found
        """
        result = await self.session.execute(
            select(WorkflowGate).where(WorkflowGate.id == gate_id)
        )
        gate = result.scalar_one_or_none()

        if not gate:
            raise ValueError(f"Gate {gate_id} not found")

        # Reset gate status
        async with self.session.begin_nested():
            gate.status = 'pending'

            # Clear approval/rejection metadata from criteria
            if gate.criteria:
                gate.criteria.pop('approval_metadata', None)
                gate.criteria.pop('rejection_metadata', None)

            # Create workflow event
            event = WorkflowEvent(
                project_id=user_id,  # TODO: Get actual project_id
                event_type=WorkflowEventType.GATE_RESET,
                to_stage=gate.stage_id,
                user_id=user_id,
                event_metadata={
                    'gate_id': str(gate_id),
                    'gate_name': gate.name
                }
            )
            self.session.add(event)

            await self.session.flush()

        await self.session.commit()

        logger.info(f"Gate {gate_id} reset by user {user_id}")

        return Gate.model_validate(gate)
