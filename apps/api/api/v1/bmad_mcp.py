"""BMAD MCP Protocol API endpoints."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from services.mcp_service import MCPService, get_mcp_service


router = APIRouter(prefix="/bmad/mcp", tags=["bmad-mcp"])


class MCPStatusResponse(BaseModel):
    """Response model for MCP status."""

    connected: bool
    session_id: str | None
    uptime: int
    last_heartbeat: str | None
    enabled: bool


@router.get("/status", status_code=status.HTTP_200_OK, response_model=MCPStatusResponse)
async def get_mcp_status(
    mcp_service: MCPService = Depends(get_mcp_service),
) -> MCPStatusResponse:
    """Get MCP connection status.

    Returns current status of MCP (Model Context Protocol) connection,
    including session ID, uptime, and last heartbeat timestamp.

    Args:
        mcp_service: MCP service dependency

    Returns:
        MCPStatusResponse with connection details
    """
    status_data = mcp_service.get_status()

    return MCPStatusResponse(
        connected=status_data["connected"],
        session_id=status_data["session_id"],
        uptime=status_data["uptime"],
        last_heartbeat=status_data["last_heartbeat"],
        enabled=status_data["enabled"],
    )
