"""
MCP Workflow State Fixtures

Provides realistic BMAD workflow state samples for testing MCP
integration and workflow automation.
"""

WORKFLOW_STATE_DRAFT = {
    "workflow_id": "wf_001",
    "project_id": "proj_123",
    "state": "draft",
    "current_phase": "planning",
    "story_data": {
        "story_id": "story_1.1",
        "title": "Project Scaffolding",
        "status": "draft",
        "assignee": None
    },
    "file_sync_status": "pending",
    "claude_code_path": None,
    "last_updated": "2025-09-30T10:00:00Z"
}

WORKFLOW_STATE_IN_PROGRESS = {
    "workflow_id": "wf_002",
    "project_id": "proj_123",
    "state": "in_progress",
    "current_phase": "development",
    "story_data": {
        "story_id": "story_1.2",
        "title": "Docker Infrastructure Setup",
        "status": "in_progress",
        "assignee": "dev_agent_james"
    },
    "file_sync_status": "synchronized",
    "claude_code_path": "/home/user/projects/agentlab",
    "tasks_completed": 3,
    "tasks_total": 10,
    "last_updated": "2025-09-30T12:00:00Z"
}

WORKFLOW_STATE_READY_FOR_QA = {
    "workflow_id": "wf_003",
    "project_id": "proj_123",
    "state": "ready_for_qa",
    "current_phase": "qa_review",
    "story_data": {
        "story_id": "story_1.3",
        "title": "Backend API Foundation",
        "status": "ready_for_review",
        "assignee": "qa_agent_quinn"
    },
    "file_sync_status": "synchronized",
    "claude_code_path": "/home/user/projects/agentlab",
    "tasks_completed": 8,
    "tasks_total": 8,
    "test_results": {
        "passed": 45,
        "failed": 0,
        "coverage": 92.5
    },
    "last_updated": "2025-09-30T14:00:00Z"
}

WORKFLOW_STATE_COMPLETED = {
    "workflow_id": "wf_004",
    "project_id": "proj_123",
    "state": "completed",
    "current_phase": "done",
    "story_data": {
        "story_id": "story_1.4",
        "title": "Frontend Foundation",
        "status": "completed",
        "assignee": None
    },
    "file_sync_status": "archived",
    "claude_code_path": "/home/user/projects/agentlab",
    "tasks_completed": 10,
    "tasks_total": 10,
    "test_results": {
        "passed": 38,
        "failed": 0,
        "coverage": 100.0
    },
    "po_approval": True,
    "completed_at": "2025-09-30T16:00:00Z",
    "last_updated": "2025-09-30T16:00:00Z"
}

WORKFLOW_TRANSITION_LOG = [
    {
        "from_state": "draft",
        "to_state": "in_progress",
        "timestamp": "2025-09-30T11:00:00Z",
        "actor": "dev_agent_james",
        "reason": "Story approved and development started"
    },
    {
        "from_state": "in_progress",
        "to_state": "ready_for_qa",
        "timestamp": "2025-09-30T13:00:00Z",
        "actor": "dev_agent_james",
        "reason": "All tasks completed, tests passing"
    },
    {
        "from_state": "ready_for_qa",
        "to_state": "in_progress",
        "timestamp": "2025-09-30T13:30:00Z",
        "actor": "qa_agent_quinn",
        "reason": "Issues found in QA review"
    },
    {
        "from_state": "in_progress",
        "to_state": "ready_for_qa",
        "timestamp": "2025-09-30T14:00:00Z",
        "actor": "dev_agent_james",
        "reason": "QA fixes applied"
    },
    {
        "from_state": "ready_for_qa",
        "to_state": "completed",
        "timestamp": "2025-09-30T16:00:00Z",
        "actor": "po_sarah",
        "reason": "PO approved, story complete"
    }
]
