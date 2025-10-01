"""
Comment repository for database operations.
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Comment


class CommentRepository:
    """Repository for comment database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_comment(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
        line_number: Optional[int] = None
    ) -> Comment:
        """
        Create a new comment.

        Args:
            document_id: Document ID
            user_id: User ID
            content: Comment content
            line_number: Optional line number for line-specific comments

        Returns:
            Created comment
        """
        comment = Comment(
            id=uuid.uuid4(),
            document_id=document_id,
            user_id=user_id,
            content=content,
            line_number=line_number,
            resolved=False
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_by_document_id(
        self,
        document_id: uuid.UUID,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comment]:
        """
        Get comments for a document.

        Args:
            document_id: Document ID
            resolved: Optional filter for resolved status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of comments ordered by created_at DESC
        """
        query = select(Comment).where(Comment.document_id == document_id)

        if resolved is not None:
            query = query.where(Comment.resolved == resolved)

        query = query.order_by(Comment.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_resolved_status(
        self,
        comment_id: uuid.UUID,
        resolved: bool
    ) -> Optional[Comment]:
        """
        Update comment resolved status.

        Args:
            comment_id: Comment ID
            resolved: New resolved status

        Returns:
            Updated comment or None if not found
        """
        result = await self.db.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment:
            return None

        comment.resolved = resolved
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete_comment(self, comment_id: uuid.UUID) -> bool:
        """
        Delete comment by ID.

        Args:
            comment_id: Comment ID

        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()

        if not comment:
            return False

        await self.db.delete(comment)
        await self.db.commit()
        return True
