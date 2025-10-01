"""
Pytest configuration and fixtures.
"""
import asyncio
import pytest
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add apps/api to Python path for imports
api_path = Path(__file__).parent.parent / "apps" / "api"
sys.path.insert(0, str(api_path))

from core.database import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_session():
    """
    Create a fresh database session for each test.
    Uses a test database to avoid polluting production data.
    """
    # Use test database URL
    db_url = os.environ.get(
        'TEST_DATABASE_URL',
        'postgresql+asyncpg://agentlab:agentlab@localhost:5434/agentlab_test'
    )

    # Create engine
    engine = create_async_engine(db_url, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()

    # Clean up - drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
