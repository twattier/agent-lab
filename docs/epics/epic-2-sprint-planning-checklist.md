# Epic 2: Sprint Planning & Execution Checklist

**Epic:** Epic 2 - Core Data Management & Client Hierarchy
**Status:** ✅ READY FOR SPRINT PLANNING
**Created:** 2025-09-30
**Product Owner:** Sarah
**Epic Document:** [epic-2-core-data-management.md](./epic-2-core-data-management.md)

---

## 📊 Epic 2 Overview

**Goal:** Implement the fundamental data management system for AgentLab, including client hierarchy management, project lifecycle tracking, and the foundational data models that support all platform functionality.

**Stories:** 5 total
**Estimated Effort:** 40-60 hours (1-2 sprint capacity for solo developer)
**Priority:** P1-Critical (Blocks Epic 3 & Epic 4)

---

## ✅ Pre-Sprint Planning Checklist

### Prerequisites Validation

- [x] **Epic 1 Complete**
  - Status: ✅ COMPLETE (Quality Score: 95/100)
  - All 6 stories delivered with QA approval
  - Development environment operational (<2 minute setup)

- [x] **Story 1.7 Complete**
  - Status: ✅ COMPLETE (Quality Score: 100/100)
  - All architecture version mismatches resolved
  - PostgreSQL 15.4, pgvector 0.5.0, Python 3.11.5 aligned

- [x] **Architecture Documentation Validated**
  - All docs reference correct canonical versions
  - Tech stack document aligned
  - Database schema documented
  - API specification available

- [x] **Development Environment Ready**
  - Docker-compose operational
  - PostgreSQL 15.4 + pgvector 0.5.0 running
  - FastAPI 0.115+ backend ready
  - Testing infrastructure operational (49 tests passing)

### Story Preparation

- [x] **Story 2.1 Ready**
  - Developer handoff document complete
  - 35 acceptance criteria defined
  - Code examples provided
  - Testing guidance documented

- [ ] **Stories 2.2-2.5 Preparation**
  - Epic document has sufficient detail
  - Can create detailed handoff docs if needed
  - Decision: Use epic-level documentation OR create individual handoff docs

### Team Readiness

- [ ] **Developer Assignment**
  - [ ] Developer assigned to Epic 2
  - [ ] Developer has reviewed Story 2.1 handoff doc
  - [ ] Developer confirmed understanding of acceptance criteria
  - [ ] Developer environment validated (PostgreSQL, Python versions correct)

- [ ] **QA Assignment**
  - [ ] QA engineer assigned for Epic 2
  - [ ] QA has reviewed Epic 2 success criteria
  - [ ] QA gates prepared for Stories 2.1-2.5

- [ ] **PO Availability**
  - [ ] PO (Sarah) available for story clarifications
  - [ ] PO available for acceptance criteria validation
  - [ ] PO scheduled for sprint review

---

## 📅 Sprint Planning

### Sprint Capacity Planning

**Estimated Story Effort:**

- Story 2.1: 8-12 hours (Client & Service Hierarchy)
- Story 2.2: 10-14 hours (Project Data Models & Lifecycle)
- Story 2.3: 8-12 hours (BMAD Workflow State Management)
- Story 2.4: 8-10 hours (Document Metadata Management)
- Story 2.5: 6-8 hours (Data Validation & Seed Data)
- **Total:** 40-56 hours

**Sprint Options:**

**Option A: Single Sprint (Full Epic)**

- Duration: 2 weeks
- Capacity needed: 40-56 hours
- Best for: Solo developer with full-time allocation
- Risk: High - all stories in one sprint

**Option B: Two Sprints (Split Epic)**

- Sprint 1: Stories 2.1, 2.2, 2.3 (26-38 hours)
- Sprint 2: Stories 2.4, 2.5 (14-18 hours)
- Best for: Incremental delivery with mid-epic review
- Risk: Lower - allows course correction

**Recommended:** Option B (Two Sprints)

### Sprint 1 Goals

**Stories:** 2.1, 2.2, 2.3
**Deliverables:**

- Client/Service hierarchy with CRUD APIs
- Project data models with lifecycle management
- BMAD workflow state tracking
- All migrations, tests, API documentation

**Sprint 1 Success Criteria:**

- [ ] 23 API endpoints implemented and tested
- [ ] Database migrations run successfully
- [ ] 80%+ test coverage achieved
- [ ] All Story 2.1-2.3 acceptance criteria met

### Sprint 2 Goals

**Stories:** 2.4, 2.5
**Deliverables:**

- Document metadata management
- Comprehensive data validation
- Seed data for all entities
- Epic 2 integration testing

**Sprint 2 Success Criteria:**

- [ ] Document management with versioning working
- [ ] All data validation rules implemented
- [ ] Seed data loads successfully
- [ ] All Epic 2 success criteria met

---

## 🎯 Story Execution Checklist

### Story 2.1: Client & Service Hierarchy Management

**Status:** 🟢 READY FOR DEVELOPMENT

#### Pre-Development

- [ ] Developer assigned
- [ ] Developer reviewed [story-2.1-developer-handoff.md](../stories/story-2.1-developer-handoff.md)
- [ ] Developer environment validated
- [ ] Developer signed off on acceptance criteria

#### Development Tasks

- [ ] Database models created (Client, Service, Contact, ServiceCategory, junction tables)
- [ ] Alembic migration created and tested
- [ ] Migration runs: `alembic upgrade head` ✅
- [ ] Migration rollback tested: `alembic downgrade -1` ✅
- [ ] Pydantic schemas created (Request/Response models)
- [ ] Client API endpoints implemented (5 endpoints)
- [ ] Service API endpoints implemented (5 endpoints)
- [ ] Contact API endpoints implemented (2 endpoints)
- [ ] ServiceCategory endpoints implemented (2 endpoints)
- [ ] All endpoints documented in FastAPI `/docs`

#### Testing

- [ ] Unit tests created (minimum 15 tests)
- [ ] Integration tests created (minimum 8 tests)
- [ ] All tests passing
- [ ] Test coverage ≥80% for new code
- [ ] Cascade delete behavior tested
- [ ] Email unique constraint tested

#### Code Quality

- [ ] No linting errors (`ruff check`, `black --check`)
- [ ] Type checking passes (`mypy`)
- [ ] Code reviewed by peer
- [ ] All TODO/FIXME comments resolved

#### Documentation

- [ ] API documentation updated
- [ ] ERD diagram updated (if needed)
- [ ] Developer notes documented

#### QA & Acceptance

- [ ] QA gate created: `docs/qa/gates/2.1-*.yml`
- [ ] All 35 acceptance criteria validated
- [ ] PO sign-off received
- [ ] Story marked as DONE

---

### Story 2.2: Project Data Models & Lifecycle

**Status:** ⏳ PENDING Story 2.1 completion

#### Prerequisites

- [ ] Story 2.1 COMPLETE (service_id foreign key available)
- [ ] Client and Service tables exist in database

#### Pre-Development

- [ ] Developer reviewed Epic 2 Story 2.2 details
- [ ] Acceptance criteria clarified with PO
- [ ] Implementation approach validated

#### Development Tasks

- [ ] Project model created with all fields
  - [ ] Basic fields: id, name, description
  - [ ] Foreign keys: service_id, implementation_type_id
  - [ ] Enums: project_type, status
  - [ ] JSON: workflow_state
  - [ ] Timestamps: created_at, updated_at
- [ ] ImplementationType reference table created
- [ ] ProjectServiceCategory junction table created (user categories)
- [ ] ProjectContact junction table created
- [ ] Alembic migration created and tested
- [ ] Pydantic schemas created for Project CRUD
- [ ] Project API endpoints implemented
  - [ ] POST /api/v1/projects (create)
  - [ ] GET /api/v1/projects (list with filtering)
  - [ ] GET /api/v1/projects/{id} (detail with relationships)
  - [ ] PUT /api/v1/projects/{id} (update)
  - [ ] DELETE /api/v1/projects/{id} (delete)
  - [ ] GET /api/v1/projects?service_id={id} (filter by service)
  - [ ] GET /api/v1/projects?status={status} (filter by status)

#### Testing

- [ ] Unit tests for Project model (minimum 12 tests)
- [ ] Integration tests for project lifecycle (minimum 10 tests)
- [ ] Test project categorization (type, implementation, user, domain)
- [ ] Test status transitions (draft → active → completed → archived)
- [ ] Test filtering and pagination
- [ ] Test coverage ≥80%

#### Code Quality

- [ ] Linting passed
- [ ] Type checking passed
- [ ] Code reviewed
- [ ] Documentation updated

#### QA & Acceptance

- [ ] QA gate created: `docs/qa/gates/2.2-*.yml`
- [ ] All acceptance criteria met
- [ ] PO sign-off received
- [ ] Story marked as DONE

---

### Story 2.3: BMAD Workflow State Management

**Status:** ⏳ PENDING Story 2.2 completion

#### Prerequisites

- [ ] Story 2.2 COMPLETE (Project model with workflow_state JSONB available)
- [ ] BMAD workflow configuration files accessible

#### Pre-Development

- [ ] Developer reviewed BMAD workflow template structure
- [ ] Workflow state schema defined
- [ ] Gate status enum defined (pending, approved, rejected)

#### Development Tasks

- [ ] WorkflowEvent model created
  - [ ] Fields: event_type, from_stage, to_stage, user_id, metadata, timestamp
  - [ ] Enum: WorkflowEventType (stage_advance, gate_approved, gate_rejected, manual_override)
- [ ] Workflow template import functionality
  - [ ] Read workflow config from YAML/JSON
  - [ ] Validate workflow structure
  - [ ] Initialize project workflow_state
- [ ] Workflow progression logic
  - [ ] Stage transition validation
  - [ ] Gate status management
  - [ ] Event logging for all transitions
- [ ] Alembic migration for WorkflowEvent table
- [ ] Workflow API endpoints implemented
  - [ ] POST /api/v1/projects/{id}/workflow/advance (advance to next stage)
  - [ ] POST /api/v1/projects/{id}/workflow/gate (approve/reject gate)
  - [ ] GET /api/v1/projects/{id}/workflow/state (get current state)
  - [ ] GET /api/v1/projects/{id}/workflow/history (get event history)

#### Testing

- [ ] Unit tests for workflow state management (minimum 10 tests)
- [ ] Integration tests for workflow progression (minimum 8 tests)
- [ ] Test workflow template import
- [ ] Test gate approval/rejection flow
- [ ] Test workflow event history
- [ ] Test invalid state transitions
- [ ] Test coverage ≥80%

#### Code Quality

- [ ] Linting passed
- [ ] Type checking passed
- [ ] Code reviewed
- [ ] Documentation updated

#### QA & Acceptance

- [ ] QA gate created: `docs/qa/gates/2.3-*.yml`
- [ ] All acceptance criteria met
- [ ] PO sign-off received
- [ ] Story marked as DONE

---

### Story 2.4: Document Metadata Management

**Status:** ⏳ PENDING Story 2.2 completion

#### Prerequisites

- [ ] Story 2.2 COMPLETE (Project model available)
- [ ] pgvector 0.5.0 ready for vector storage

#### Pre-Development

- [ ] Developer reviewed document versioning requirements
- [ ] Content hash strategy defined (SHA-256)
- [ ] Document type enum defined

#### Development Tasks

- [ ] Document model created
  - [ ] Fields: name, content, content_hash, version, language, document_type
  - [ ] Vector field: content_vector (pgvector 1536 dimensions)
  - [ ] Foreign key: project_id
- [ ] DocumentVersion model created (for change tracking)
  - [ ] Fields: version, content, content_hash, change_summary, created_by
- [ ] Comment model created
  - [ ] Fields: content, line_number, resolved, user_id
- [ ] Alembic migration with pgvector index
  - [ ] CREATE INDEX using ivfflat (pgvector 0.5.0 syntax)
- [ ] Document API endpoints implemented
  - [ ] POST /api/v1/documents (create)
  - [ ] GET /api/v1/documents (list with filtering)
  - [ ] GET /api/v1/documents/{id} (detail)
  - [ ] PUT /api/v1/documents/{id} (update with versioning)
  - [ ] DELETE /api/v1/documents/{id} (delete)
  - [ ] GET /api/v1/documents/{id}/versions (version history)
  - [ ] GET /api/v1/documents/{id}/comments (get comments)
  - [ ] POST /api/v1/documents/{id}/comments (add comment)

#### Testing

- [ ] Unit tests for Document model (minimum 12 tests)
- [ ] Integration tests for versioning (minimum 8 tests)
- [ ] Test content hash generation
- [ ] Test change detection
- [ ] Test version history retrieval
- [ ] Test comment functionality
- [ ] Test pgvector index (if semantic search implemented)
- [ ] Test coverage ≥80%

#### Code Quality

- [ ] Linting passed
- [ ] Type checking passed
- [ ] Code reviewed
- [ ] Documentation updated

#### QA & Acceptance

- [ ] QA gate created: `docs/qa/gates/2.4-*.yml`
- [ ] All acceptance criteria met
- [ ] PO sign-off received
- [ ] Story marked as DONE

---

### Story 2.5: Data Validation, Integrity & Seed Data Management

**Status:** ⏳ PENDING Stories 2.1-2.4 completion

#### Prerequisites

- [ ] All Stories 2.1-2.4 COMPLETE
- [ ] All data models exist in database

#### Pre-Development

- [ ] Developer reviewed comprehensive validation requirements
- [ ] Seed data specifications confirmed
- [ ] Audit logging strategy defined

#### Development Tasks

**Data Validation:**

- [ ] Pydantic models enhanced with comprehensive validation
  - [ ] Email format validation (EmailStr)
  - [ ] URL validation for Claude Code paths
  - [ ] Enum validation for all categorical fields
  - [ ] Length constraints on all string fields
- [ ] Database constraints verified
  - [ ] Foreign key constraints with appropriate CASCADE rules
  - [ ] Unique constraints on all business keys
  - [ ] Check constraints for enum validations
  - [ ] NOT NULL constraints where required
- [ ] Business logic validation
  - [ ] Workflow state transition rules
  - [ ] Project status validation
  - [ ] Document versioning logic
- [ ] Input sanitization
  - [ ] XSS prevention for text inputs
  - [ ] SQL injection prevention (SQLAlchemy ORM provides this)
  - [ ] File path validation for Claude Code integration

**Referential Integrity:**

- [ ] All foreign key relationships validated
- [ ] Cascade delete rules tested for all relationships
- [ ] Orphan prevention verified
- [ ] Circular dependency checks

**Seed Data Implementation:**

- [ ] Development seed data created
  - [ ] 3-5 sample clients (realistic business domains)
  - [ ] 10-15 sample services across different clients
  - [ ] 20-25 sample projects covering all categorizations
  - [ ] Sample contacts with realistic data
  - [ ] Sample documents with version history
- [ ] Test seed data created
  - [ ] Edge case scenarios
  - [ ] Boundary condition data
  - [ ] Invalid data for negative testing
  - [ ] Comprehensive test fixtures
- [ ] Production seed data created
  - [ ] BMAD workflow templates
  - [ ] Service categories (already in Story 2.1)
  - [ ] Implementation types (already in Story 2.2)
  - [ ] System configuration defaults
- [ ] Seed data Alembic migration or script
- [ ] Seed data loading tested
  - [ ] `alembic upgrade` loads seed data ✅
  - [ ] Idempotent loading (can run multiple times)
  - [ ] Data validation on load

**Audit Logging:**

- [ ] Change tracking for data modifications
  - [ ] Created/updated timestamps (already in models)
  - [ ] User action logging (if user model exists, else defer)
- [ ] Data export capabilities
  - [ ] CSV export endpoint (if required)
  - [ ] JSON export endpoint (if required)

#### Testing

- [ ] Unit tests for validation rules (minimum 15 tests)
- [ ] Integration tests for referential integrity (minimum 10 tests)
- [ ] Test seed data loading
- [ ] Test constraint violations
- [ ] Test cascade delete behavior
- [ ] Test data export (if implemented)
- [ ] Test coverage ≥80%

#### Code Quality

- [ ] Linting passed
- [ ] Type checking passed
- [ ] Code reviewed
- [ ] Documentation updated

#### QA & Acceptance

- [ ] QA gate created: `docs/qa/gates/2.5-*.yml`
- [ ] All acceptance criteria met
- [ ] PO sign-off received
- [ ] Story marked as DONE

---

## 📊 Epic 2 Integration Testing

**After all stories complete:**

### Integration Test Scenarios

- [ ] **End-to-End User Flows**
  - [ ] Create client → Create service → Assign contact → Create project
  - [ ] Create project → Add documents → Version documents → Add comments
  - [ ] Import workflow → Advance stages → Approve gates → Complete project
  - [ ] Filter and search across all entities
  - [ ] Cascade delete validation (client deletion cascades properly)

- [ ] **Data Integrity Tests**
  - [ ] Foreign key constraints enforced
  - [ ] Unique constraints prevent duplicates
  - [ ] Enum validation works across all models
  - [ ] Timestamps update correctly

- [ ] **Performance Tests**
  - [ ] List endpoints with 100+ records (pagination works)
  - [ ] Nested relationship queries perform acceptably
  - [ ] Database indexes improve query performance
  - [ ] Vector similarity search performs (if implemented)

- [ ] **API Documentation Tests**
  - [ ] All endpoints accessible at `/docs`
  - [ ] Request/response examples accurate
  - [ ] Error responses documented
  - [ ] Authentication requirements clear (if implemented)

---

## ✅ Epic 2 Success Criteria Validation

### Data Model Requirements

- [ ] All entities properly normalized and related
- [ ] Referential integrity maintained across all operations
- [ ] Data validation prevents invalid states
- [ ] Migration scripts handle schema evolution
- [ ] Performance acceptable for expected data volumes (50+ projects, 1000+ documents)

### API Requirements

- [ ] CRUD operations available for all core entities
- [ ] API endpoints follow RESTful conventions
- [ ] Response times under 200ms for standard operations
- [ ] Proper error handling and validation messages
- [ ] API documentation generated and accurate

### Business Logic Requirements

- [ ] Client hierarchy correctly enforced (Client → Service → Project)
- [ ] Project categorization supports all PRD requirements
- [ ] Workflow state transitions follow BMAD Method rules
- [ ] Document versioning preserves change history
- [ ] Data deletion follows confirmation requirements (if UI implemented)

### Testing Requirements

- [ ] All 5 stories have passing tests
- [ ] Overall test coverage ≥80% for Epic 2 code
- [ ] Integration tests cover critical workflows
- [ ] Edge cases tested (boundary conditions, invalid inputs)

---

## 📋 Epic 2 Definition of Done

- [ ] All 5 stories completed with acceptance criteria met
- [ ] Data models support all PRD functional requirements (FR1-FR4, partial FR5)
- [ ] API endpoints tested and documented
- [ ] Migration scripts validated (upgrade/downgrade tested)
- [ ] Performance benchmarks met
- [ ] Security review completed for data access patterns (if applicable)
- [ ] Epic 2 retrospective completed
- [ ] Handoff notes prepared for Epic 3

---

## 📞 Epic 2 Support & Resources

### Documentation

- **Epic 2 Document:** [epic-2-core-data-management.md](./epic-2-core-data-management.md)
- **Story 2.1 Handoff:** [story-2.1-developer-handoff.md](../stories/story-2.1-developer-handoff.md)
- **Architecture - Data Models:** [data-models.md](../architecture/data-models.md)
- **Architecture - Database Schema:** [database-schema.md](../architecture/database-schema.md)
- **Canonical Versions:** [EPIC-2-CANONICAL-VERSIONS.md](../EPIC-2-CANONICAL-VERSIONS.md)

### Prerequisites

- **Epic 1 Status:** [epic-1-foundation-infrastructure.md](./epic-1-foundation-infrastructure.md)
- **Story 1.7 Status:** [story-1.7-architecture-documentation-alignment.md](../stories/story-1.7-architecture-documentation-alignment.md)

### PRD Requirements

- **FR1:** Two-level client hierarchy with contact info and business domains
- **FR2:** Complete project lifecycle management with categorization
- **FR3:** BMAD workflow template import and progression status
- **FR4:** Document display with GitHub-style change tracking

### Escalation

- **Product Owner:** Sarah (for acceptance criteria, scope questions)
- **Tech Lead:** (for technical architecture questions)
- **QA Lead:** Quinn (for testing strategy, quality gates)

---

## 📅 Sprint Review Preparation

### Sprint 1 Review (After Stories 2.1-2.3)

**Demonstrate:**

- [ ] Client/Service hierarchy CRUD via API
- [ ] Project creation and lifecycle management
- [ ] Workflow state tracking and progression
- [ ] Database schema in PostgreSQL
- [ ] Test coverage reports

**Metrics:**

- [ ] Stories completed: X/3
- [ ] Test coverage: XX%
- [ ] API endpoints: XX total
- [ ] Migration files: X created

**Blockers/Risks:**

- Document any blockers encountered
- Note any technical debt created
- Identify risks for Sprint 2

### Sprint 2 Review (After Stories 2.4-2.5)

**Demonstrate:**

- [ ] Document management with versioning
- [ ] Complete data model with seed data
- [ ] End-to-end workflow: Client → Service → Project → Documents
- [ ] Comprehensive validation and error handling
- [ ] Full Epic 2 integration

**Metrics:**

- [ ] Epic 2 stories completed: 5/5 ✅
- [ ] Total test coverage: XX%
- [ ] Total API endpoints: XX
- [ ] Total database tables: XX
- [ ] Seed data records: XXX

**Epic 2 Completion:**

- [ ] All success criteria met
- [ ] Epic 2 retrospective scheduled
- [ ] Epic 3 dependencies validated

---

## 🎯 Next Steps After Epic 2

**Epic 3: MCP Integration** will depend on Epic 2 deliverables:

- Client/Service/Project data models
- Document management system
- Workflow state tracking

**Validation before Epic 3:**

- [ ] All Epic 2 APIs documented and stable
- [ ] Database schema finalized
- [ ] Seed data available for Epic 3 testing
- [ ] Architecture documentation updated with Epic 2 implementations

---

**Created:** 2025-09-30
**Product Owner:** Sarah
**Last Updated:** 2025-09-30
**Status:** ✅ READY FOR SPRINT PLANNING
