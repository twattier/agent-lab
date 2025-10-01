"""
SQLAlchemy database models for AgentLab.
"""
import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    Boolean,
    Integer,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from core.database import Base


class ProjectType(str, enum.Enum):
    """Project type enumeration."""
    NEW = "new"
    EXISTING = "existing"


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class WorkflowEventType(str, enum.Enum):
    """Workflow event type enumeration."""
    STAGE_ADVANCE = "stage_advance"
    GATE_APPROVED = "gate_approved"
    GATE_REJECTED = "gate_rejected"
    GATE_RESET = "gate_reset"
    REVIEWER_ASSIGNED = "reviewer_assigned"
    MANUAL_OVERRIDE = "manual_override"


class Language(str, enum.Enum):
    """Language enumeration for documents."""
    FRENCH = "fr"
    ENGLISH = "en"


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    PRD = "prd"
    ARCHITECTURE = "architecture"
    REQUIREMENTS = "requirements"
    FEEDBACK = "feedback"
    OTHER = "other"


class Client(Base):
    """Client model representing DSI client organizations."""

    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_domain: Mapped[str] = mapped_column(
        SQLEnum(
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
    """Project model with BMAD workflow state and lifecycle management."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_type: Mapped[str] = mapped_column(
        SQLEnum("new", "existing", name="project_type_enum", create_type=False), nullable=False, index=True
    )
    implementation_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("implementation_types.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        SQLEnum("draft", "active", "blocked", "completed", "archived", name="project_status_enum", create_type=False), nullable=False, default="draft", index=True
    )
    workflow_state: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default='{}')
    claude_code_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), insert_default=func.now(), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), insert_default=func.now(), onupdate=func.now(), server_default=func.now(), nullable=False
    )

    # Relationships
    service: Mapped["Service"] = relationship("Service", back_populates="projects")
    implementation_type: Mapped[Optional["ImplementationType"]] = relationship(
        "ImplementationType", back_populates="projects"
    )
    project_contacts: Mapped[List["ProjectContact"]] = relationship(
        "ProjectContact", back_populates="project", cascade="all, delete-orphan"
    )
    user_category_assignments: Mapped[List["ProjectServiceCategory"]] = relationship(
        "ProjectServiceCategory", back_populates="project", cascade="all, delete-orphan"
    )
    workflow_events: Mapped[List["WorkflowEvent"]] = relationship(
        "WorkflowEvent", back_populates="project", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan"
    )


class ImplementationType(Base):
    """Reference table for implementation types."""

    __tablename__ = "implementation_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
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
    project_contacts: Mapped[List["ProjectContact"]] = relationship(
        "ProjectContact", back_populates="contact", cascade="all, delete-orphan"
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
    project_assignments: Mapped[List["ProjectServiceCategory"]] = relationship(
        "ProjectServiceCategory", back_populates="service_category", cascade="all, delete-orphan"
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


class ProjectContact(Base):
    """Junction table linking projects to contacts."""

    __tablename__ = "project_contacts"
    __table_args__ = (
        UniqueConstraint('project_id', 'contact_id', 'contact_type', name='uq_project_contact'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_type: Mapped[str] = mapped_column(String(50), nullable=False, default="stakeholder")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="project_contacts")
    contact: Mapped["Contact"] = relationship("Contact", back_populates="project_contacts")


class ProjectServiceCategory(Base):
    """Junction table linking projects to service categories (target user categories)."""

    __tablename__ = "project_service_categories"
    __table_args__ = (
        UniqueConstraint('project_id', 'service_category_id', name='uq_project_service_category'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="user_category_assignments")
    service_category: Mapped["ServiceCategory"] = relationship("ServiceCategory", back_populates="project_assignments")


class WorkflowEvent(Base):
    """Workflow event audit trail for project workflow state changes."""

    __tablename__ = "workflow_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type: Mapped[WorkflowEventType] = mapped_column(
        SQLEnum(WorkflowEventType),
        nullable=False,
        index=True
    )
    from_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default='{}')
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="workflow_events")


class Document(Base):
    """Document model with version tracking and semantic search."""

    __tablename__ = "document"

    __table_args__ = (
        Index(
            'idx_document_vector',
            'content_vector',
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'content_vector': 'vector_cosine_ops'}
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    language: Mapped[Language] = mapped_column(
        SQLEnum(Language),
        nullable=False,
        default=Language.ENGLISH,
        index=True
    )
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType),
        nullable=False,
        index=True
    )
    content_vector: Mapped[Optional[str]] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="document",
        cascade="all, delete-orphan"
    )


class DocumentVersion(Base):
    """Document version history model."""

    __tablename__ = "document_version"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")


class Comment(Base):
    """Comment model for document feedback and discussions."""

    __tablename__ = "comment"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="comments")

# Story 3.1 & 3.2: Workflow and Gate Management Models

class WorkflowTemplate(Base):
    """Workflow template model for BMAD templates."""

    __tablename__ = "workflow_template"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    stages: Mapped[List["WorkflowStage"]] = relationship(
        "WorkflowStage", back_populates="template", cascade="all, delete-orphan"
    )
    gates: Mapped[List["WorkflowGate"]] = relationship(
        "WorkflowGate", back_populates="template", cascade="all, delete-orphan"
    )


class WorkflowStage(Base):
    """Workflow stage model for BMAD stages."""

    __tablename__ = "workflow_stage"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_template.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    stage_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    template: Mapped["WorkflowTemplate"] = relationship(
        "WorkflowTemplate", back_populates="stages"
    )


class WorkflowGate(Base):
    """Workflow gate model for stage transitions."""

    __tablename__ = "workflow_gate"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_template.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    gate_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stage_id: Mapped[str] = mapped_column(String(100), nullable=False)
    criteria: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default='pending'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    template: Mapped["WorkflowTemplate"] = relationship(
        "WorkflowTemplate", back_populates="gates"
    )
    reviewers: Mapped[List["GateReviewer"]] = relationship(
        "GateReviewer", back_populates="gate", cascade="all, delete-orphan"
    )


class GateReviewer(Base):
    """Gate reviewer assignment model."""

    __tablename__ = "gate_reviewer"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    gate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_gate.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reviewer_role: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    gate: Mapped["WorkflowGate"] = relationship(
        "WorkflowGate", back_populates="reviewers"
    )
    contact: Mapped["Contact"] = relationship("Contact")
