"""
Data export endpoints.
"""
import csv
import json
import io
from typing import Literal
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from models.database import Client, Service, Project, Contact

router = APIRouter()


@router.get("/export/clients")
async def export_clients(
    format: Literal["csv", "json"] = Query("csv", description="Export format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all clients.

    Supports CSV and JSON formats.
    """
    result = await db.execute(select(Client))
    clients = result.scalars().all()

    if format == "json":
        data = [
            {
                "id": str(client.id),
                "name": client.name,
                "business_domain": client.business_domain,
                "created_at": client.created_at.isoformat(),
                "updated_at": client.updated_at.isoformat()
            }
            for client in clients
        ]
        return StreamingResponse(
            io.StringIO(json.dumps(data, indent=2)),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=clients.json"}
        )

    # CSV format
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "business_domain", "created_at", "updated_at"])
    writer.writeheader()

    for client in clients:
        writer.writerow({
            "id": str(client.id),
            "name": client.name,
            "business_domain": client.business_domain,
            "created_at": client.created_at.isoformat(),
            "updated_at": client.updated_at.isoformat()
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients.csv"}
    )


@router.get("/export/projects")
async def export_projects(
    format: Literal["csv", "json"] = Query("csv", description="Export format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all projects.

    Supports CSV and JSON formats.
    """
    result = await db.execute(select(Project))
    projects = result.scalars().all()

    if format == "json":
        data = [
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "service_id": str(project.service_id),
                "project_type": project.project_type,
                "status": project.status,
                "workflow_state": project.workflow_state,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            }
            for project in projects
        ]
        return StreamingResponse(
            io.StringIO(json.dumps(data, indent=2)),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=projects.json"}
        )

    # CSV format
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "name", "description", "service_id", "project_type", "status", "created_at", "updated_at"]
    )
    writer.writeheader()

    for project in projects:
        writer.writerow({
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "service_id": str(project.service_id),
            "project_type": project.project_type,
            "status": project.status,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=projects.csv"}
    )


@router.get("/export/contacts")
async def export_contacts(
    format: Literal["csv", "json"] = Query("csv", description="Export format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all contacts.

    Supports CSV and JSON formats.
    """
    result = await db.execute(select(Contact))
    contacts = result.scalars().all()

    if format == "json":
        data = [
            {
                "id": str(contact.id),
                "name": contact.name,
                "email": contact.email,
                "role": contact.role,
                "phone": contact.phone,
                "is_active": contact.is_active,
                "created_at": contact.created_at.isoformat(),
                "updated_at": contact.updated_at.isoformat()
            }
            for contact in contacts
        ]
        return StreamingResponse(
            io.StringIO(json.dumps(data, indent=2)),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=contacts.json"}
        )

    # CSV format
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "name", "email", "role", "phone", "is_active", "created_at", "updated_at"]
    )
    writer.writeheader()

    for contact in contacts:
        writer.writerow({
            "id": str(contact.id),
            "name": contact.name,
            "email": contact.email,
            "role": contact.role,
            "phone": contact.phone,
            "is_active": contact.is_active,
            "created_at": contact.created_at.isoformat(),
            "updated_at": contact.updated_at.isoformat()
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"}
    )
