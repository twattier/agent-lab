# Data Models

## Client
**Purpose:** Represents DSI's client organizations in the two-level hierarchy (Client → Service)

**Key Attributes:**
- id: UUID - Unique identifier
- name: string - Client organization name
- businessDomain: enum - Business domain classification
- createdAt: DateTime - Record creation timestamp
- updatedAt: DateTime - Last modification timestamp

### TypeScript Interface
```typescript
interface Client {
  id: string;
  name: string;
  businessDomain: BusinessDomain;
  services: Service[];
  createdAt: Date;
  updatedAt: Date;
}

enum BusinessDomain {
  HEALTHCARE = 'healthcare',
  FINANCE = 'finance',
  TECHNOLOGY = 'technology',
  MANUFACTURING = 'manufacturing',
  EDUCATION = 'education',
  OTHER = 'other'
}
```

### Relationships
- Has many Services (one-to-many)
- Has many Projects through Services (one-to-many-through)

## Contact
**Purpose:** Represents contact persons associated with services and projects

**Key Attributes:**
- id: UUID - Unique identifier
- name: string - Contact person's name
- email: string - Contact email address (unique)
- role: string - Business role/title
- phone: string - Phone number (optional)
- isActive: boolean - Contact status

### TypeScript Interface
```typescript
interface Contact {
  id: string;
  name: string;
  email: string;
  role?: string;
  phone?: string;
  isActive: boolean;
  serviceContacts: ServiceContact[];
  projectContacts: ProjectContact[];
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Has many ServiceContacts (one-to-many)
- Has many ProjectContacts (one-to-many)

## ServiceCategory
**Purpose:** Reference table for service and project categorization

**Key Attributes:**
- id: UUID - Unique identifier
- code: string - Unique category code
- name: string - Display name
- description: string - Category description
- color: string - Hex color for UI display
- isActive: boolean - Category status

### TypeScript Interface
```typescript
interface ServiceCategory {
  id: string;
  code: string;
  name: string;
  description?: string;
  color?: string;
  isActive: boolean;
  serviceAssignments: ServiceServiceCategory[];
  projectAssignments: ProjectServiceCategory[];
  createdAt: Date;
  updatedAt: Date;
}

enum ServiceCategoryCode {
  SALES = 'SALES',
  HR = 'HR',
  FINANCE = 'FINANCE',
  OPERATIONS = 'OPERATIONS',
  CUSTOMER_SERVICE = 'CUSTOMER_SERVICE',
  IT = 'IT',
  LEGAL = 'LEGAL',
  PRODUCT = 'PRODUCT',
  EXECUTIVE = 'EXECUTIVE'
}
```

### Relationships
- Has many ServiceServiceCategory (one-to-many)
- Has many ProjectServiceCategory (one-to-many)

## ImplementationType
**Purpose:** Reference table for project implementation approaches

**Key Attributes:**
- id: UUID - Unique identifier
- code: string - Unique implementation type code
- name: string - Display name
- description: string - Implementation description
- isActive: boolean - Type status

### TypeScript Interface
```typescript
interface ImplementationType {
  id: string;
  code: string;
  name: string;
  description?: string;
  isActive: boolean;
  projects: Project[];
  createdAt: Date;
  updatedAt: Date;
}

enum ImplementationTypeCode {
  RAG = 'RAG',
  AGENTIC = 'AGENTIC',
  AUTOMATON = 'AUTOMATON',
  CHATBOT = 'CHATBOT',
  ANALYTICS = 'ANALYTICS',
  RECOMMENDATION = 'RECOMMENDATION'
}
```

### Relationships
- Has many Projects (one-to-many)

## Service
**Purpose:** Represents specific services under each client in the hierarchy

**Key Attributes:**
- id: UUID - Unique identifier
- name: string - Service name
- description: string - Service description
- clientId: UUID - Foreign key to Client

### TypeScript Interface
```typescript
interface Service {
  id: string;
  name: string;
  description?: string;
  clientId: string;
  client: Client;
  projects: Project[];
  serviceContacts: ServiceContact[];
  categoryAssignments: ServiceServiceCategory[];
  createdAt: Date;
  updatedAt: Date;
}
```

### Relationships
- Belongs to Client (many-to-one)
- Has many Projects (one-to-many)
- Has many ServiceContacts (one-to-many)
- Has many ServiceServiceCategory (one-to-many)

## Project
**Purpose:** Core entity representing individual projects with BMAD workflow state

**Key Attributes:**
- id: UUID - Unique identifier
- name: string - Project name
- description: string - Project description
- serviceId: UUID - Foreign key to Service
- projectType: enum - New/existing project classification
- implementationTypeId: UUID - Foreign key to ImplementationType
- status: enum - Current project status
- workflowState: JSON - Current BMAD workflow position
- claudeCodePath: string - Path to Claude Code project

### TypeScript Interface
```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  serviceId: string;
  projectType: ProjectType;
  implementationTypeId?: string;
  status: ProjectStatus;
  workflowState: WorkflowState;
  claudeCodePath?: string;
  service: Service;
  implementationType?: ImplementationType;
  documents: Document[];
  workflowHistory: WorkflowEvent[];
  projectContacts: ProjectContact[];
  userCategoryAssignments: ProjectServiceCategory[];
  createdAt: Date;
  updatedAt: Date;
}

enum ProjectType {
  NEW = 'new',
  EXISTING = 'existing'
}

enum ProjectStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  BLOCKED = 'blocked',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

interface WorkflowState {
  currentStage: string;
  completedStages: string[];
  stageData: Record<string, any>;
  lastTransition: Date;
}
```

### Relationships
- Belongs to Service (many-to-one)
- Belongs to ImplementationType (many-to-one, optional)
- Has many Documents (one-to-many)
- Has many WorkflowEvents (one-to-many)
- Has many ProjectContacts (one-to-many)
- Has many ProjectServiceCategory (one-to-many)

## Document
**Purpose:** Manages project documents with versioning and change tracking

**Key Attributes:**
- id: UUID - Unique identifier
- projectId: UUID - Foreign key to Project
- name: string - Document name
- content: text - Markdown content
- contentHash: string - Content hash for change detection
- version: integer - Document version number
- language: enum - Document language (French/English)
- documentType: enum - Type classification

### TypeScript Interface
```typescript
interface Document {
  id: string;
  projectId: string;
  name: string;
  content: string;
  contentHash: string;
  version: number;
  language: Language;
  documentType: DocumentType;
  project: Project;
  versions: DocumentVersion[];
  comments: Comment[];
  createdAt: Date;
  updatedAt: Date;
}

enum Language {
  FRENCH = 'fr',
  ENGLISH = 'en'
}

enum DocumentType {
  PRD = 'prd',
  ARCHITECTURE = 'architecture',
  REQUIREMENTS = 'requirements',
  FEEDBACK = 'feedback',
  OTHER = 'other'
}
```

### Relationships
- Belongs to Project (many-to-one)
- Has many DocumentVersions (one-to-many)
- Has many Comments (one-to-many)

## WorkflowEvent
**Purpose:** Audit trail for BMAD workflow state changes and gate approvals

**Key Attributes:**
- id: UUID - Unique identifier
- projectId: UUID - Foreign key to Project
- eventType: enum - Type of workflow event
- fromStage: string - Previous workflow stage
- toStage: string - New workflow stage
- userId: UUID - User who triggered event
- metadata: JSON - Additional event data
- timestamp: DateTime - When event occurred

### TypeScript Interface
```typescript
interface WorkflowEvent {
  id: string;
  projectId: string;
  eventType: WorkflowEventType;
  fromStage?: string;
  toStage: string;
  userId: string;
  metadata: Record<string, any>;
  timestamp: Date;
  project: Project;
}

enum WorkflowEventType {
  STAGE_ADVANCE = 'stage_advance',
  GATE_APPROVED = 'gate_approved',
  GATE_REJECTED = 'gate_rejected',
  MANUAL_OVERRIDE = 'manual_override'
}
```

### Relationships
- Belongs to Project (many-to-one)

## Junction Tables

### ServiceContact
**Purpose:** Links contacts to services with relationship metadata

```typescript
interface ServiceContact {
  id: string;
  serviceId: string;
  contactId: string;
  isPrimary: boolean;
  relationshipType: string; // 'main', 'billing', 'technical', etc.
  service: Service;
  contact: Contact;
  createdAt: Date;
}
```

### ProjectContact
**Purpose:** Links contacts to projects with role definitions

```typescript
interface ProjectContact {
  id: string;
  projectId: string;
  contactId: string;
  contactType: string; // 'stakeholder', 'reviewer', 'approver', etc.
  isActive: boolean;
  project: Project;
  contact: Contact;
  createdAt: Date;
}
```

### ServiceServiceCategory
**Purpose:** Many-to-many relationship between services and categories

```typescript
interface ServiceServiceCategory {
  id: string;
  serviceId: string;
  serviceCategoryId: string;
  service: Service;
  serviceCategory: ServiceCategory;
  createdAt: Date;
}
```

### ProjectServiceCategory
**Purpose:** Links projects to target user categories (reuses service categories)

```typescript
interface ProjectServiceCategory {
  id: string;
  projectId: string;
  serviceCategoryId: string;
  project: Project;
  serviceCategory: ServiceCategory;
  createdAt: Date;
}
```

---
[← Back to Tech Stack](tech-stack.md) | [Architecture Index](index.md) | [Next: API Specification →](api-specification.md)