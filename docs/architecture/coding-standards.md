# Coding Standards

## Critical Fullstack Rules

1. **Type Safety First:** All data must be typed end-to-end from database to frontend
2. **Consistent Error Handling:** Use unified error response format across all API endpoints
3. **Component Composition:** Prefer composition over inheritance in both React and Python code
4. **Async/Await:** Use async patterns consistently for all I/O operations
5. **Validation Everywhere:** Validate data at API boundaries and form inputs using Pydantic/Zod
6. **Test Coverage:** Maintain >80% test coverage for business logic
7. **Documentation:** Every public function/component must have JSDoc/docstring
8. **Performance:** Optimize for sub-second response times on all user interactions

## Naming Conventions

### TypeScript/React
- **Components:** PascalCase (`ProjectCard`, `WorkflowStatus`)
- **Files:** kebab-case (`project-card.tsx`, `workflow-status.tsx`)
- **Variables/Functions:** camelCase (`projectData`, `handleSubmit`)
- **Constants:** UPPER_SNAKE_CASE (`API_BASE_URL`, `MAX_FILE_SIZE`)
- **Types/Interfaces:** PascalCase (`Project`, `WorkflowState`)

### Python
- **Classes:** PascalCase (`ProjectService`, `WorkflowEngine`)
- **Files/Modules:** snake_case (`project_service.py`, `workflow_engine.py`)
- **Functions/Variables:** snake_case (`create_project`, `workflow_state`)
- **Constants:** UPPER_SNAKE_CASE (`DATABASE_URL`, `MAX_RETRY_ATTEMPTS`)
- **Private Methods:** Leading underscore (`_validate_workflow`)

### Database
- **Tables:** snake_case (`projects`, `workflow_events`)
- **Columns:** snake_case (`created_at`, `workflow_state`)
- **Indexes:** Descriptive (`idx_projects_service_status`)
- **Foreign Keys:** Explicit (`service_id`, `project_id`)

## Code Organization Principles

### Frontend Structure
```typescript
// Component file structure
export interface ComponentProps {
  // Props definition
}

export function Component({ ...props }: ComponentProps) {
  // Hooks
  // Event handlers
  // Render logic
  return (
    // JSX
  );
}

// Export default for page components, named for reusable components
```

### Backend Structure
```python
# Service class structure
class ServiceClass:
    """Service description."""

    def __init__(self, dependencies):
        """Initialize with dependencies."""
        pass

    async def public_method(self, params) -> ReturnType:
        """Public method with clear return type."""
        # Input validation
        # Business logic
        # Return formatted result
        pass

    def _private_method(self):
        """Private helper method."""
        pass
```

## Import Organization

### TypeScript
```typescript
// External libraries
import React from 'react';
import { NextPage } from 'next';

// Internal packages (monorepo)
import { Project } from '@agentlab/types';
import { Button } from '@agentlab/ui';

// Relative imports (same app)
import { ProjectCard } from '../components/project-card';
import { useProjects } from '../hooks/use-projects';
```

### Python
```python
# Standard library
import asyncio
import logging
from typing import Optional, List

# Third-party packages
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Local imports
from models.project import Project, CreateProjectRequest
from services.project_service import ProjectService
```

---
[← Back to Development Workflow](development-workflow.md) | [Architecture Index](index.md) | [Next: Testing Strategy →](testing-strategy.md)