"""
Service Category repository for data access.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import ServiceCategory
from repositories.base import BaseRepository


class ServiceCategoryRepository(BaseRepository[ServiceCategory]):
    """Repository for ServiceCategory model."""

    def __init__(self, db: AsyncSession):
        super().__init__(ServiceCategory, db)

    async def get_by_code(self, code: str) -> Optional[ServiceCategory]:
        """Get service category by code."""
        result = await self.db.execute(
            select(ServiceCategory).where(ServiceCategory.code == code)
        )
        return result.scalar_one_or_none()

    async def get_active_categories(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ServiceCategory]:
        """Get all active service categories."""
        query = (
            select(ServiceCategory)
            .where(ServiceCategory.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
