"""
Service repository for data access operations.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import Service, Client, Project
from repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    """Repository for Service operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Service, db)

    async def get_with_projects(self, service_id: uuid.UUID) -> Optional[Service]:
        """Get service with all associated projects."""
        result = await self.db.execute(
            select(Service)
            .options(selectinload(Service.projects))
            .where(Service.id == service_id)
        )
        return result.scalar_one_or_none()

    async def get_by_client_id(
        self,
        client_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Service]:
        """Get services by client ID."""
        result = await self.db.execute(
            select(Service)
            .where(Service.client_id == client_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_name_and_client(
        self,
        name_pattern: str,
        client_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Service]:
        """Search services by name pattern within a specific client."""
        result = await self.db.execute(
            select(Service)
            .where(
                Service.client_id == client_id,
                Service.name.ilike(f"%{name_pattern}%")
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())