# Backend Architecture

## Service Architecture

### Function Organization
The backend follows a layered architecture with clear separation between API controllers, business services, and data access:

```
apps/api/
├── api/                    # API layer
│   ├── v1/                # Versioned API endpoints
│   │   ├── projects.py    # Project management endpoints
│   │   ├── clients.py     # Client/service management
│   │   ├── documents.py   # Document operations
│   │   └── workflows.py   # Workflow management
│   └── middleware/        # Cross-cutting concerns
├── services/              # Business logic layer
│   ├── project_service.py # Project business logic
│   ├── document_service.py# Document processing
│   ├── workflow_service.py# BMAD workflow engine
│   └── mcp_service.py     # Claude Code integration
├── repositories/          # Data access layer
│   ├── base.py           # Base repository patterns
│   ├── project_repo.py   # Project data access
│   └── document_repo.py  # Document data access
├── models/               # Pydantic data models
├── core/                 # Core utilities and config
└── tests/               # Test suites
```

### Controller Template
```python
# api/v1/projects.py
from fastapi import APIRouter, Depends, HTTPException
from services.project_service import ProjectService
from models.project import Project, CreateProjectRequest

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=Project)
async def create_project(
    request: CreateProjectRequest,
    service: ProjectService = Depends()
) -> Project:
    """Create a new project with BMAD workflow initialization."""
    try:
        return await service.create_project(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Database Architecture

### Schema Design
PostgreSQL with pgvector extension provides both relational data management and vector similarity search capabilities for semantic document search.

### Data Access Layer
```python
# repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, obj: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def list(self, offset: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    async def update(self, id: str, updates: dict) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
```

## Authentication and Authorization

### Auth Flow
NextAuth.js integration with FastAPI for secure authentication:

1. **Frontend Authentication:** NextAuth.js handles OAuth providers and session management
2. **Token Validation:** FastAPI validates JWT tokens on each request
3. **Role-Based Access:** Middleware enforces role-based permissions
4. **Session Management:** Redis stores session data for scalability

### Middleware/Guards
```python
# core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> User:
    """Validate JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user

async def require_role(required_role: str):
    """Decorator for role-based access control."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Usage in endpoints
@router.post("/", dependencies=[Depends(require_role("product_owner"))])
async def create_project(request: CreateProjectRequest) -> Project:
    # Only product owners and admins can create projects
    pass
```

---
[← Back to Frontend Architecture](frontend-architecture.md) | [Architecture Index](index.md) | [Next: Project Structure →](project-structure.md)