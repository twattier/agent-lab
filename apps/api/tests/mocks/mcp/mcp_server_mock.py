"""
Mock MCP Server Implementation

Provides a mock implementation of the Claude Code MCP (Model Context Protocol)
server for testing file synchronization and workflow automation without
requiring a real MCP server connection.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from tests.fixtures.mcp.workflow_states import (
    WORKFLOW_STATE_DRAFT,
    WORKFLOW_STATE_IN_PROGRESS,
    WORKFLOW_STATE_READY_FOR_QA,
    WORKFLOW_STATE_COMPLETED,
)
from tests.fixtures.mcp.file_sync_events import (
    FILE_SYNC_READ_EVENT,
    FILE_SYNC_WRITE_EVENT,
    FILE_SYNC_ERROR_EVENT,
)


class MCPConnectionState(Enum):
    """MCP connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MockMCPServer:
    """
    Mock implementation of Claude Code MCP Server for testing.

    Simulates file synchronization, workflow state management, and
    real-time status updates without requiring an actual MCP server.

    Usage:
        >>> mock_mcp = MockMCPServer()
        >>> await mock_mcp.connect()
        >>> result = await mock_mcp.read_file("/path/to/file.py")
        >>> await mock_mcp.write_file("/path/to/file.py", "content")
    """

    def __init__(
        self,
        server_url: str = "ws://localhost:8765",
        fail_rate: float = 0.0,
        simulate_latency: bool = False
    ):
        """
        Initialize mock MCP server.

        Args:
            server_url: Mock server URL (not actually used)
            fail_rate: Probability of simulating errors (0.0 to 1.0)
            simulate_latency: Whether to simulate network latency
        """
        self.server_url = server_url
        self.fail_rate = fail_rate
        self.simulate_latency = simulate_latency
        self.connection_state = MCPConnectionState.DISCONNECTED
        self.workflow_states: Dict[str, Dict[str, Any]] = {}
        self.file_system: Dict[str, str] = {}
        self.event_log: List[Dict[str, Any]] = []

    async def connect(self) -> Dict[str, Any]:
        """
        Mock MCP server connection.

        Returns:
            Connection status response
        """
        import random
        if random.random() < self.fail_rate:
            self.connection_state = MCPConnectionState.ERROR
            return {
                "status": "error",
                "error": "Connection failed: Timeout"
            }

        self.connection_state = MCPConnectionState.CONNECTED
        return {
            "status": "connected",
            "server_version": "1.0.0",
            "protocol_version": "mcp-v1"
        }

    async def disconnect(self) -> Dict[str, Any]:
        """Mock disconnect from MCP server."""
        self.connection_state = MCPConnectionState.DISCONNECTED
        return {"status": "disconnected"}

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Mock file read operation.

        Args:
            file_path: Path to file to read

        Returns:
            File read result with content or error
        """
        import random
        if random.random() < self.fail_rate:
            event = FILE_SYNC_ERROR_EVENT.copy()
            event["file_path"] = file_path
            self.event_log.append(event)
            return {
                "status": "error",
                "error": "Permission denied"
            }

        # Return mock content or error if not exists
        if file_path not in self.file_system:
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }

        event = FILE_SYNC_READ_EVENT.copy()
        event["file_path"] = file_path
        self.event_log.append(event)

        return {
            "status": "success",
            "file_path": file_path,
            "content": self.file_system[file_path],
            "metadata": {
                "size": len(self.file_system[file_path]),
                "encoding": "utf-8"
            }
        }

    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Mock file write operation.

        Args:
            file_path: Path to file to write
            content: File content

        Returns:
            File write result
        """
        import random
        if random.random() < self.fail_rate:
            event = FILE_SYNC_ERROR_EVENT.copy()
            event["file_path"] = file_path
            self.event_log.append(event)
            return {
                "status": "error",
                "error": "Write failed: Permission denied"
            }

        self.file_system[file_path] = content

        event = FILE_SYNC_WRITE_EVENT.copy()
        event["file_path"] = file_path
        self.event_log.append(event)

        return {
            "status": "success",
            "file_path": file_path,
            "bytes_written": len(content)
        }

    async def sync_files(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Mock batch file synchronization.

        Args:
            files: List of file operations {"path": str, "operation": str, "content": str}

        Returns:
            Batch sync result
        """
        results = []
        for file_op in files:
            if file_op["operation"] == "write":
                result = await self.write_file(file_op["path"], file_op.get("content", ""))
                results.append({
                    "file_path": file_op["path"],
                    "status": result["status"]
                })
            elif file_op["operation"] == "read":
                result = await self.read_file(file_op["path"])
                results.append({
                    "file_path": file_op["path"],
                    "status": result["status"]
                })

        success_count = sum(1 for r in results if r["status"] == "success")
        return {
            "status": "completed",
            "total": len(files),
            "success": success_count,
            "failed": len(files) - success_count,
            "results": results
        }

    async def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """
        Mock get workflow state.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Current workflow state
        """
        if workflow_id not in self.workflow_states:
            # Return a default draft state
            return WORKFLOW_STATE_DRAFT.copy()

        return self.workflow_states[workflow_id]

    async def update_workflow_state(
        self,
        workflow_id: str,
        state: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mock workflow state update.

        Args:
            workflow_id: Workflow identifier
            state: New state
            metadata: Additional metadata

        Returns:
            Updated workflow state
        """
        if workflow_id not in self.workflow_states:
            self.workflow_states[workflow_id] = WORKFLOW_STATE_DRAFT.copy()

        self.workflow_states[workflow_id]["state"] = state
        if metadata:
            self.workflow_states[workflow_id].update(metadata)

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "state": state
        }

    async def simulate_real_time_update(self, workflow_id: str) -> Dict[str, Any]:
        """
        Mock real-time status update event.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Real-time update event
        """
        return {
            "event_type": "workflow_update",
            "workflow_id": workflow_id,
            "timestamp": "2025-09-30T10:00:00Z",
            "data": self.workflow_states.get(workflow_id, WORKFLOW_STATE_DRAFT)
        }

    def get_event_log(self) -> List[Dict[str, Any]]:
        """Get all logged events for debugging."""
        return self.event_log

    def clear_event_log(self):
        """Clear event log."""
        self.event_log = []

    def is_connected(self) -> bool:
        """Check if mock server is connected."""
        return self.connection_state == MCPConnectionState.CONNECTED
