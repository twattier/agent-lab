"""
Mock MCP Server

This module provides a mock implementation of the Claude Code MCP server
for testing AgentLab's MCP integration without requiring a running MCP server.
"""

from .mcp_server_mock import MockMCPServer

__all__ = ["MockMCPServer"]
