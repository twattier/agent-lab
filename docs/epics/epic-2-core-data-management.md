# Epic 2: Core Data Management & Client Hierarchy

**Status:** 🟢 READY FOR DEVELOPMENT
**Prerequisites:** ✅ Epic 1 Complete (95/100) | ✅ Story 1.7 Complete (100/100)
**Estimated Effort:** 40-56 hours (1-2 sprints)
**Priority:** P1-Critical (Blocks Epic 3 & Epic 4)
**Started:** [Date]
**Completed:** [Date]

---

## Epic Goal

Implement the fundamental data management system for AgentLab, including client hierarchy management, project lifecycle tracking, and the foundational data models that support all platform functionality.

## Epic Description

**Project Context:**
AgentLab requires a robust data management foundation to handle client hierarchies (Client → Service), project categorization, and BMAD Method workflow states. This epic establishes the core data layer that enables all subsequent features.

**Epic Scope:**
This epic implements:

- Client and Service hierarchy management with contact information
- Project lifecycle management with comprehensive categorization
- BMAD workflow state tracking and progression
- Data validation and integrity constraints
- Basic CRUD operations for core entities

## Stories (5 Total)

### Story 2.1: Client & Service Hierarchy Management

**Status:** 🟢 READY | **Estimated:** 8-12 hours | **Developer Handoff:** ✅ [Complete](../stories/story-2.1-developer-handoff.md)

**Deliverables:**

- Implement Client and Service database models
- Create contact information storage (name + email)
- Add business domain classification system
- Build client hierarchy CRUD operations
- Implement client management API endpoints (14 endpoints total)

**Acceptance Criteria:** 35 total
**Blocks:** Stories 2.2, 2.3, 2.4, 2.5

---

### Story 2.2: Project Data Models & Lifecycle

**Status:** ⏳ PENDING Story 2.1 | **Estimated:** 10-14 hours | **Developer Handoff:** Epic-level

**Deliverables:**

- Create comprehensive project data model
- Implement project categorization (type, implementation, user, domain)
- Add project status and lifecycle state management
- Create project metadata and description handling
- Build project CRUD operations and API endpoints (7 endpoints)

**Dependencies:** Requires Story 2.1 (service_id foreign key)
**Blocks:** Stories 2.3, 2.4, 2.5

---

### Story 2.3: BMAD Workflow State Management

**Status:** ✅ DONE (99/100) | **Estimated:** 8-12 hours | **Actual:** 8-12 hours | **Developer Handoff:** ✅ [Complete](../stories/2.3.bmad-workflow-state-management.story.md)

**Deliverables:**

- ✅ Implement workflow template import from configuration
- ✅ Create workflow progression state tracking
- ✅ Add gate status management (pending, approved, rejected)
- ✅ Implement workflow stage transitions
- ✅ Create workflow state query and update APIs (4 endpoints)

**Dependencies:** Requires Story 2.2 (Project model with workflow_state JSONB) ✅
**Blocks:** Story 2.5 → Now Unblocked ✅

---

### Story 2.4: Document Metadata Management

**Status:** ✅ DONE (98/100) | **Estimated:** 8-10 hours | **Actual:** 8-10 hours | **Developer Handoff:** Epic-level

**Deliverables:**

- Create document tracking and metadata storage
- Implement GitHub-style change tracking
- Add document version management with pgvector 0.5.0
- Create document-to-project associations
- Build document management API endpoints (8 endpoints)

**Dependencies:** Requires Story 2.2 (Project model ✅), pgvector 0.5.0 ✅
**Blocks:** Story 2.5 → Now Unblocked ✅

---

### Story 2.5: Data Validation, Integrity & Seed Data Management

**Status:** 🟢 READY (All dependencies complete: Stories 2.1-2.4 ✅) | **Estimated:** 6-8 hours | **Developer Handoff:** Epic-level

**Deliverables:**

- **Implement comprehensive data validation rules:**
  - Pydantic models for API request/response validation
  - Database constraints for data integrity
  - Business logic validation for workflow states
  - Input sanitization and security validation
- **Add referential integrity constraints:**
  - Foreign key relationships between all entities
  - Cascade delete rules for data consistency
  - Unique constraints for business rules
  - Check constraints for enum validations
- **Create comprehensive migration and seeding strategy:**
  - Alembic migration scripts for schema evolution
  - Development seed data: Sample clients, services, projects
  - Test seed data: Comprehensive test scenarios and edge cases
  - Production seed data: Initial system configuration and default values
- **Seed data specifications:**
  - 3-5 sample clients with realistic business domains
  - 10-15 sample services across different client types
  - 20-25 sample projects covering all categorization types
  - BMAD workflow templates and initial configurations
  - User accounts and authentication test data
- **Implement audit logging and data management:**
  - Change tracking for all data modifications
  - User action logging for compliance
  - Data export capabilities (CSV, JSON formats)
  - Automated backup procedures and restore capabilities

## Success Criteria

### Data Model Requirements

- [ ] All entities properly normalized and related
- [ ] Referential integrity maintained across all operations
- [ ] Data validation prevents invalid states
- [ ] Migration scripts handle schema evolution
- [ ] Performance acceptable for expected data volumes

### API Requirements

- [ ] CRUD operations available for all core entities
- [ ] API endpoints follow RESTful conventions
- [ ] Response times under 200ms for standard operations
- [ ] Proper error handling and validation messages
- [ ] API documentation generated and accurate

### Business Logic Requirements

- [ ] Client hierarchy correctly enforced
- [ ] Project categorization supports all PRD requirements
- [ ] Workflow state transitions follow BMAD Method rules
- [ ] Document versioning preserves change history
- [ ] Data deletion follows confirmation requirements

## Data Models

### Client Hierarchy

```
Client
├── id: UUID
├── name: String
├── contact_name: String
├── contact_email: String
├── business_domain: Enum
└── services: [Service]

Service
├── id: UUID
├── client_id: UUID (FK)
├── name: String
├── contact_name: String
├── contact_email: String
└── projects: [Project]
```

### Project Management

```
Project
├── id: UUID
├── service_id: UUID (FK)
├── name: String
├── description: Text
├── project_type: Enum (new/existing)
├── implementation_type: Enum
├── user_type: Enum
├── business_domain: Enum
├── status: Enum
├── workflow_state: JSONB
├── created_at: Timestamp
└── updated_at: Timestamp
```

## Dependencies

- **Internal:** Epic 1 (Foundation & Infrastructure) - Database and API framework
- **External:** PostgreSQL with JSON support, pgvector extension

## Risks & Mitigation

- **Risk:** Data model changes requiring migration
  - **Mitigation:** Use Alembic for versioned database migrations
- **Risk:** Performance with large datasets
  - **Mitigation:** Implement proper indexing and query optimization
- **Risk:** Data integrity violations
  - **Mitigation:** Comprehensive validation at both API and database levels

## Definition of Done

- [ ] All 5 stories completed with acceptance criteria met (3/5 completed: 2.1 ✅, 2.2 ✅, 2.3 ✅)
- [ ] Data models support all PRD functional requirements (In Progress)
- [ ] API endpoints tested and documented (In Progress)
- [ ] Migration scripts validated (In Progress)
- [ ] Performance benchmarks met (In Progress)
- [ ] Security review completed for data access patterns (In Progress)

### Epic 2 Progress Summary

| Story                               | Status   | Score   | Completed Date |
| ----------------------------------- | -------- | ------- | -------------- |
| 2.1 Client & Service Hierarchy      | ✅ DONE  | 100/100 | 2025-09-30     |
| 2.2 Project Data Models & Lifecycle | ✅ DONE  | 100/100 | 2025-09-30     |
| 2.3 BMAD Workflow State Management  | ✅ DONE  | 99/100  | 2025-10-01     |
| 2.4 Document Metadata Management    | ✅ DONE  | 98/100  | 2025-10-01     |
| 2.5 Data Validation & Seed Data     | 🟢 READY | -       | -              |

**Overall Epic Progress:** 80% Complete (4/5 stories done)

---

## 📋 Prerequisites & Readiness

### ✅ Completed Prerequisites

1. **Epic 1: Foundation & Infrastructure Setup**
   - Status: ✅ COMPLETE (Quality Score: 95/100)
   - Date Completed: 2025-09-30
   - Deliverables: Docker environment, PostgreSQL 15.4, pgvector 0.5.0, FastAPI, testing infrastructure
   - Reference: [epic-1-foundation-infrastructure.md](./epic-1-foundation-infrastructure.md)

2. **Story 1.7: Architecture Documentation Alignment**
   - Status: ✅ COMPLETE (Quality Score: 100/100)
   - Date Completed: 2025-09-30
   - Deliverables: All architecture docs aligned with canonical versions
   - Reference: [story-1.7-architecture-documentation-alignment.md](../stories/story-1.7-architecture-documentation-alignment.md)

3. **Architecture Documentation**
   - All version mismatches resolved (PostgreSQL pg17→pg15, pgvector 0.8→0.5.0, Python 3.12→3.11.5)
   - IaC implementation documented
   - Mock services documented
   - CI/CD pipeline documented

### Environment Validation

Before starting Epic 2, verify:

```bash
# PostgreSQL version
docker exec -it agentlab-postgres-1 psql -U agentlab -c "SELECT version();"
# Expected: PostgreSQL 15.4

# pgvector extension
docker exec -it agentlab-postgres-1 psql -U agentlab -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
# Expected: vector | 0.5.0

# Python version
python --version
# Expected: Python 3.11.5

# Development environment
docker-compose ps
# Expected: All services running (postgres, api, web if applicable)
```

---

## 📚 Resources & References

### Documentation

- **Sprint Planning Checklist:** [epic-2-sprint-planning-checklist.md](./epic-2-sprint-planning-checklist.md)
- **Story 2.1 Developer Handoff:** [story-2.1-developer-handoff.md](../stories/story-2.1-developer-handoff.md)
- **Canonical Version Reference:** [EPIC-2-CANONICAL-VERSIONS.md](../EPIC-2-CANONICAL-VERSIONS.md)
- **Architecture - Data Models:** [architecture/data-models.md](../architecture/data-models.md)
- **Architecture - Database Schema:** [architecture/database-schema.md](../architecture/database-schema.md)
- **Architecture - API Specification:** [architecture/api-specification.md](../architecture/api-specification.md)
- **Architecture - Tech Stack:** [architecture/tech-stack.md](../architecture/tech-stack.md)

### PRD Requirements Addressed

Epic 2 directly implements the following PRD functional requirements:

- **FR1:** Two-level client hierarchy (Client → Service) with contact information and business domain classification
- **FR2:** Complete project lifecycle management with categorization by type, implementation, user, and business domain
- **FR3:** BMAD Method workflow template import and workflow progression status display
- **FR4:** Markdown document display with GitHub-style change tracking and version management
- **FR10** (partial): Data deletion with proper cascade rules (UI confirmation deferred to later epic)

Reference: [prd/requirements.md](../prd/requirements.md)

### Technical Stack (Canonical Versions)

| Component  | Version      | Status       |
| ---------- | ------------ | ------------ |
| PostgreSQL | 15.4         | ✅ Validated |
| pgvector   | 0.5.0        | ✅ Validated |
| Python     | 3.11.5       | ✅ Validated |
| FastAPI    | 0.115+       | ✅ Validated |
| SQLAlchemy | 2.0+ (async) | ✅ Ready     |
| Alembic    | 1.11+        | ✅ Ready     |
| Pydantic   | 2.0+         | ✅ Ready     |

---

## 🚀 Getting Started

### For Developers

1. **Review Documentation:**
   - Read this epic document completely
   - Review [story-2.1-developer-handoff.md](../stories/story-2.1-developer-handoff.md) for Story 2.1
   - Familiarize with [data-models.md](../architecture/data-models.md) and [database-schema.md](../architecture/database-schema.md)

2. **Validate Environment:**
   - Run environment validation commands above
   - Ensure all Epic 1 tests passing: `pytest apps/api/tests/`
   - Verify database connection: `alembic current`

3. **Start with Story 2.1:**
   - Story 2.1 has complete developer handoff documentation
   - 35 acceptance criteria clearly defined
   - Code examples provided for all components
   - Testing guidance included

4. **Follow Development Workflow:**
   - Create feature branch: `git checkout -b epic-2/story-2.1`
   - Implement database models first
   - Create Alembic migration
   - Implement Pydantic schemas
   - Implement API endpoints
   - Write tests (aim for 80%+ coverage)
   - Update documentation
   - Submit for QA review

### For Product Owners

1. **Sprint Planning:**
   - Review [epic-2-sprint-planning-checklist.md](./epic-2-sprint-planning-checklist.md)
   - Decide: Single sprint (full epic) or two sprints (split)
   - Assign developer(s) and QA engineer(s)
   - Schedule sprint review and retrospective

2. **Story Validation:**
   - All acceptance criteria in Story 2.1 defined (35 total)
   - Stories 2.2-2.5 have sufficient detail in epic document
   - Optional: Create detailed handoff docs for Stories 2.2-2.5

3. **Availability:**
   - Be available for acceptance criteria clarification
   - Schedule mid-sprint check-ins
   - Prepare for sprint review demos

### For QA Engineers

1. **Test Planning:**
   - Review Epic 2 success criteria
   - Prepare QA gates for each story (template: `docs/qa/gates/`)
   - Plan integration test scenarios

2. **Test Execution:**
   - Validate acceptance criteria for each story
   - Verify test coverage ≥80%
   - Perform manual API testing via `/docs`
   - Test database migrations (upgrade/downgrade)
   - Execute integration tests

---

## 🎯 Epic 2 Metrics & Tracking

### Story Completion

| Story | Status     | Start Date | Completion Date | Quality Score | Tests |
| ----- | ---------- | ---------- | --------------- | ------------- | ----- |
| 2.1   | 🟢 READY   | [TBD]      | [TBD]           | [TBD]         | 0/35+ |
| 2.2   | ⏳ PENDING | [TBD]      | [TBD]           | [TBD]         | 0/22+ |
| 2.3   | ⏳ PENDING | [TBD]      | [TBD]           | [TBD]         | 0/18+ |
| 2.4   | ⏳ PENDING | [TBD]      | [TBD]           | [TBD]         | 0/20+ |
| 2.5   | ⏳ PENDING | [TBD]      | [TBD]           | [TBD]         | 0/25+ |

### API Endpoints

| Category            | Planned | Implemented | Tested | Documented |
| ------------------- | ------- | ----------- | ------ | ---------- |
| Client Management   | 5       | 0           | 0      | 0          |
| Service Management  | 5       | 0           | 0      | 0          |
| Contact Management  | 2       | 0           | 0      | 0          |
| Service Categories  | 2       | 0           | 0      | 0          |
| Project Management  | 7       | 0           | 0      | 0          |
| Workflow Management | 4       | 0           | 0      | 0          |
| Document Management | 8       | 0           | 0      | 0          |
| **Total**           | **33**  | **0**       | **0**  | **0**      |

### Test Coverage

| Component          | Target Coverage | Current Coverage | Tests Written | Tests Passing |
| ------------------ | --------------- | ---------------- | ------------- | ------------- |
| Database Models    | 80%             | 0%               | 0             | 0             |
| API Endpoints      | 80%             | 0%               | 0             | 0             |
| Validation Logic   | 90%             | 0%               | 0             | 0             |
| Integration Tests  | N/A             | N/A              | 0             | 0             |
| **Overall Epic 2** | **80%**         | **0%**           | **0**         | **0**         |

---

## 📞 Support & Escalation

**Product Owner:** Sarah

- Acceptance criteria questions
- Scope clarifications
- Priority decisions

**Tech Lead:** [Assign]

- Architecture questions
- Technical approach validation
- Cross-story integration

**QA Lead:** Quinn

- Testing strategy
- Quality gates
- Coverage validation

**Scrum Master:** Bob (if applicable)

- Sprint planning
- Impediment removal
- Velocity tracking

---

## 🔄 Epic 2 Changelog

| Date       | Version | Change                                                      | Author     |
| ---------- | ------- | ----------------------------------------------------------- | ---------- |
| 2025-09-30 | 1.0     | Epic created from PRD requirements                          | Sarah (PO) |
| 2025-09-30 | 1.1     | Updated with Story 1.7 completion, readiness validation     | Sarah (PO) |
| 2025-09-30 | 1.2     | Added sprint planning checklist, story estimates, resources | Sarah (PO) |

---

**Next Epic:** Epic 3 - MCP Integration (depends on Epic 2 completion)
**Related Documents:** [PRD](../prd.md) | [Architecture](../architecture.md) | [Epic 1](./epic-1-foundation-infrastructure.md)
