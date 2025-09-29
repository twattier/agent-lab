# Error Handling Strategy

## Error Flow

AgentLab implements comprehensive error handling across the full stack with consistent error formats, appropriate user messaging, and detailed logging for debugging.

### Error Classification
- **Validation Errors (400):** Invalid input data or business rule violations
- **Authentication Errors (401):** Missing or invalid authentication credentials
- **Authorization Errors (403):** Insufficient permissions for requested action
- **Not Found Errors (404):** Requested resource does not exist
- **Conflict Errors (409):** Resource state conflicts (e.g., workflow violations)
- **Server Errors (500):** Unexpected system errors and exceptions

## Error Response Format

### Standard API Error Response
```typescript
interface ApiError {
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable error message
    details?: {             // Additional error context
      field?: string;       // Field name for validation errors
      value?: any;          // Invalid value that caused error
      constraints?: string[]; // Validation constraints violated
    };
  };
  timestamp: string;        // ISO timestamp when error occurred
  path: string;            // API path where error occurred
  requestId: string;       // Unique request identifier for tracing
}
```

### Example Error Responses
```json
// Validation Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Project name must be between 3 and 100 characters",
    "details": {
      "field": "name",
      "value": "AB",
      "constraints": ["minLength", "maxLength"]
    }
  },
  "timestamp": "2025-09-29T10:30:00Z",
  "path": "/api/v1/projects",
  "requestId": "req_123456789"
}

// Business Logic Error
{
  "error": {
    "code": "WORKFLOW_VIOLATION",
    "message": "Cannot advance to market research without completing business analysis gate",
    "details": {
      "currentStage": "business_analysis",
      "requestedStage": "market_research",
      "requiredGate": "business_gate_approval"
    }
  },
  "timestamp": "2025-09-29T10:30:00Z",
  "path": "/api/v1/projects/123/workflow/advance",
  "requestId": "req_123456790"
}
```

## Frontend Error Handling

### Error Boundary Implementation
```typescript
// components/error-boundary.tsx
import React from 'react';
import { Alert, AlertDescription } from '@agentlab/ui';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error boundary caught error:', error, errorInfo);
    // Send to error reporting service
    reportError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert variant="destructive">
          <AlertDescription>
            Something went wrong. Please refresh the page or contact support.
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}
```

### API Error Handling Hook
```typescript
// hooks/use-error-handler.ts
import { useCallback } from 'react';
import { toast } from '@agentlab/ui';
import { ApiError } from '@agentlab/types';

export function useErrorHandler() {
  const handleError = useCallback((error: unknown) => {
    if (isApiError(error)) {
      // Handle structured API errors
      toast.error(error.error.message);

      // Log detailed error for debugging
      console.error('API Error:', {
        code: error.error.code,
        path: error.path,
        requestId: error.requestId,
        details: error.error.details
      });
    } else if (error instanceof Error) {
      // Handle generic JavaScript errors
      toast.error('An unexpected error occurred');
      console.error('Unexpected error:', error);
    } else {
      // Handle unknown error types
      toast.error('An unknown error occurred');
      console.error('Unknown error:', error);
    }
  }, []);

  return { handleError };
}

function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'error' in error &&
    typeof (error as any).error === 'object' &&
    'code' in (error as any).error &&
    'message' in (error as any).error
  );
}
```

## Backend Error Handling

### Custom Exception Classes
```python
# core/exceptions.py
from typing import Optional, Dict, Any

class AgentLabException(Exception):
    """Base exception for AgentLab application errors."""

    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ValidationError(AgentLabException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        constraints: Optional[list] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if constraints:
            details["constraints"] = constraints

        super().__init__(message, "VALIDATION_ERROR", details)

class WorkflowViolationError(AgentLabException):
    """Raised when workflow business rules are violated."""

    def __init__(
        self,
        message: str,
        current_stage: str,
        requested_stage: Optional[str] = None
    ):
        details = {
            "currentStage": current_stage,
            "requestedStage": requested_stage
        }
        super().__init__(message, "WORKFLOW_VIOLATION", details)

class ResourceNotFoundError(AgentLabException):
    """Raised when requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id '{resource_id}' not found"
        details = {
            "resourceType": resource_type,
            "resourceId": resource_id
        }
        super().__init__(message, "RESOURCE_NOT_FOUND", details)
```

### Exception Handler Registration
```python
# main.py - Register exception handlers
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exceptions import AgentLabException, ValidationError
import logging
import uuid

app = FastAPI()

@app.exception_handler(AgentLabException)
async def agentlab_exception_handler(request: Request, exc: AgentLabException):
    """Handle custom AgentLab exceptions."""
    request_id = str(uuid.uuid4())

    # Log error for debugging
    logging.error(
        f"AgentLab error [{request_id}]: {exc.code} - {exc.message}",
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "details": exc.details
        }
    )

    status_code = get_status_code_for_error(exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path),
            "requestId": request_id
        }
    )

def get_status_code_for_error(exc: AgentLabException) -> int:
    """Map exception types to HTTP status codes."""
    error_status_map = {
        "VALIDATION_ERROR": 400,
        "WORKFLOW_VIOLATION": 409,
        "RESOURCE_NOT_FOUND": 404,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403
    }
    return error_status_map.get(exc.code, 500)

# Usage in services
async def create_project(request: CreateProjectRequest) -> Project:
    if len(request.name) < 3:
        raise ValidationError(
            "Project name must be at least 3 characters",
            field="name",
            value=request.name,
            constraints=["minLength"]
        )

    # Business logic...
```

## Error Monitoring and Alerting

- **Production Errors:** Automatic alerts for 500-level errors
- **Rate Limiting:** Monitoring for unusual error patterns
- **User Impact:** Track error rates by user and endpoint
- **Debug Information:** Detailed logging with request correlation IDs
- **Error Trends:** Weekly reports on common error patterns

---
[← Back to Testing Strategy](testing-strategy.md) | [Architecture Index](index.md) | [Next: Security and Performance →](security-and-performance.md)