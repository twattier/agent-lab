"""
SQLAlchemy database models for AgentLab.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    JSON,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from core.database import Base


class Client(Base):
    """Client model representing DSI client organizations."""

    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_domain: Mapped[str] = mapped_column(
        Enum(
            "healthcare",
            "finance",
            "education",
            "government",
            "technology",
            "retail",
            "manufacturing",
            name="business_domain_enum"
        ),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    services: Mapped[List["Service"]] = relationship(
        "Service", back_populates="client", cascade="all, delete-orphan"
    )


class Service(Base):
    """Service model representing specific services under each client."""

    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    client: Mapped["Client"] = relationship("Client", back_populates="services")
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="service", cascade="all, delete-orphan"
    )
    service_contacts: Mapped[List["ServiceContact"]] = relationship(
        "ServiceContact", back_populates="service", cascade="all, delete-orphan"
    )
    category_assignments: Mapped[List["ServiceServiceCategory"]] = relationship(
        "ServiceServiceCategory", back_populates="service", cascade="all, delete-orphan"
    )


class Project(Base):
    """Project model with BMAD workflow state and pgvector support."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id"), nullable=False
    )
    project_type: Mapped[str] = mapped_column(
        Enum(
            "web_application",
            "mobile_app",
            "api_service",
            "data_pipeline",
            "ml_model",
            "automation_script",
            name="project_type_enum"
        ),
        nullable=False
    )
    implementation_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("implementation_types.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "draft",
            "planning",
            "in_progress",
            "review",
            "completed",
            "on_hold",
            "cancelled",
            name="project_status_enum"
        ),
        default="draft",
        nullable=False
    )
    workflow_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    claude_code_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Vector embedding for semantic search
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        Vector(1536), nullable=True  # OpenAI embedding dimension
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    service: Mapped["Service"] = relationship("Service", back_populates="projects")
    implementation_type: Mapped[Optional["ImplementationType"]] = relationship(
        "ImplementationType", back_populates="projects"
    )


class ImplementationType(Base):
    """Reference table for implementation types."""

    __tablename__ = "implementation_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="implementation_type"
    )


class Contact(Base):
    """Contact model for storing contact information."""

    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    service_contacts: Mapped[List["ServiceContact"]] = relationship(
        "ServiceContact", back_populates="contact", cascade="all, delete-orphan"
    )


class ServiceCategory(Base):
    """Reference table for service categories."""

    __tablename__ = "service_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    service_assignments: Mapped[List["ServiceServiceCategory"]] = relationship(
        "ServiceServiceCategory", back_populates="service_category", cascade="all, delete-orphan"
    )


class ServiceContact(Base):
    """Junction table linking services to contacts."""

    __tablename__ = "service_contacts"
    __table_args__ = (
        UniqueConstraint('service_id', 'contact_id', name='uq_service_contact'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), default="main", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    service: Mapped["Service"] = relationship("Service", back_populates="service_contacts")
    contact: Mapped["Contact"] = relationship("Contact", back_populates="service_contacts")


class ServiceServiceCategory(Base):
    """Junction table linking services to service categories."""

    __tablename__ = "service_service_categories"
    __table_args__ = (
        UniqueConstraint('service_id', 'service_category_id', name='uq_service_service_category'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    service_category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    service: Mapped["Service"] = relationship("Service", back_populates="category_assignments")
    service_category: Mapped["ServiceCategory"] = relationship("ServiceCategory", back_populates="service_assignments")