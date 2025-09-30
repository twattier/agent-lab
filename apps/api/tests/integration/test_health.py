"""
Integration tests for health check endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    """Test health check endpoint."""
    response = await test_client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "service" in data
    assert "version" in data

    assert data["service"] == "agentlab-api"
    assert data["version"] == "1.0.0"
    # Database status depends on test setup, could be healthy or unhealthy