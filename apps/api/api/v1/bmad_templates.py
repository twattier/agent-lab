"""BMAD Template Management API endpoints."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from services.bmad_template_service import BMAdTemplateService, WorkflowTemplate


router = APIRouter(prefix="/bmad/templates", tags=["bmad-templates"])


class TemplateImportRequest(BaseModel):
    """Request model for template import."""

    template_path: str
    strict_validation: bool = True


class TemplateImportResponse(BaseModel):
    """Response model for template import."""

    success: bool
    template: WorkflowTemplate | None = None
    errors: list[str] = []


@router.post("/import", status_code=status.HTTP_201_CREATED, response_model=TemplateImportResponse)
async def import_template(request: TemplateImportRequest) -> TemplateImportResponse:
    """Import BMAD workflow template from filesystem.

    Args:
        request: Template import request with file path and validation settings

    Returns:
        TemplateImportResponse with imported template or errors

    Raises:
        HTTPException: 400 for validation errors, 500 for unexpected errors
    """
    try:
        # Initialize service
        service = BMAdTemplateService()

        # Import template
        file_path = Path(request.template_path)
        workflow_template, errors = service.import_template(
            file_path, request.strict_validation
        )

        # Handle validation errors
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Template validation failed",
                    "errors": errors,
                },
            )

        # Return successful response
        return TemplateImportResponse(
            success=True,
            template=workflow_template,
            errors=[],
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Internal server error during template import",
                "error": str(e),
            },
        )
