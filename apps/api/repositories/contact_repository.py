"""
Contact repository for data access.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Contact
from repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Repository for Contact model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Contact, db)

    async def get_by_email(self, email: str) -> Optional[Contact]:
        """Get contact by email address."""
        result = await self.db.execute(
            select(Contact).where(Contact.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_contacts(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contact]:
        """Get all active contacts."""
        query = select(Contact).where(Contact.is_active == True).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_by_name(
        self,
        name_query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contact]:
        """Search contacts by name (case-insensitive partial match)."""
        query = (
            select(Contact)
            .where(Contact.name.ilike(f"%{name_query}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
