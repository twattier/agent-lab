"""
Client repository for data access operations.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import Client, Service
from repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Repository for Client operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Client, db)

    async def get_with_services(self, client_id: uuid.UUID) -> Optional[Client]:
        """Get client with all associated services."""
        result = await self.db.execute(
            select(Client)
            .options(selectinload(Client.services))
            .where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def get_by_business_domain(
        self,
        business_domain: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Get clients by business domain."""
        result = await self.db.execute(
            select(Client)
            .where(Client.business_domain == business_domain)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_name(
        self,
        name_pattern: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Search clients by name pattern."""
        result = await self.db.execute(
            select(Client)
            .where(Client.name.ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())