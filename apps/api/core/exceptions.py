"""
Custom exceptions and error handlers for AgentLab API.
"""
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound


class AgentLabException(Exception):
    """Base exception for AgentLab."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundError(AgentLabException):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)}
        )


class DuplicateResourceError(AgentLabException):
    """Duplicate resource error."""

    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            details={"resource": resource, "field": field, "value": str(value)}
        )


class ValidationException(AgentLabException):
    """Validation error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details or {}
        )


class BusinessRuleViolationError(AgentLabException):
    """Business rule violation error."""

    def __init__(self, message: str, rule: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_RULE_VIOLATION",
            details={"rule": rule}
        )


# Exception handlers

async def agentlab_exception_handler(request: Request, exc: AgentLabException) -> JSONResponse:
    """Handle AgentLab custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors}
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle SQLAlchemy integrity errors."""
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    # Check for specific constraint violations
    if "unique constraint" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "code": "DUPLICATE_RESOURCE",
                    "message": "Resource already exists",
                    "details": {"constraint": "unique_constraint"}
                }
            }
        )
    elif "foreign key constraint" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "INVALID_REFERENCE",
                    "message": "Referenced resource does not exist",
                    "details": {"constraint": "foreign_key_constraint"}
                }
            }
        )
    elif "check constraint" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Data violates database constraints",
                    "details": {"constraint": "check_constraint"}
                }
            }
        )

    # Generic integrity error
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INTEGRITY_ERROR",
                "message": "Database integrity constraint violated",
                "details": {}
            }
        }
    )


async def not_found_handler(request: Request, exc: NoResultFound) -> JSONResponse:
    """Handle SQLAlchemy NoResultFound errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Requested resource not found",
                "details": {}
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    # Log the error for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {}
            }
        }
    )


def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app."""
    from fastapi.exceptions import RequestValidationError as FastAPIValidationError

    app.add_exception_handler(AgentLabException, agentlab_exception_handler)
    app.add_exception_handler(FastAPIValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(NoResultFound, not_found_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
