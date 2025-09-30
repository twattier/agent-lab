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


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

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
        async with session.begin():
            # Use savepoint for nested transactions
            async with session.begin_nested() as savepoint:
                yield session
                await savepoint.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for tests."""
    async def _override_get_db():
        yield db_session
    return _override_get_db


@pytest.fixture
async def test_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database dependency override."""
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
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