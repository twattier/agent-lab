"""Repository for ImplementationType model."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import ImplementationType


class ImplementationTypeRepository:
    """Repository for managing implementation types."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def list_implementation_types(
        self, is_active: Optional[bool] = True
    ) -> List[ImplementationType]:
        """
        List all implementation types with optional filtering.

        Args:
            is_active: Filter by active status (default: True)

        Returns:
            List of ImplementationType objects
        """
        query = select(ImplementationType)

        if is_active is not None:
            query = query.where(ImplementationType.is_active == is_active)

        query = query.order_by(ImplementationType.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_implementation_type_by_id(
        self, impl_type_id: uuid.UUID
    ) -> Optional[ImplementationType]:
        """
        Get a single implementation type by ID.

        Args:
            impl_type_id: UUID of the implementation type

        Returns:
            ImplementationType object or None if not found
        """
        query = select(ImplementationType).where(ImplementationType.id == impl_type_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_implementation_type_by_code(
        self, code: str
    ) -> Optional[ImplementationType]:
        """
        Get a single implementation type by code.

        Args:
            code: Code of the implementation type

        Returns:
            ImplementationType object or None if not found
        """
        query = select(ImplementationType).where(ImplementationType.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
