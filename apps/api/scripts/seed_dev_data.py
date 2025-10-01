#!/usr/bin/env python3
"""
Development seed data script for AgentLab.

This script populates the database with realistic development data including:
- 5 sample clients across different business domains
- 15 sample services
- 25 sample projects with various states
- 10 sample contacts

Usage:
    python scripts/seed_dev_data.py [--reset]

Options:
    --reset: Drop all existing data before seeding
"""
import asyncio
import argparse
import sys
import uuid
from datetime import datetime, timedelta
import random
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
import os

def get_db_url():
    """Get database URL from environment."""
    url = os.environ.get('DATABASE_URL', 'postgresql://agentlab:agentlab@localhost:5434/agentlab')
    # Convert to asyncpg format
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    return url

from models.database import (
    Client, Service, Project, Contact, ImplementationType, ServiceCategory,
    ServiceContact, ProjectContact, ProjectServiceCategory, WorkflowEvent,
    ProjectType, ProjectStatus, WorkflowEventType, ServiceServiceCategory
)

try:
    from faker import Faker
    fake = Faker()
except ImportError:
    print("ERROR: faker library not installed. Install with: pip install faker")
    sys.exit(1)


class DevDataSeeder:
    """Development data seeder."""

    def __init__(self, session: AsyncSession, reset: bool = False):
        """Initialize seeder."""
        self.session = session
        self.reset = reset
        self.clients = []
        self.services = []
        self.projects = []
        self.contacts = []
        self.impl_types = []
        self.service_categories = []

    async def check_existing_data(self) -> bool:
        """Check if data already exists."""
        result = await self.session.execute(select(Client))
        existing_clients = result.scalars().all()
        return len(existing_clients) > 0

    async def clear_data(self):
        """Clear all existing data."""
        print("⚠️  Clearing all data...")
        # Delete in reverse dependency order
        await self.session.execute(delete(WorkflowEvent))
        await self.session.execute(delete(ProjectServiceCategory))
        await self.session.execute(delete(ProjectContact))
        await self.session.execute(delete(ServiceServiceCategory))
        await self.session.execute(delete(ServiceContact))
        await self.session.execute(delete(Project))
        await self.session.execute(delete(Service))
        await self.session.execute(delete(Client))
        await self.session.execute(delete(Contact))
        await self.session.commit()
        print("✅ Data cleared")

    async def load_reference_data(self):
        """Load reference data (implementation types and service categories)."""
        result = await self.session.execute(select(ImplementationType))
        self.impl_types = result.scalars().all()

        result = await self.session.execute(select(ServiceCategory))
        self.service_categories = result.scalars().all()

        if not self.impl_types or not self.service_categories:
            print("❌ ERROR: Reference data not found. Run migrations first.")
            sys.exit(1)

        print(f"📦 Loaded {len(self.impl_types)} implementation types and {len(self.service_categories)} service categories")

    async def seed_clients(self):
        """Seed client data."""
        print("🏢 Seeding clients...")
        domains = ['healthcare', 'finance', 'technology', 'manufacturing', 'education']

        for domain in domains:
            client = Client(
                id=uuid.uuid4(),
                name=fake.company(),
                business_domain=domain,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(client)
            self.clients.append(client)

        await self.session.commit()
        print(f"✅ Created {len(self.clients)} clients")

    async def seed_contacts(self):
        """Seed contact data."""
        print("👤 Seeding contacts...")
        for _ in range(10):
            contact = Contact(
                id=uuid.uuid4(),
                name=fake.name(),
                email=fake.email(),
                role=fake.job(),
                phone=f"+1{fake.numerify('##########')}",  # Simple US phone format
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(contact)
            self.contacts.append(contact)

        await self.session.commit()
        print(f"✅ Created {len(self.contacts)} contacts")

    async def seed_services(self):
        """Seed service data."""
        print("🔧 Seeding services...")
        for client in self.clients:
            num_services = random.randint(2, 4)
            for _ in range(num_services):
                service = Service(
                    id=uuid.uuid4(),
                    name=f"{client.name} - {fake.bs().title()}",
                    description=fake.catch_phrase(),
                    client_id=client.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.session.add(service)
                self.services.append(service)

                # Assign contacts to services
                num_contacts = random.randint(1, 3)
                assigned_contacts = random.sample(self.contacts, min(num_contacts, len(self.contacts)))
                for idx, contact in enumerate(assigned_contacts):
                    service_contact = ServiceContact(
                        id=uuid.uuid4(),
                        service_id=service.id,
                        contact_id=contact.id,
                        is_primary=(idx == 0),
                        relationship_type="main",
                        created_at=datetime.utcnow()
                    )
                    self.session.add(service_contact)

                # Assign categories to services
                num_categories = random.randint(1, 2)
                assigned_categories = random.sample(self.service_categories, min(num_categories, len(self.service_categories)))
                for category in assigned_categories:
                    ssc = ServiceServiceCategory(
                        id=uuid.uuid4(),
                        service_id=service.id,
                        service_category_id=category.id,
                        created_at=datetime.utcnow()
                    )
                    self.session.add(ssc)

        await self.session.commit()
        print(f"✅ Created {len(self.services)} services")

    async def seed_projects(self):
        """Seed project data."""
        print("📁 Seeding projects...")
        statuses = ['draft', 'active', 'blocked', 'completed', 'archived']
        stages = ['business_analysis', 'market_research', 'technical_design', 'development', 'deployment']

        for service in self.services:
            num_projects = random.randint(1, 2)
            for _ in range(num_projects):
                project_type = random.choice(['new', 'existing'])
                status = random.choice(statuses)
                impl_type = random.choice(self.impl_types) if random.random() > 0.3 else None
                current_stage = random.choice(stages)

                # Build workflow state
                stage_index = stages.index(current_stage)
                completed_stages = stages[:stage_index]

                workflow_state = {
                    'currentStage': current_stage,
                    'completedStages': completed_stages,
                    'stageData': {stage: {'completed': True} for stage in completed_stages},
                    'lastTransition': datetime.utcnow().isoformat(),
                    'gateStatus': 'pending'
                }

                project = Project(
                    id=uuid.uuid4(),
                    name=f"{fake.catch_phrase()} System",
                    description=fake.paragraph(nb_sentences=3),
                    service_id=service.id,
                    project_type=project_type,
                    implementation_type_id=impl_type.id if impl_type else None,
                    status=status,
                    workflow_state=workflow_state,
                    claude_code_path=f"/projects/{fake.slug()}",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                    updated_at=datetime.utcnow()
                )
                self.session.add(project)
                self.projects.append(project)

                # Assign contacts to projects
                num_contacts = random.randint(1, 2)
                assigned_contacts = random.sample(self.contacts, min(num_contacts, len(self.contacts)))
                for contact in assigned_contacts:
                    project_contact = ProjectContact(
                        id=uuid.uuid4(),
                        project_id=project.id,
                        contact_id=contact.id,
                        contact_type=random.choice(['stakeholder', 'owner', 'contributor']),
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    self.session.add(project_contact)

                # Assign user categories to projects
                num_categories = random.randint(1, 3)
                assigned_categories = random.sample(self.service_categories, min(num_categories, len(self.service_categories)))
                for category in assigned_categories:
                    psc = ProjectServiceCategory(
                        id=uuid.uuid4(),
                        project_id=project.id,
                        service_category_id=category.id,
                        created_at=datetime.utcnow()
                    )
                    self.session.add(psc)

                # Add workflow events for completed stages
                for idx, stage in enumerate(completed_stages):
                    event = WorkflowEvent(
                        id=uuid.uuid4(),
                        project_id=project.id,
                        event_type=WorkflowEventType.STAGE_ADVANCE,
                        from_stage=stages[idx - 1] if idx > 0 else None,
                        to_stage=stage,
                        user_id=uuid.uuid4(),  # Dummy user ID
                        event_metadata={'notes': f'Completed {stage}'},
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 90))
                    )
                    self.session.add(event)

        await self.session.commit()
        print(f"✅ Created {len(self.projects)} projects")

    async def run(self):
        """Run the seeding process."""
        print("\n🌱 AgentLab Development Data Seeder")
        print("=" * 50)

        # Check for existing data
        if not self.reset and await self.check_existing_data():
            print("❌ Data already exists. Use --reset to clear and reseed.")
            return

        if self.reset:
            await self.clear_data()

        # Load reference data
        await self.load_reference_data()

        # Seed all data
        await self.seed_clients()
        await self.seed_contacts()
        await self.seed_services()
        await self.seed_projects()

        print("\n✅ Development data seeding complete!")
        print(f"   - {len(self.clients)} clients")
        print(f"   - {len(self.contacts)} contacts")
        print(f"   - {len(self.services)} services")
        print(f"   - {len(self.projects)} projects")
        print()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Seed development data for AgentLab')
    parser.add_argument('--reset', action='store_true', help='Drop all data before seeding')
    args = parser.parse_args()

    # Get database URL
    db_url = get_db_url()
    print(f"📊 Connecting to database...")

    # Create async engine
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        seeder = DevDataSeeder(session, reset=args.reset)
        await seeder.run()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
