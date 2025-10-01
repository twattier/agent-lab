"""
Audit log query endpoints.
"""
import uuid
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, text
from pydantic import BaseModel

from core.database import get_db

router = APIRouter()


class AuditLogEntry(BaseModel):
    """Audit log entry response."""
    id: uuid.UUID
    table_name: str
    record_id: uuid.UUID
    action: str
    user_id: Optional[uuid.UUID]
    old_values: Optional[dict]
    new_values: Optional[dict]
    changed_fields: Optional[List[str]]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    """Paginated audit log response."""
    total: int
    page: int
    page_size: int
    entries: List[AuditLogEntry]


@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    record_id: Optional[uuid.UUID] = Query(None, description="Filter by record ID"),
    action: Optional[str] = Query(None, description="Filter by action (INSERT, UPDATE, DELETE)"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """
    Query audit logs with filtering and pagination.

    Supports filtering by:
    - table_name: Table that was modified
    - record_id: ID of the record that was modified
    - action: Type of action (INSERT, UPDATE, DELETE)
    - user_id: User who performed the action
    - start_date: Start of date range
    - end_date: End of date range
    """
    # Build filter conditions
    conditions = []

    if table_name:
        conditions.append(text("table_name = :table_name"))
    if record_id:
        conditions.append(text("record_id = :record_id"))
    if action:
        conditions.append(text("action = :action"))
    if user_id:
        conditions.append(text("user_id = :user_id"))
    if start_date:
        conditions.append(text("timestamp >= :start_date"))
    if end_date:
        conditions.append(text("timestamp <= :end_date"))

    # Build parameters
    params = {}
    if table_name:
        params["table_name"] = table_name
    if record_id:
        params["record_id"] = str(record_id)
    if action:
        params["action"] = action
    if user_id:
        params["user_id"] = str(user_id)
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    # Build WHERE clause
    where_clause = " AND ".join(str(c) for c in conditions) if conditions else "1=1"

    # Get total count
    count_query = text(f"SELECT COUNT(*) FROM audit_log WHERE {where_clause}")
    count_result = await db.execute(count_query, params)
    total = count_result.scalar() or 0

    # Get paginated results
    offset = (page - 1) * page_size
    query = text(f"""
        SELECT * FROM audit_log
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT :limit OFFSET :offset
    """)
    params["limit"] = page_size
    params["offset"] = offset

    result = await db.execute(query, params)
    rows = result.mappings().all()

    # Convert to Pydantic models
    entries = [
        AuditLogEntry(
            id=row["id"],
            table_name=row["table_name"],
            record_id=row["record_id"],
            action=row["action"],
            user_id=row["user_id"],
            old_values=row["old_values"],
            new_values=row["new_values"],
            changed_fields=row["changed_fields"],
            timestamp=row["timestamp"],
            ip_address=row["ip_address"],
            user_agent=row["user_agent"]
        )
        for row in rows
    ]

    return AuditLogResponse(
        total=total,
        page=page,
        page_size=page_size,
        entries=entries
    )


@router.get("/audit-logs/record/{record_id}", response_model=List[AuditLogEntry])
async def get_record_audit_history(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete audit history for a specific record.

    Returns all audit log entries for the given record ID, ordered by timestamp.
    """
    query = text("""
        SELECT * FROM audit_log
        WHERE record_id = :record_id
        ORDER BY timestamp DESC
    """)

    result = await db.execute(query, {"record_id": str(record_id)})
    rows = result.mappings().all()

    return [
        AuditLogEntry(
            id=row["id"],
            table_name=row["table_name"],
            record_id=row["record_id"],
            action=row["action"],
            user_id=row["user_id"],
            old_values=row["old_values"],
            new_values=row["new_values"],
            changed_fields=row["changed_fields"],
            timestamp=row["timestamp"],
            ip_address=row["ip_address"],
            user_agent=row["user_agent"]
        )
        for row in rows
    ]


@router.get("/audit-logs/stats")
async def get_audit_stats(
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit log statistics.

    Returns summary statistics for the specified number of days.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    query = text("""
        SELECT
            COUNT(*) as total_entries,
            COUNT(DISTINCT table_name) as tables_modified,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(CASE WHEN action = 'INSERT' THEN 1 ELSE 0 END) as inserts,
            SUM(CASE WHEN action = 'UPDATE' THEN 1 ELSE 0 END) as updates,
            SUM(CASE WHEN action = 'DELETE' THEN 1 ELSE 0 END) as deletes
        FROM audit_log
        WHERE timestamp >= :start_date
    """)

    result = await db.execute(query, {"start_date": start_date})
    row = result.mappings().one()

    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "total_entries": row["total_entries"],
        "tables_modified": row["tables_modified"],
        "unique_users": row["unique_users"],
        "actions": {
            "inserts": row["inserts"],
            "updates": row["updates"],
            "deletes": row["deletes"]
        }
    }
