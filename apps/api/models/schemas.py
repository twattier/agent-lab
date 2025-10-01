"""
Pydantic models for request/response schemas.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class BusinessDomain(str, Enum):
    """Business domain enumeration."""
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    GOVERNMENT = "government"
    TECHNOLOGY = "technology"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"


class ProjectType(str, Enum):
    """Project type enumeration."""
    NEW = "new"
    EXISTING = "existing"


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# Client schemas
class ClientBase(BaseModel):
    """Base client schema."""
    name: str = Field(..., min_length=1, max_length=255)
    business_domain: BusinessDomain


class ClientCreate(ClientBase):
    """Client creation schema."""
    pass


class ClientUpdate(BaseModel):
    """Client update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    business_domain: Optional[BusinessDomain] = None


class ClientResponse(ClientBase):
    """Client response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Service schemas
class ServiceBase(BaseModel):
    """Base service schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    """Service creation schema."""
    client_id: uuid.UUID


class ServiceUpdate(BaseModel):
    """Service update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ServiceResponse(ServiceBase):
    """Service response schema."""
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# WorkflowState schema for JSONB validation
class WorkflowState(BaseModel):
    """Workflow state schema for JSONB field."""
    currentStage: Optional[str] = None
    completedStages: List[str] = Field(default_factory=list)
    stageData: Dict[str, Any] = Field(default_factory=dict)
    lastTransition: Optional[datetime] = None


# Project schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    project_type: ProjectType


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    service_id: uuid.UUID
    implementation_type_id: Optional[uuid.UUID] = None


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[ProjectStatus] = None
    implementation_type_id: Optional[uuid.UUID] = None
    claude_code_path: Optional[str] = Field(None, max_length=500)


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: uuid.UUID
    service_id: uuid.UUID
    implementation_type_id: Optional[uuid.UUID] = None
    status: ProjectStatus
    workflow_state: Dict[str, Any]
    claude_code_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    """Project detail response with relationships."""
    service: Optional['ServiceResponse'] = None
    implementation_type: Optional['ImplementationTypeResponse'] = None
    contacts: List['ProjectContactResponse'] = Field(default_factory=list)
    user_categories: List['ServiceCategoryResponse'] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Implementation Type schemas
class ImplementationTypeBase(BaseModel):
    """Base implementation type schema."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class ImplementationTypeCreate(ImplementationTypeBase):
    """Implementation type creation schema."""
    pass


class ImplementationTypeResponse(ImplementationTypeBase):
    """Implementation type response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Standard API response schemas
class SuccessResponse(BaseModel):
    """Standard success response."""
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    service: str
    version: str


# Contact schemas
class ContactBase(BaseModel):
    """Base contact schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    role: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class ContactCreate(ContactBase):
    """Contact creation schema."""
    pass


class ContactUpdate(BaseModel):
    """Contact update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    role: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ContactResponse(ContactBase):
    """Contact response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ServiceCategory schemas
class ServiceCategoryBase(BaseModel):
    """Base service category schema."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9a-fA-F]{6}$')
    is_active: bool = True


class ServiceCategoryCreate(ServiceCategoryBase):
    """Service category creation schema."""
    pass


class ServiceCategoryUpdate(BaseModel):
    """Service category update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9a-fA-F]{6}$')
    is_active: Optional[bool] = None


class ServiceCategoryResponse(ServiceCategoryBase):
    """Service category response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ServiceContact schemas
class ServiceContactCreate(BaseModel):
    """Schema for assigning a contact to a service."""
    contact_id: uuid.UUID
    is_primary: bool = False
    relationship_type: str = Field("main", max_length=50)


class ServiceContactResponse(BaseModel):
    """Service contact association response."""
    id: uuid.UUID
    service_id: uuid.UUID
    contact_id: uuid.UUID
    is_primary: bool
    relationship_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ServiceServiceCategory schemas
class ServiceCategoryAssignmentCreate(BaseModel):
    """Schema for assigning a category to a service."""
    service_category_id: uuid.UUID


class ServiceCategoryAssignmentResponse(BaseModel):
    """Service category assignment response."""
    id: uuid.UUID
    service_id: uuid.UUID
    service_category_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ProjectContact schemas
class ProjectContactCreate(BaseModel):
    """Schema for assigning a contact to a project."""
    contact_id: uuid.UUID
    contact_type: str = Field("stakeholder", max_length=50)
    is_active: bool = True


class ProjectContactUpdate(BaseModel):
    """Schema for updating a project-contact relationship."""
    contact_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ProjectContactResponse(BaseModel):
    """Project contact association response."""
    id: uuid.UUID
    project_id: uuid.UUID
    contact_id: uuid.UUID
    contact_type: str
    is_active: bool
    created_at: datetime
    contact: Optional[ContactResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ProjectServiceCategory (User Category) schemas
class ProjectUserCategoryCreate(BaseModel):
    """Schema for assigning a user category to a project."""
    service_category_id: uuid.UUID


class ProjectUserCategoryResponse(BaseModel):
    """Project user category assignment response."""
    id: uuid.UUID
    project_id: uuid.UUID
    service_category_id: uuid.UUID
    created_at: datetime
    service_category: Optional[ServiceCategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)