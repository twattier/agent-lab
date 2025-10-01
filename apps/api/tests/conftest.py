"""
Pytest configuration and fixtures for AgentLab API tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine

from main import app
from core.database import Base, get_db
from core.config import get_settings


# Test database URL - using port 5434 from docker-compose configuration
TEST_DATABASE_URL = "postgresql+asyncpg://agentlab:agentlab@localhost:5434/agentlab"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine for each test function.

    Using function scope to ensure each test has its own engine in the same event loop,
    preventing 'attached to a different loop' errors with pytest-asyncio.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_size=2,  # Smaller pool for function scope
        max_overflow=5,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Clean slate
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: dispose engine to close all connections properly
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with transaction rollback."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()


@pytest.fixture
async def test_session(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Alias for db_session for backward compatibility with Story 2.4 tests."""
    yield db_session


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for tests."""
    async def _override_get_db():
        yield db_session
    return _override_get_db


@pytest.fixture
async def test_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database dependency override."""
    from fastapi.testclient import TestClient
    from httpx import AsyncClient, ASGITransport

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.DEBUG = True
    settings.MCP_ENABLED = False  # Disable MCP for tests
    return settings


# Shared test data fixtures
@pytest.fixture
async def test_client_data(db_session: AsyncSession):
    """Create test client."""
    from repositories.client_repository import ClientRepository

    client_repo = ClientRepository(db_session)
    client = await client_repo.create(
        name="Test Client",
        business_domain="technology"
    )
    return client


@pytest.fixture
async def test_service_data(db_session: AsyncSession, test_client_data):
    """Create test service."""
    from repositories.service_repository import ServiceRepository

    service_repo = ServiceRepository(db_session)
    service = await service_repo.create(
        name="Test Service",
        description="Test service description",
        client_id=test_client_data.id
    )
    return service


@pytest.fixture
async def test_project_data(db_session: AsyncSession, test_service_data):
    """Create test project with initialized workflow."""
    from repositories.project_repository import ProjectRepository

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create_project({
        "name": "Test Project",
        "description": "Test project description",
        "service_id": test_service_data.id,
        "project_type": "new",
        "status": "active"
    })
    return project