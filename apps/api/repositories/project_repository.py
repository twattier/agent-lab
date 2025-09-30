"""
Project repository for data access operations.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import Project, Service
from repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_with_service(self, project_id: uuid.UUID) -> Optional[Project]:
        """Get project with associated service."""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.service))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_service_id(
        self,
        service_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """Get projects by service ID."""
        result = await self.db.execute(
            select(Project)
            .where(Project.service_id == service_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """Get projects by status."""
        result = await self.db.execute(
            select(Project)
            .where(Project.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_vector_similarity(
        self,
        query_vector: List[float],
        limit: int = 10,
        threshold: float = 0.8
    ) -> List[Project]:
        """Search projects by vector similarity using pgvector."""
        # Using raw SQL for pgvector similarity search
        query = text("""
            SELECT p.* FROM projects p
            WHERE p.embedding IS NOT NULL
            AND p.embedding <-> :query_vector < :threshold
            ORDER BY p.embedding <-> :query_vector
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "query_vector": str(query_vector),
                "threshold": 1 - threshold,  # Convert similarity to distance
                "limit": limit
            }
        )

        # Convert raw results to Project objects
        project_rows = result.fetchall()
        project_ids = [row[0] for row in project_rows]

        if not project_ids:
            return []

        # Fetch complete Project objects
        projects_result = await self.db.execute(
            select(Project).where(Project.id.in_(project_ids))
        )
        return list(projects_result.scalars().all())

    async def update_embedding(
        self,
        project_id: uuid.UUID,
        embedding: List[float]
    ) -> Optional[Project]:
        """Update project embedding vector."""
        await self.db.execute(
            text("UPDATE projects SET embedding = :embedding WHERE id = :project_id"),
            {"embedding": str(embedding), "project_id": str(project_id)}
        )
        await self.db.commit()
        return await self.get_by_id(project_id)