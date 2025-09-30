"""
Factory Boy factories for test data generation.
"""
import uuid
from datetime import datetime
from typing import Any, Dict

import factory
from factory import SubFactory, LazyAttribute, LazyFunction
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Client, Service, Project, ImplementationType, Contact, ServiceCategory


class AsyncSQLAlchemyModelFactory(factory.Factory):
    """Base factory for async SQLAlchemy models."""

    class Meta:
        abstract = True

    @classmethod
    async def create_async(cls, session: AsyncSession, **kwargs) -> Any:
        """Create an instance and save to database asynchronously."""
        instance = cls.build(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def create_batch_async(cls, session: AsyncSession, size: int, **kwargs) -> list:
        """Create multiple instances asynchronously."""
        instances = []
        for _ in range(size):
            instance = await cls.create_async(session, **kwargs)
            instances.append(instance)
        return instances


class ClientFactory(AsyncSQLAlchemyModelFactory):
    """Factory for Client model."""

    class Meta:
        model = Client

    id = LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Client {n}")
    business_domain = factory.Iterator([
        "healthcare", "finance", "education", "government",
        "technology", "retail", "manufacturing"
    ])
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class ServiceFactory(AsyncSQLAlchemyModelFactory):
    """Factory for Service model."""

    class Meta:
        model = Service

    id = LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Service {n}")
    description = factory.Faker("text", max_nb_chars=200)
    client_id = LazyFunction(uuid.uuid4)  # Will be overridden with real client
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class ImplementationTypeFactory(AsyncSQLAlchemyModelFactory):
    """Factory for ImplementationType model."""

    class Meta:
        model = ImplementationType

    id = LazyFunction(uuid.uuid4)
    name = factory.Iterator([
        "Custom Development", "Framework Integration", "API Development",
        "Database Design", "Frontend Development", "DevOps Setup"
    ])
    description = factory.Faker("text", max_nb_chars=100)
    created_at = LazyFunction(datetime.utcnow)


class ProjectFactory(AsyncSQLAlchemyModelFactory):
    """Factory for Project model."""

    class Meta:
        model = Project

    id = LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("text", max_nb_chars=300)
    service_id = LazyFunction(uuid.uuid4)  # Will be overridden with real service
    project_type = factory.Iterator([
        "web_application", "mobile_app", "api_service",
        "data_pipeline", "ml_model", "automation_script"
    ])
    implementation_type_id = None  # Optional field
    status = "draft"
    workflow_state = factory.LazyAttribute(lambda obj: {
        "phase": "initial",
        "progress": 0,
        "last_updated": datetime.utcnow().isoformat()
    })
    claude_code_path = factory.Faker("file_path", depth=3)
    embedding = None  # Vector field, will be set separately if needed
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class ContactFactory(AsyncSQLAlchemyModelFactory):
    """Factory for Contact model."""

    class Meta:
        model = Contact

    id = LazyFunction(uuid.uuid4)
    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"contact{n}@example.com")
    role = factory.Iterator([
        "Product Manager", "Engineering Manager", "CTO",
        "CEO", "Project Manager", "Technical Lead"
    ])
    phone = factory.Faker("phone_number")
    is_active = True
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class ServiceCategoryFactory(AsyncSQLAlchemyModelFactory):
    """Factory for ServiceCategory model."""

    class Meta:
        model = ServiceCategory

    id = LazyFunction(uuid.uuid4)
    code = factory.Sequence(lambda n: f"CAT{n}")
    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker("text", max_nb_chars=100)
    color = factory.Iterator(["#2563eb", "#dc2626", "#059669", "#7c3aed", "#ea580c"])
    is_active = True
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


# Helper functions for creating related objects
async def create_client_with_services(
    session: AsyncSession,
    service_count: int = 2,
    **client_kwargs
) -> tuple[Client, list[Service]]:
    """Create a client with associated services."""
    client = await ClientFactory.create_async(session, **client_kwargs)

    services = []
    for _ in range(service_count):
        service = await ServiceFactory.create_async(
            session,
            client_id=client.id
        )
        services.append(service)

    return client, services


async def create_service_with_projects(
    session: AsyncSession,
    project_count: int = 3,
    client_id: uuid.UUID = None,
    **service_kwargs
) -> tuple[Service, list[Project]]:
    """Create a service with associated projects."""
    if client_id is None:
        client = await ClientFactory.create_async(session)
        client_id = client.id

    service = await ServiceFactory.create_async(
        session,
        client_id=client_id,
        **service_kwargs
    )

    projects = []
    for _ in range(project_count):
        project = await ProjectFactory.create_async(
            session,
            service_id=service.id
        )
        projects.append(project)

    return service, projects


async def create_full_hierarchy(
    session: AsyncSession,
    service_count: int = 2,
    project_count: int = 2
) -> tuple[Client, list[Service], list[Project]]:
    """Create a complete client -> services -> projects hierarchy."""
    client = await ClientFactory.create_async(session)

    services = []
    all_projects = []

    for _ in range(service_count):
        service = await ServiceFactory.create_async(
            session,
            client_id=client.id
        )
        services.append(service)

        for _ in range(project_count):
            project = await ProjectFactory.create_async(
                session,
                service_id=service.id
            )
            all_projects.append(project)

    return client, services, all_projects