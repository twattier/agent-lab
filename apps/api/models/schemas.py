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
    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DATA_PIPELINE = "data_pipeline"
    ML_MODEL = "ml_model"
    AUTOMATION_SCRIPT = "automation_script"


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


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


# Project schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: ProjectType
    claude_code_path: Optional[str] = Field(None, max_length=500)


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    service_id: uuid.UUID
    implementation_type_id: Optional[uuid.UUID] = None


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    implementation_type_id: Optional[uuid.UUID] = None
    status: Optional[ProjectStatus] = None
    workflow_state: Optional[Dict[str, Any]] = None
    claude_code_path: Optional[str] = Field(None, max_length=500)


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: uuid.UUID
    service_id: uuid.UUID
    implementation_type_id: Optional[uuid.UUID] = None
    status: ProjectStatus
    workflow_state: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Implementation Type schemas
class ImplementationTypeBase(BaseModel):
    """Base implementation type schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ImplementationTypeCreate(ImplementationTypeBase):
    """Implementation type creation schema."""
    pass


class ImplementationTypeResponse(ImplementationTypeBase):
    """Implementation type response schema."""
    id: uuid.UUID
    created_at: datetime

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