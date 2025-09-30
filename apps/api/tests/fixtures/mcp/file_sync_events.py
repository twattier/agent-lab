"""
MCP File Synchronization Event Fixtures

Provides realistic file sync event samples for testing MCP
file operations and synchronization.
"""

FILE_SYNC_READ_EVENT = {
    "event_type": "file_read",
    "file_path": "/home/user/projects/agentlab/apps/api/main.py",
    "timestamp": "2025-09-30T10:00:00Z",
    "requested_by": "dev_agent_james",
    "status": "success",
    "metadata": {
        "file_size": 1024,
        "encoding": "utf-8",
        "line_count": 45
    }
}

FILE_SYNC_WRITE_EVENT = {
    "event_type": "file_write",
    "file_path": "/home/user/projects/agentlab/apps/api/api/v1/health.py",
    "timestamp": "2025-09-30T10:05:00Z",
    "requested_by": "dev_agent_james",
    "status": "success",
    "changes": {
        "lines_added": 10,
        "lines_deleted": 2,
        "lines_modified": 3
    },
    "metadata": {
        "file_size": 1536,
        "backup_created": True
    }
}

FILE_SYNC_ERROR_EVENT = {
    "event_type": "file_write",
    "file_path": "/root/protected/file.py",
    "timestamp": "2025-09-30T10:10:00Z",
    "requested_by": "dev_agent_james",
    "status": "error",
    "error": {
        "code": "permission_denied",
        "message": "Permission denied: Cannot write to protected directory"
    }
}

FILE_SYNC_BATCH_EVENT = {
    "event_type": "batch_sync",
    "timestamp": "2025-09-30T10:15:00Z",
    "requested_by": "dev_agent_james",
    "status": "partial_success",
    "files": [
        {
            "file_path": "/home/user/projects/agentlab/apps/api/models/database.py",
            "operation": "write",
            "status": "success"
        },
        {
            "file_path": "/home/user/projects/agentlab/apps/api/repositories/base.py",
            "operation": "write",
            "status": "success"
        },
        {
            "file_path": "/home/user/projects/agentlab/apps/api/invalid/path.py",
            "operation": "write",
            "status": "error",
            "error": "Path does not exist"
        }
    ],
    "summary": {
        "total": 3,
        "success": 2,
        "failed": 1
    }
}

FILE_SYNC_STATUS_QUERY = {
    "query_type": "sync_status",
    "project_path": "/home/user/projects/agentlab",
    "timestamp": "2025-09-30T10:20:00Z",
    "result": {
        "synchronized": True,
        "last_sync": "2025-09-30T10:15:00Z",
        "pending_changes": 0,
        "files_tracked": 152,
        "sync_conflicts": []
    }
}

FILE_SYNC_CONFLICT_EVENT = {
    "event_type": "sync_conflict",
    "file_path": "/home/user/projects/agentlab/apps/api/main.py",
    "timestamp": "2025-09-30T10:25:00Z",
    "conflict": {
        "local_modified": "2025-09-30T10:20:00Z",
        "remote_modified": "2025-09-30T10:22:00Z",
        "conflict_type": "concurrent_modification",
        "resolution": "manual_required"
    },
    "status": "unresolved"
}
