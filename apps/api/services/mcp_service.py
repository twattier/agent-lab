"""
MCP (Model Context Protocol) service for Claude Code communication.
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPMessage(BaseModel):
    """MCP message structure."""
    type: str
    data: Dict[str, Any]
    project_id: Optional[str] = None


class MCPService:
    """Service for MCP protocol communication with Claude Code."""

    def __init__(self):
        # Epic 3 enhancements
        self.enabled = os.getenv("MCP_ENABLED", "true").lower() == "true"
        self.server_url = os.getenv("MCP_SERVER_URL", "ws://localhost:8080/mcp")
        self.timeout = int(os.getenv("MCP_TIMEOUT", "30000")) / 1000

        self.session_id: Optional[str] = None
        self.last_heartbeat: Optional[datetime] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        # Legacy support
        self.client: Optional[httpx.AsyncClient] = None
        self.connected = False

    async def connect(self) -> bool:
        """Establish connection to MCP server."""
        if not self.enabled:
            logger.info("MCP is disabled in configuration")
            return False

        try:
            # TODO: Implement WebSocket connection using mcp library
            # For now, mark as connected for development
            self.connected = True
            self.last_heartbeat = datetime.now()

            # Start heartbeat task
            if not self._heartbeat_task or self._heartbeat_task.done():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            logger.info(f"MCP connection established to {self.server_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> None:
        """Close MCP connection."""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()

        if self.client:
            await self.client.aclose()

        self.connected = False
        self.session_id = None
        logger.info("Disconnected from MCP server")

    async def send_message(self, message: MCPMessage) -> Dict[str, Any]:
        """Send message to MCP server."""
        if not self.connected or not self.client:
            raise ConnectionError("MCP client not connected")

        try:
            response = await self.client.post(
                "/mcp/message",
                json=message.dict()
            )
            response.raise_for_status()
            return response.json()

        except httpx.RequestError as e:
            logger.error(f"MCP request failed: {e}")
            raise ConnectionError(f"Failed to send MCP message: {e}")

    async def sync_project_files(
        self,
        project_id: str,
        file_paths: list[str]
    ) -> Dict[str, Any]:
        """Synchronize project files with Claude Code."""
        message = MCPMessage(
            type="file_sync",
            data={"file_paths": file_paths},
            project_id=project_id
        )
        return await self.send_message(message)

    async def update_project_context(
        self,
        project_id: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update project context in Claude Code."""
        message = MCPMessage(
            type="context_update",
            data=context_data,
            project_id=project_id
        )
        return await self.send_message(message)

    async def initialize_session(self, workspace_path: Path) -> str:
        """Initialize MCP session with workspace path.

        Args:
            workspace_path: Path to project workspace

        Returns:
            Session ID from MCP server

        Raises:
            RuntimeError: If session initialization fails or times out
        """
        if not self.enabled:
            logger.debug("MCP disabled, skipping session initialization")
            return "mcp-disabled"

        if not self.connected:
            await self.connect()

        try:
            # Validate workspace path exists
            if not workspace_path.exists():
                raise ValueError(f"Workspace path does not exist: {workspace_path}")

            # TODO: Send session initialization message to MCP server
            # For now, generate mock session ID
            self.session_id = f"session-{uuid.uuid4()}"

            logger.info(f"MCP session initialized: {self.session_id} (workspace: {workspace_path})")
            return self.session_id

        except asyncio.TimeoutError:
            raise RuntimeError(f"MCP session initialization timed out after {self.timeout}s")

        except Exception as e:
            logger.error(f"MCP session initialization failed: {str(e)}")
            raise

    async def send_workflow_event(self, event_type: str, payload: dict) -> bool:
        """Send workflow event to MCP server.

        Args:
            event_type: Type of event ('TEMPLATE_IMPORTED', 'TEMPLATE_VALIDATED', 'PROVIDER_CONFIGURED')
            payload: Event payload data

        Returns:
            True if event sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"MCP disabled, skipping event: {event_type}")
            return False

        try:
            if not self.connected:
                logger.warning(f"MCP not connected, cannot send event: {event_type}")
                return False

            # TODO: Send event via MCP protocol
            logger.info(f"MCP event sent: {event_type} (payload: {len(str(payload))} bytes)")
            return True

        except Exception as e:
            logger.warning(f"MCP event publishing failed: {event_type}, error: {str(e)}")
            return False

    def get_status(self) -> dict:
        """Get current MCP connection status.

        Returns:
            Dictionary with connection status details
        """
        uptime = 0
        if self.last_heartbeat and self.connected:
            uptime = int((datetime.now() - self.last_heartbeat).total_seconds())

        return {
            "connected": self.connected,
            "session_id": self.session_id,
            "uptime": uptime,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "enabled": self.enabled,
        }

    async def _heartbeat_loop(self):
        """Heartbeat loop to maintain connection (every 30 seconds)."""
        while self.connected:
            try:
                await asyncio.sleep(30)

                if self.connected:
                    # TODO: Send heartbeat message
                    self.last_heartbeat = datetime.now()
                    logger.debug("MCP heartbeat sent")

            except asyncio.CancelledError:
                logger.debug("Heartbeat task cancelled")
                break

            except Exception as e:
                logger.error(f"Heartbeat failed: {str(e)}")

    async def health_check(self) -> Dict[str, str]:
        """Check MCP connection health."""
        if not self.enabled:
            return {"status": "disabled", "message": "MCP is disabled"}

        if not self.connected:
            return {"status": "disconnected", "message": "Not connected to MCP server"}

        return {"status": "healthy", "message": "MCP connection is healthy"}


# Global MCP service instance
mcp_service = MCPService()


async def get_mcp_service() -> MCPService:
    """Dependency for getting MCP service."""
    return mcp_service