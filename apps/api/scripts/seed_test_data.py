#!/usr/bin/env python3
"""
Test seed data script for AgentLab automated tests.

Creates minimal, predictable test data for integration tests.
All IDs and data are deterministic for consistent testing.

Usage:
    python scripts/seed_test_data.py
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import UUID

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

def get_db_url():
    """Get database URL from environment."""
    url = os.environ.get('TEST_DATABASE_URL', 'postgresql://agentlab:agentlab@localhost:5434/agentlab_test')
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return url

from models.database import (
    Client, Service, Project, Contact, ImplementationType, ServiceCategory,
    ServiceContact, ProjectContact
)

# Deterministic UUIDs for testing
TEST_CLIENT_ID = UUID('00000000-0000-0000-0000-000000000001')
TEST_SERVICE_ID = UUID('00000000-0000-0000-0000-000000000002')
TEST_PROJECT_ID = UUID('00000000-0000-0000-0000-000000000003')
TEST_CONTACT_ID = UUID('00000000-0000-0000-0000-000000000004')


class TestDataSeeder:
    """Test data seeder with deterministic IDs."""

    def __init__(self, session: AsyncSession):
        """Initialize seeder."""
        self.session = session

    async def clear_data(self):
        """Clear all test data."""
        print("🧹 Clearing test data...")
        await self.session.execute(delete(ProjectContact))
        await self.session.execute(delete(ServiceContact))
        await self.session.execute(delete(Project))
        await self.session.execute(delete(Service))
        await self.session.execute(delete(Client))
        await self.session.execute(delete(Contact))
        await self.session.commit()
        print("✅ Test data cleared")

    async def seed_minimal_data(self):
        """Seed minimal test data."""
        print("📦 Seeding minimal test data...")

        # Create test client
        client = Client(
            id=TEST_CLIENT_ID,
            name="Test Client",
            business_domain="technology",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(client)

        # Create test contact
        contact = Contact(
            id=TEST_CONTACT_ID,
            name="Test Contact",
            email="test@example.com",
            role="Test Role",
            phone="+15551234567",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(contact)

        # Create test service
        service = Service(
            id=TEST_SERVICE_ID,
            name="Test Service",
            description="Test service description",
            client_id=TEST_CLIENT_ID,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(service)

        # Create test project
        project = Project(
            id=TEST_PROJECT_ID,
            name="Test Project",
            description="Test project description",
            service_id=TEST_SERVICE_ID,
            project_type="new",
            status="draft",
            workflow_state={
                "currentStage": "business_analysis",
                "completedStages": []
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(project)

        await self.session.commit()
        print("✅ Minimal test data seeded")
        print(f"   - Client ID: {TEST_CLIENT_ID}")
        print(f"   - Service ID: {TEST_SERVICE_ID}")
        print(f"   - Project ID: {TEST_PROJECT_ID}")
        print(f"   - Contact ID: {TEST_CONTACT_ID}")

    async def run(self):
        """Run the seeding process."""
        print("\n🧪 AgentLab Test Data Seeder")
        print("=" * 50)

        await self.clear_data()
        await self.seed_minimal_data()

        print("\n✅ Test data seeding complete!")
        print()


async def main():
    """Main function."""
    db_url = get_db_url()
    print(f"📊 Connecting to test database...")

    # Create async engine
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        seeder = TestDataSeeder(session)
        await seeder.run()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
