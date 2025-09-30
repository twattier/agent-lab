"""
MCP (Model Context Protocol) service for Claude Code communication.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import httpx
from pydantic import BaseModel

from core.config import get_settings

logger = logging.getLogger(__name__)


class MCPMessage(BaseModel):
    """MCP message structure."""
    type: str
    data: Dict[str, Any]
    project_id: Optional[str] = None


class MCPService:
    """Service for MCP protocol communication with Claude Code."""

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[httpx.AsyncClient] = None
        self.connected = False

    async def connect(self) -> bool:
        """Establish connection to MCP server."""
        if not self.settings.MCP_ENABLED:
            logger.info("MCP is disabled in configuration")
            return False

        try:
            self.client = httpx.AsyncClient(
                base_url=f"http://{self.settings.MCP_HOST}:{self.settings.MCP_PORT}",
                timeout=30.0
            )

            # Test connection with health check
            response = await self.client.get("/health")
            if response.status_code == 200:
                self.connected = True
                logger.info("Successfully connected to MCP server")
                return True
            else:
                logger.error(f"MCP health check failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False

    async def disconnect(self) -> None:
        """Close MCP connection."""
        if self.client:
            await self.client.aclose()
            self.connected = False
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

    async def health_check(self) -> Dict[str, str]:
        """Check MCP connection health."""
        if not self.settings.MCP_ENABLED:
            return {"status": "disabled", "message": "MCP is disabled"}

        if not self.connected:
            return {"status": "disconnected", "message": "Not connected to MCP server"}

        try:
            if self.client:
                response = await self.client.get("/health")
                if response.status_code == 200:
                    return {"status": "healthy", "message": "MCP connection is healthy"}
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"MCP health check failed: {response.status_code}"
                    }
            else:
                return {"status": "error", "message": "MCP client not initialized"}

        except Exception as e:
            return {"status": "error", "message": f"MCP health check error: {e}"}


# Global MCP service instance
mcp_service = MCPService()


async def get_mcp_service() -> MCPService:
    """Dependency for getting MCP service."""
    return mcp_service