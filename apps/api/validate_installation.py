#!/usr/bin/env python3
"""
Installation and integration validation script for AgentLab API.
"""
import asyncio
import importlib
import sys
from typing import List, Tuple


def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all critical imports."""
    results = []

    imports_to_test = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("sqlalchemy", "ORM framework"),
        ("asyncpg", "Async PostgreSQL driver"),
        ("psycopg2", "Sync PostgreSQL driver"),
        ("alembic", "Database migrations"),
        ("pgvector", "Vector similarity search"),
        ("redis", "Redis client"),
        ("httpx", "HTTP client"),
        ("pytest", "Testing framework"),
        ("factory", "Test data factories"),
    ]

    for module_name, description in imports_to_test:
        try:
            importlib.import_module(module_name)
            results.append((module_name, True, description))
        except ImportError as e:
            results.append((module_name, False, f"{description} - Error: {e}"))

    return results


def test_application_imports() -> List[Tuple[str, bool, str]]:
    """Test application-specific imports."""
    results = []

    app_imports = [
        ("main", "FastAPI application entry point"),
        ("core.config", "Configuration management"),
        ("core.database", "Database configuration"),
        ("models.database", "Database models"),
        ("models.schemas", "Pydantic schemas"),
        ("api.v1.health", "Health check endpoints"),
        ("api.v1.clients", "Client API endpoints"),
        ("api.v1.services", "Service API endpoints"),
        ("api.v1.projects", "Project API endpoints"),
        ("repositories.base", "Base repository pattern"),
        ("repositories.client_repository", "Client repository"),
        ("repositories.service_repository", "Service repository"),
        ("repositories.project_repository", "Project repository"),
        ("services.mcp_service", "MCP service"),
    ]

    for module_name, description in app_imports:
        try:
            importlib.import_module(module_name)
            results.append((module_name, True, description))
        except ImportError as e:
            results.append((module_name, False, f"{description} - Error: {e}"))

    return results


async def test_fastapi_app():
    """Test FastAPI application creation."""
    try:
        from main import app

        # Test basic app properties
        assert app.title == "AgentLab API"
        assert app.version == "1.0.0"
        assert app.openapi_url == "/api/v1/openapi.json"

        # Test routes are registered
        route_paths = [route.path for route in app.routes]
        expected_paths = [
            "/api/v1/health",
            "/api/v1/clients",
            "/api/v1/services",
            "/api/v1/projects"
        ]

        for expected_path in expected_paths:
            if not any(expected_path in path for path in route_paths):
                return False, f"Missing route: {expected_path}"

        return True, "FastAPI application configured correctly"

    except Exception as e:
        return False, f"FastAPI app test failed: {e}"


async def test_database_models():
    """Test database models can be imported and instantiated."""
    try:
        from models.database import Client, Service, Project, ImplementationType
        import uuid
        from datetime import datetime

        # Test Client model
        client = Client(
            id=uuid.uuid4(),
            name="Test Client",
            business_domain="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert client.name == "Test Client"

        # Test Service model
        service = Service(
            id=uuid.uuid4(),
            name="Test Service",
            client_id=client.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert service.name == "Test Service"

        # Test Project model
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            service_id=service.id,
            project_type="web_application",
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert project.name == "Test Project"

        return True, "Database models working correctly"

    except Exception as e:
        return False, f"Database models test failed: {e}"


async def test_pydantic_schemas():
    """Test Pydantic schemas validation."""
    try:
        from models.schemas import ClientCreate, ServiceCreate, ProjectCreate

        # Test ClientCreate schema
        client_data = ClientCreate(
            name="Test Client",
            business_domain="technology"
        )
        assert client_data.name == "Test Client"

        # Test ServiceCreate schema
        service_data = ServiceCreate(
            name="Test Service",
            client_id="123e4567-e89b-12d3-a456-426614174000"
        )
        assert service_data.name == "Test Service"

        # Test ProjectCreate schema
        project_data = ProjectCreate(
            name="Test Project",
            service_id="123e4567-e89b-12d3-a456-426614174000",
            project_type="web_application"
        )
        assert project_data.name == "Test Project"

        return True, "Pydantic schemas validation working"

    except Exception as e:
        return False, f"Pydantic schemas test failed: {e}"


async def test_mcp_service():
    """Test MCP service can be instantiated."""
    try:
        from services.mcp_service import MCPService, MCPMessage

        # Test MCPService instantiation
        mcp_service = MCPService()
        assert mcp_service.connected is False

        # Test MCPMessage creation
        message = MCPMessage(
            type="test",
            data={"key": "value"},
            project_id="test-project"
        )
        assert message.type == "test"
        assert message.data["key"] == "value"

        return True, "MCP service components working"

    except Exception as e:
        return False, f"MCP service test failed: {e}"


def print_results(title: str, results: List[Tuple[str, bool, str]]):
    """Print test results in a formatted way."""
    print(f"\n{title}")
    print("=" * len(title))

    passed = 0
    failed = 0

    for name, success, description in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} {name:30} - {description}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


async def main():
    """Run all validation tests."""
    print("AgentLab API Installation Validation")
    print("=" * 40)

    # Test package imports
    import_results = test_imports()
    imports_ok = print_results("Package Imports", import_results)

    # Test application imports
    app_import_results = test_application_imports()
    app_imports_ok = print_results("Application Imports", app_import_results)

    # Test application components
    component_tests = [
        ("FastAPI Application", *await test_fastapi_app()),
        ("Database Models", *await test_database_models()),
        ("Pydantic Schemas", *await test_pydantic_schemas()),
        ("MCP Service", *await test_mcp_service()),
    ]

    components_ok = print_results("Component Tests", component_tests)

    # Overall result
    print("\nOverall Validation Result")
    print("=" * 25)

    all_passed = imports_ok and app_imports_ok and components_ok

    if all_passed:
        print("✓ ALL TESTS PASSED - Installation is valid and ready for use!")
        print("\nNext steps:")
        print("1. Start PostgreSQL database (if not running)")
        print("2. Run database migrations: alembic upgrade head")
        print("3. Start the API server: uvicorn main:app --reload")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))