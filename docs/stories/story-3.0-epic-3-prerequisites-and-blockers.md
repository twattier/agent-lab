# Story 3.0: Epic 3 Prerequisites & Blockers Resolution

**Epic:** Epic 3: BMAD Method Workflow Integration
**Story:** 3.0 - Prerequisites & Blockers Resolution (Foundation Story)
**Status:** 🟡 Ready for Development
**Estimated Effort:** 28-38 hours (1 week with 2 developers + QA)
**Priority:** P0-Blocker (Must complete before Stories 3.1-3.5)
**Dependencies:** Epic 2 complete ✅
**Blocks:** Stories 3.1, 3.2, 3.3, 3.4, 3.5
**Created:** 2025-10-01
**Owner:** Dev Lead + QA Engineer (Quinn)

---

## Story

**As a** Development Team preparing for Epic 3,
**I want** all Epic 2 technical validations completed, Epic 3 infrastructure configured, and process improvements implemented,
**so that** Epic 3 Stories 3.1-3.5 can execute without blockers, with high quality documentation, and validated integration points.

---

## Story Context

### Why This Story Exists

Epic 3 introduces significant new complexity:

- **External service integrations:** MCP Protocol, OpenAI API, Anthropic Claude API, OLLAMA
- **Complex workflow automation:** Gate management, workflow progression, conversational agents
- **New technology stack:** Model Context Protocol (MCP), LLM provider integrations

**Without Story 3.0 completion:**

- Epic 2 quality gaps (Stories 2.3, 2.4) may propagate into Epic 3
- Integration tests cannot execute (async driver configuration issue)
- Epic 3 external dependency versions undocumented (risk of version conflicts)
- Story documentation gaps (Stories 3.1-3.5 lack detailed handoff docs like Story 2.1)
- Migration validation not automated (risk of repeating Story 2.4 migration inconsistency)

**With Story 3.0 completion:**

- Epic 2 quality scores reach 100/100 (Stories 2.3, 2.4 gaps resolved)
- All integration tests execute reliably in CI/CD
- Epic 3 external dependencies documented and validated
- All Epic 3 stories have Story 2.1-quality developer handoff docs
- Migration validation automated and integrated into CI/CD
- Clear dependency map enables parallel execution (Stories 3.2/3.3)

---

## Acceptance Criteria

### Category 1: Epic 2 Technical Validation (10 criteria)

#### AC1: Story 2.3 Gate Timing Logic Fixed

**Priority:** P2-High (Potentially blocks Epic 3 gate management)

- [ ] Run `pytest apps/api/tests/integration/test_workflow_api.py::test_complete_workflow_lifecycle -vv` successfully
- [ ] Identify root cause of gate timing race condition (gate approval → stage advance)
- [ ] Implement fix (Option A: transaction delay, Option B: atomic update, or Option C: transaction isolation)
- [ ] Verify fix: Run test 10 times consecutively, all pass
- [ ] Add regression test: `test_rapid_gate_approval_and_advance` (tests race condition explicitly)
- [ ] All 16 Story 2.3 integration tests passing (100% pass rate)
- [ ] Update Story 2.3 QA Results: Quality Score 99/100 → 100/100
- [ ] Document fix in Story 2.3 Dev Agent Record

**Validation:**

```bash
# Must pass consistently (10 consecutive runs)
for i in {1..10}; do
  pytest apps/api/tests/integration/test_workflow_api.py::test_complete_workflow_lifecycle -v || exit 1
done
echo "✅ Gate timing logic verified"
```

---

#### AC2: Alembic Migration Consistency Validated

**Priority:** P1-Critical (Database integrity)

- [ ] Run `alembic history` and verify linear progression (no branches)
- [ ] Run `alembic current` and verify matches latest migration
- [ ] Query `alembic_version` table: Only 1 row, matches current revision
- [ ] Validate all Epic 2 migrations present (Stories 2.1-2.5)
- [ ] Verify database schema matches SQLAlchemy models (no drift)
- [ ] Test migration rollback: `alembic downgrade -1` executes cleanly
- [ ] Test migration upgrade: `alembic upgrade head` restores correctly
- [ ] No orphaned migration files in `apps/api/migrations/versions/`
- [ ] Create corrective migration if inconsistencies found
- [ ] Document migration state in validation report

**Validation:**

```bash
# Check migration history
alembic history | grep -E "^[a-f0-9]{12}" | wc -l  # Count migrations
# Expected: 5-6 migrations (Stories 2.1-2.5 + any corrections)

# Check current revision
alembic current | grep -E "^[a-f0-9]{12}"
# Expected: Latest migration revision

# Check alembic_version table
docker exec -it agentlab-postgres-1 psql -U agentlab -d agentlab -c "SELECT * FROM alembic_version;"
# Expected: 1 row, matches alembic current
```

---

#### AC3: Story 2.3 Workflow Event Audit Trail Validated

**Priority:** P1-Critical (Workflow audit integrity required for Epic 3)

- [ ] Review all workflow state mutation code paths (advance_stage, approve_gate, reject_gate, manual_override)
- [ ] Verify WorkflowEvent creation for each mutation path (code review)
- [ ] Add integration test: `test_manual_override_creates_event` (if missing)
- [ ] Add integration test: `test_gate_reapproval_creates_multiple_events` (if missing)
- [ ] Add integration test: `test_concurrent_workflow_updates_no_race_condition` (if missing)
- [ ] Verify event metadata completeness: reason, notes, previous_gate_status, new_gate_status
- [ ] Run full workflow event test suite: `pytest apps/api/tests/integration/test_workflow_api.py -k "workflow_event or history" -v`
- [ ] Verify 100% of workflow state mutations create WorkflowEvent (no gaps)
- [ ] Document validation results in validation report

**Validation:**

```bash
# Run workflow event tests
pytest apps/api/tests/integration/test_workflow_api.py -k "event" -v

# Expected: All event-related tests passing
# Expected: Coverage for STAGE_ADVANCE, GATE_APPROVED, GATE_REJECTED, MANUAL_OVERRIDE
```

---

#### AC4: Story 2.4 Semantic Search Validated

**Priority:** P1-Critical (If Epic 3 Story 3.5 depends on semantic search)

- [ ] Validate embedding generation on document creation (integration test)
- [ ] Validate embedding update on content changes (integration test)
- [ ] Test bulk document operations: Create 100 documents, verify all embeddings generated
- [ ] Test document rollback to previous version: Verify embedding matches version
- [ ] Test semantic search with sample queries: Verify relevant results returned
- [ ] Verify embeddings stored correctly in `content_vector` column (PostgreSQL query)
- [ ] Test semantic search performance: <500ms for similarity search with 1000+ documents
- [ ] Validate ivfflat index usage: `EXPLAIN ANALYZE` shows index scan (not seq scan)
- [ ] Document validation results in validation report

**Validation:**

```bash
# Run semantic search tests
pytest apps/api/tests/integration/test_pgvector.py -v

# Check embedding storage in database
docker exec -it agentlab-postgres-1 psql -U agentlab -d agentlab -c "
SELECT COUNT(*) as total_docs,
       COUNT(content_vector) as docs_with_embeddings,
       COUNT(*) - COUNT(content_vector) as docs_without_embeddings
FROM document;
"
# Expected: docs_with_embeddings = total_docs (100% coverage)
```

---

#### AC5: All 33 Epic 2 API Endpoints Tested

**Priority:** P1-Critical (Integration point validation)

- [ ] Run full Epic 2 test suite: `pytest apps/api/tests/ -v --tb=short`
- [ ] Verify all client management endpoints passing (5 endpoints)
- [ ] Verify all service management endpoints passing (5 endpoints)
- [ ] Verify all contact management endpoints passing (2 endpoints)
- [ ] Verify all service categories endpoints passing (2 endpoints)
- [ ] Verify all project management endpoints passing (7 endpoints)
- [ ] Verify all workflow management endpoints passing (4 endpoints)
- [ ] Verify all document management endpoints passing (8 endpoints)
- [ ] Test integration flows: Client → Service → Project → Workflow → Document (end-to-end)
- [ ] Test CASCADE delete operations: Verify referential integrity
- [ ] Document API test results: 175+ tests passing, 0 failures
- [ ] Generate test coverage report: Verify ≥80% coverage maintained

**Validation:**

```bash
# Run full Epic 2 API test suite
pytest apps/api/tests/ -v --cov=apps/api --cov-report=term-missing

# Expected: 175+ tests passing
# Expected: Coverage ≥80%
# Expected: 0 failures, 0 errors
```

---

#### AC6: Seed Data and Workflow Templates Validated

**Priority:** P1-Critical (Epic 3 depends on seed data)

- [ ] Verify 3-5 sample clients present in database
- [ ] Verify 10-15 sample services present in database
- [ ] Verify 20-25 sample projects present in database
- [ ] Verify BMAD workflow templates configured correctly (8 stages)
- [ ] Test sample workflow progressions: discovery → production_monitoring
- [ ] Validate foreign key relationships: All seed data properly linked
- [ ] Verify data integrity constraints: No orphaned records
- [ ] Test seed data script: `python -m apps.api.scripts.seed_data` (if exists)
- [ ] Document seed data inventory in validation report

**Validation:**

```bash
# Check seed data counts
docker exec -it agentlab-postgres-1 psql -U agentlab -d agentlab -c "
SELECT
  (SELECT COUNT(*) FROM client) as clients,
  (SELECT COUNT(*) FROM service) as services,
  (SELECT COUNT(*) FROM project) as projects,
  (SELECT COUNT(*) FROM workflow_event) as workflow_events;
"

# Expected:
# clients: 3-5
# services: 10-15
# projects: 20-25
# workflow_events: 50+

# Verify BMAD workflow template
python -c "
from apps.api.core.workflow_templates import load_workflow_template
template = load_workflow_template('bmad_method')
print(f'Template: {template.template_name}')
print(f'Stages: {len(template.stages)}')
assert len(template.stages) == 8, 'BMAD template must have 8 stages'
print('✅ BMAD workflow template valid')
"
```

---

#### AC7: Async Driver Configuration Fixed

**Priority:** P1-Critical (Blocks all Epic 3 integration tests)

- [ ] Diagnose current async driver configuration issue
- [ ] Update `TEST_DATABASE_URL` to use `postgresql+asyncpg://` (async driver)
- [ ] Verify pytest-asyncio installed: `pip list | grep pytest-asyncio`
- [ ] Create/update `pytest.ini` with `asyncio_mode = auto`
- [ ] Update `conftest.py` test_engine fixture to use async driver
- [ ] Update `conftest.py` test_session fixture to use AsyncSession
- [ ] Run Story 2.4 integration tests: `pytest apps/api/tests/integration/test_document_api.py -v`
- [ ] Run Story 2.4 pgvector tests: `pytest apps/api/tests/integration/test_pgvector.py -v`
- [ ] Verify all 12+ Story 2.4 integration tests execute and pass
- [ ] Run full Epic 2 integration test suite: `pytest apps/api/tests/integration/ -v`
- [ ] Update Story 2.4 QA Results: Quality Score 98/100 → 100/100
- [ ] Document async driver fix in validation report

**Validation:**

```bash
# Check DATABASE_URL uses async driver
grep -r "TEST_DATABASE_URL" apps/api/tests/conftest.py apps/api/core/config.py
# Expected: postgresql+asyncpg:// (async driver)

# Run Story 2.4 integration tests
pytest apps/api/tests/integration/test_document_api.py -v
pytest apps/api/tests/integration/test_pgvector.py -v

# Expected: All tests execute and pass (no "async driver" errors)
```

---

#### AC8: Epic 2 → Epic 3 Integration Tests Created

**Priority:** P1-Critical (Validate integration points)

- [ ] Create `apps/api/tests/integration/test_epic_2_to_epic_3.py`
- [ ] Test 1: Epic 3 reads Epic 2 workflow_state JSONB successfully
- [ ] Test 2: Epic 3 creates WorkflowEvent via Epic 2 workflow APIs
- [ ] Test 3: Epic 3 queries documents from Epic 2 document API
- [ ] Test 4: Epic 3 updates project workflow_state via Epic 2 APIs
- [ ] Test 5: Epic 3 Claude Code sync reads/writes Epic 2 documents
- [ ] Add integration tests to CI/CD pipeline (pytest)
- [ ] Run integration tests: `pytest apps/api/tests/integration/test_epic_2_to_epic_3.py -v`
- [ ] Verify all 5+ integration tests passing
- [ ] Document integration test coverage in validation report

**Validation:**

```bash
# Run Epic 2 → Epic 3 integration tests
pytest apps/api/tests/integration/test_epic_2_to_epic_3.py -v

# Expected: 5+ tests passing
# Expected: All Epic 2 → Epic 3 integration points validated
```

---

#### AC9: Migration Validation Script Created

**Priority:** P1-Critical (Prevent future migration issues)

- [ ] Create `apps/api/scripts/validate_migration.py`
- [ ] Implement check: Linear migration history (no branches)
- [ ] Implement check: Current revision matches database state
- [ ] Implement check: All migrations have upgrade/downgrade functions
- [ ] Implement check: Database schema matches SQLAlchemy models
- [ ] Implement check: No orphaned alembic_version entries
- [ ] Make script executable: `chmod +x apps/api/scripts/validate_migration.py`
- [ ] Test script: `python -m apps.api.scripts.validate_migration`
- [ ] Verify script exits 0 on success, exits 1 on failure
- [ ] Document script usage in README or architecture docs

**Validation:**

```bash
# Run migration validation script
python -m apps.api.scripts.validate_migration

# Expected: Exit code 0
# Expected: All validation checks pass
# Expected: Clear success/failure messages
```

---

#### AC10: Migration Validation Added to CI/CD

**Priority:** P1-Critical (Automate validation)

- [ ] Update `.github/workflows/ci.yml` (or equivalent CI config)
- [ ] Add step: "Validate Alembic Migration Consistency"
- [ ] Step runs: `python -m apps.api.scripts.validate_migration`
- [ ] Pipeline fails if migration validation fails (exit code 1)
- [ ] Test pipeline: Create intentional migration issue, verify CI fails
- [ ] Test pipeline: Fix issue, verify CI passes
- [ ] Document CI/CD migration validation in architecture docs
- [ ] Ensure migration validation runs on every pull request

**Validation:**

```bash
# Check CI/CD configuration includes migration validation
grep -A 5 "validate_migration" .github/workflows/ci.yml

# Expected: migration validation step present
# Expected: Runs on every PR
```

---

### Category 2: Epic 3 Technical Foundation (1 criterion)

#### AC11: Epic 3 External Dependency Versions Documented

**Priority:** P1-Critical (Prevent version conflicts)

- [ ] Research MCP Protocol latest stable version
- [ ] Research Python MCP SDK version compatible with MCP Protocol
- [ ] Research OpenAI Python library latest stable version (openai==1.x.x)
- [ ] Research Anthropic Python library latest stable version (anthropic==0.x.x)
- [ ] Research OLLAMA version (if using local LLM)
- [ ] Create `docs/EPIC-3-CANONICAL-VERSIONS.md` (similar to Epic 2)
- [ ] Document all Epic 3 dependency versions in canonical doc
- [ ] Update `apps/api/requirements.txt` with pinned versions
- [ ] Verify no version conflicts with Epic 1/2 dependencies
- [ ] Test dependency installation: `pip install -r apps/api/requirements.txt`
- [ ] Document rationale for each version choice

**Canonical Versions to Document:**

```yaml
# Epic 3 External Dependencies (example format)
MCP Protocol: [Specify - e.g., v1.0.0]
Python MCP SDK: [Specify - e.g., mcp==0.9.0]
OpenAI Python Library: openai==1.6.0 (or latest stable)
Anthropic Python Library: anthropic==0.8.0 (or latest stable)
OLLAMA: [Specify version if using]
```

**Validation:**

```bash
# Verify canonical versions document created
cat docs/EPIC-3-CANONICAL-VERSIONS.md

# Verify requirements.txt updated
grep -E "(mcp|openai|anthropic|ollama)" apps/api/requirements.txt

# Test installation
pip install -r apps/api/requirements.txt
# Expected: No conflicts, all dependencies install successfully
```

---

### Category 3: Process & Documentation (8 criteria)

#### AC12: Story 3.1 Developer Handoff Document Created

**Priority:** P2-High (Improves velocity)

- [ ] Create `docs/stories/story-3.1-developer-handoff.md`
- [ ] Use Story 2.1 format as template (12-16 pages)
- [ ] Include story context and user value
- [ ] Include detailed acceptance criteria with code examples
- [ ] Include implementation guidance (models, schemas, endpoints)
- [ ] Include testing strategy (unit, integration, manual)
- [ ] Include dev notes (file locations, pitfalls, performance)
- [ ] Include MCP Protocol integration examples
- [ ] Include OpenAI/Anthropic API setup instructions
- [ ] Include template import parser examples
- [ ] Dev Lead reviews for technical accuracy
- [ ] Estimated page count: 12-16 pages (comprehensive)

---

#### AC13: Story 3.2 Developer Handoff Document Created

**Priority:** P2-High (Improves velocity)

- [ ] Create `docs/stories/story-3.2-developer-handoff.md`
- [ ] Use Story 2.1 format as template (10-14 pages)
- [ ] Include story context: Gate management and human/agent boundaries
- [ ] Include detailed acceptance criteria with UI/API examples
- [ ] Include implementation guidance (gate approval workflow)
- [ ] Include testing strategy (authorization, audit trails, notifications)
- [ ] Include dev notes (coordination with Story 3.3, shared interfaces)
- [ ] Include gate review UI mockups/wireframes (if available)
- [ ] Dev Lead reviews for technical accuracy
- [ ] Estimated page count: 10-14 pages

---

#### AC14: Story 3.3 Developer Handoff Document Created

**Priority:** P2-High (Improves velocity)

- [ ] Create `docs/stories/story-3.3-developer-handoff.md`
- [ ] Use Story 2.1 format as template (10-14 pages)
- [ ] Include story context: Workflow progression engine and state machine
- [ ] Include detailed acceptance criteria with state machine examples
- [ ] Include implementation guidance (progression rules, branching logic)
- [ ] Include testing strategy (state transitions, completion detection)
- [ ] Include dev notes (coordination with Story 3.2, shared interfaces)
- [ ] Include workflow state machine diagram (Mermaid or ASCII)
- [ ] Dev Lead reviews for technical accuracy
- [ ] Estimated page count: 10-14 pages

---

#### AC15: Story 3.4 Developer Handoff Document Created

**Priority:** P2-High (Improves velocity)

- [ ] Create `docs/stories/story-3.4-developer-handoff.md`
- [ ] Use Story 2.1 format as template (10-14 pages)
- [ ] Include story context: Claude Code directory synchronization
- [ ] Include detailed acceptance criteria with sync examples
- [ ] Include implementation guidance (bidirectional sync, conflict detection)
- [ ] Include testing strategy (conflict scenarios, large files, network issues)
- [ ] Include dev notes (file system operations, performance considerations)
- [ ] Include sync conflict resolution UI/workflow
- [ ] Dev Lead reviews for technical accuracy
- [ ] Estimated page count: 10-14 pages

---

#### AC16: Story 3.5 Developer Handoff Document Created

**Priority:** P2-High (Improves velocity)

- [ ] Create `docs/stories/story-3.5-developer-handoff.md`
- [ ] Use Story 2.1 format as template (12-16 pages)
- [ ] Include story context: Conversational agent interface with LLM providers
- [ ] Include detailed acceptance criteria with conversation examples
- [ ] Include implementation guidance (LLM provider abstraction, context management)
- [ ] Include testing strategy (response quality, token tracking, failover)
- [ ] Include dev notes (prompt engineering, cost optimization, caching)
- [ ] Include LLM provider comparison (OpenAI vs Anthropic vs OLLAMA)
- [ ] Dev Lead reviews for technical accuracy
- [ ] Estimated page count: 12-16 pages

---

#### AC17: Epic 3 Dependency Map Created

**Priority:** P2-High (Enable parallel execution)

- [ ] Create visual dependency map (Mermaid diagram)
- [ ] Document Story 3.0 (Prerequisites) → Story 3.1 dependency
- [ ] Document Story 3.1 → Stories 3.2, 3.3, 3.5 dependencies
- [ ] Document Stories 3.2, 3.3 → Story 3.4 dependencies
- [ ] Identify hard dependencies (blocking)
- [ ] Identify soft dependencies (coordination required)
- [ ] Document parallel execution opportunities (Stories 3.2/3.3)
- [ ] Define coordination plan for parallel stories (daily syncs, shared interface)
- [ ] Add dependency map to Epic 3 Sprint Planning document
- [ ] Team reviews and understands dependency structure

**Dependency Map:**

```mermaid
graph TD
    P0[Story 3.0: Prerequisites] --> S1[Story 3.1: BMAD Template Import & External Service Setup]
    S1 --> S2[Story 3.2: Gate Management]
    S1 --> S3[Story 3.3: Workflow Progression Engine]
    S1 --> S5[Story 3.5: Conversational Agent Interface]
    S2 --> S4[Story 3.4: Claude Code Directory Sync]
    S3 --> S4

    style P0 fill:#ff9999
    style S1 fill:#99ccff
    style S2 fill:#99ff99
    style S3 fill:#99ff99
    style S4 fill:#ffff99
    style S5 fill:#ff99ff
```

---

#### AC18: Story Template Updated with Quality Gap Analysis

**Priority:** P2-High (Process improvement)

- [ ] Create/update story template in `.bmad-core/templates/story-tmpl.yaml` (if exists)
- [ ] Add "Quality Gap Analysis" section to template
- [ ] Add "Quality Score Threshold" to Definition of Done (≥95/100)
- [ ] Create quality score tracking spreadsheet (Google Sheets or Excel)
- [ ] Add columns: Story ID, Quality Score, Missing Points, Gap Analysis, Remediation Tasks
- [ ] Train team on quality gap analysis process (30-minute session)
- [ ] Document quality gap analysis workflow in architecture docs
- [ ] Update Definition of Done with quality threshold

**Updated Definition of Done (example):**

```markdown
## Definition of Done

- [ ] All acceptance criteria met (verified by QA)
- [ ] Test coverage ≥80% (unit + integration)
- [ ] Code review approved (no blocking comments)
- [ ] Documentation updated (API docs, architecture docs)
- [ ] **Quality score ≥95/100** (if <95, create remediation tasks before next story)
- [ ] QA gate passed (no P1 or P2 bugs)
- [ ] Migration validation passed (if database changes)
```

---

#### AC19: Story Template Updated with Migration Validation

**Priority:** P2-High (Process improvement)

- [ ] Create/update story template with migration validation section
- [ ] Add migration validation checklist to template
- [ ] Document migration validation process (step-by-step)
- [ ] Add migration validation to Definition of Done
- [ ] Create migration best practices guide
- [ ] Train team on migration validation (15-minute session)

**Migration Validation Template (example):**

```markdown
## Acceptance Criteria

### Database Migration (if applicable)

X. **Alembic Migration Created and Validated**

- Migration file created: `alembic/versions/YYYYMMDD_HHMM_story_X_X_description.py`
- Migration includes:
  - Upgrade function: Creates/modifies schema
  - Downgrade function: Reverts changes
  - Clear docstring describing changes
- Migration validation:
  - `alembic upgrade head` executes without errors
  - `alembic downgrade -1` reverts cleanly
  - `alembic history` shows linear progression
  - `python -m apps.api.scripts.validate_migration` passes
- Test data compatibility:
  - Existing seed data remains valid after migration
- Performance validation:
  - Migration completes in <30 seconds
```

---

### Category 4: Validation & Sign-off (2 criteria)

#### AC20: Prerequisites Validation Report Created

**Priority:** P1-Critical (Sign-off requirement)

- [ ] Create validation report: `docs/qa/assessments/epic-3-prerequisites-validation-report.md`
- [ ] Document all Epic 2 technical validation results (AC1-AC10)
- [ ] Document all Epic 3 technical foundation results (AC11)
- [ ] Document all process & documentation results (AC12-AC19)
- [ ] Include test execution summaries (pass rates, coverage)
- [ ] Include quality score updates (Stories 2.3, 2.4 → 100/100)
- [ ] Include migration validation results
- [ ] Include async driver configuration fix details
- [ ] Include external dependency version documentation
- [ ] Sign-off section for Dev Lead, QA, and Product Owner

---

#### AC21: Story 3.0 Completion Sign-off

**Priority:** P1-Critical (Epic 3 gate)

- [ ] All 21 acceptance criteria met and verified
- [ ] Prerequisites validation report approved by Dev Lead
- [ ] Prerequisites validation report approved by QA Engineer (Quinn)
- [ ] Prerequisites validation report approved by Product Owner (Sarah)
- [ ] Epic 3 Sprint 1 planning meeting scheduled
- [ ] Team confirms readiness to start Story 3.1
- [ ] Story 3.0 marked as Done ✅

---

## Tasks / Subtasks

### Task 1: Epic 2 Quality Gap Resolution (AC1, AC7)

**Owner:** Dev Lead
**Estimated Effort:** 3-5 hours

**Subtasks:**

- [ ] **Task 1.1: Fix Story 2.3 Gate Timing Logic** (AC1)
  - [ ] Run failing test with verbose output: `pytest apps/api/tests/integration/test_workflow_api.py::test_complete_workflow_lifecycle -vv -s`
  - [ ] Review test code and identify race condition
  - [ ] Review WorkflowService.approve_gate and WorkflowService.advance_stage methods
  - [ ] Implement fix (choose option based on root cause):
    - [ ] Option A: Add explicit transaction commit/refresh in test
    - [ ] Option B: Fix WorkflowService atomic update with flush/commit
    - [ ] Option C: Add transaction isolation to test
  - [ ] Test fix: Run test 10 times, verify all pass
  - [ ] Add regression test: `test_rapid_gate_approval_and_advance`
  - [ ] Run full Story 2.3 integration test suite
  - [ ] Update Story 2.3 QA Results: 99/100 → 100/100

- [ ] **Task 1.2: Fix Async Driver Configuration** (AC7)
  - [ ] Check current TEST_DATABASE_URL in conftest.py and config.py
  - [ ] Update to `postgresql+asyncpg://agentlab:agentlab@localhost:5434/agentlab_test`
  - [ ] Verify pytest-asyncio installed: `pip list | grep pytest-asyncio`
  - [ ] Create/update pytest.ini with `asyncio_mode = auto`
  - [ ] Update conftest.py test_engine fixture for async driver
  - [ ] Update conftest.py test_session fixture to use AsyncSession
  - [ ] Run Story 2.4 integration tests
  - [ ] Run full Epic 2 integration test suite
  - [ ] Update Story 2.4 QA Results: 98/100 → 100/100

---

### Task 2: Epic 2 Technical Validation (AC2-AC6)

**Owner:** Dev Lead + QA Engineer (Quinn)
**Estimated Effort:** 4-6 hours

**Subtasks:**

- [ ] **Task 2.1: Validate Alembic Migration Consistency** (AC2)
  - [ ] Run `alembic history | grep -E "^[a-f0-9]{12}"` and count migrations
  - [ ] Run `alembic current` and verify matches latest migration
  - [ ] Query alembic_version table and verify 1 row
  - [ ] Validate all Epic 2 migrations present (2.1-2.5)
  - [ ] Run `alembic downgrade -1` and verify clean rollback
  - [ ] Run `alembic upgrade head` and verify restore
  - [ ] Document migration state

- [ ] **Task 2.2: Validate Workflow Event Audit Trail** (AC3)
  - [ ] Code review: All workflow state mutation paths
  - [ ] Verify WorkflowEvent creation in advance_stage, approve_gate, reject_gate
  - [ ] Add missing integration tests (manual_override, gate_reapproval, concurrent_updates)
  - [ ] Run workflow event test suite
  - [ ] Document validation results

- [ ] **Task 2.3: Validate Semantic Search** (AC4)
  - [ ] Run pgvector integration tests
  - [ ] Test bulk document operations (100 documents)
  - [ ] Test semantic search performance (<500ms)
  - [ ] Verify ivfflat index usage with EXPLAIN ANALYZE
  - [ ] Document validation results

- [ ] **Task 2.4: Test All 33 Epic 2 API Endpoints** (AC5)
  - [ ] Run full Epic 2 test suite: `pytest apps/api/tests/ -v`
  - [ ] Test integration flows (end-to-end)
  - [ ] Test CASCADE delete operations
  - [ ] Generate test coverage report (≥80%)
  - [ ] Document API test results (175+ tests passing)

- [ ] **Task 2.5: Validate Seed Data and Workflow Templates** (AC6)
  - [ ] Query database: Count clients, services, projects, workflow_events
  - [ ] Verify BMAD workflow template (8 stages)
  - [ ] Test sample workflow progressions
  - [ ] Validate data integrity (no orphaned records)
  - [ ] Document seed data inventory

---

### Task 3: Epic 3 Technical Foundation (AC8-AC11)

**Owner:** Dev Lead + Winston (Architect)
**Estimated Effort:** 6-8 hours

**Subtasks:**

- [ ] **Task 3.1: Create Epic 2 → Epic 3 Integration Tests** (AC8)
  - [ ] Create `apps/api/tests/integration/test_epic_2_to_epic_3.py`
  - [ ] Write Test 1: Epic 3 reads workflow_state JSONB
  - [ ] Write Test 2: Epic 3 creates WorkflowEvent
  - [ ] Write Test 3: Epic 3 queries documents
  - [ ] Write Test 4: Epic 3 updates workflow_state
  - [ ] Write Test 5: Epic 3 Claude Code sync reads/writes documents
  - [ ] Run integration tests and verify all pass
  - [ ] Add to CI/CD pipeline

- [ ] **Task 3.2: Create Migration Validation Script** (AC9)
  - [ ] Create `apps/api/scripts/validate_migration.py`
  - [ ] Implement check: Linear history
  - [ ] Implement check: Current revision matches database
  - [ ] Implement check: Upgrade/downgrade functions exist
  - [ ] Implement check: Schema matches models
  - [ ] Implement check: No orphaned alembic_version
  - [ ] Make executable and test

- [ ] **Task 3.3: Add Migration Validation to CI/CD** (AC10)
  - [ ] Update .github/workflows/ci.yml
  - [ ] Add migration validation step
  - [ ] Test pipeline with intentional issue
  - [ ] Test pipeline with fix
  - [ ] Document in architecture docs

- [ ] **Task 3.4: Document Epic 3 External Dependency Versions** (AC11)
  - [ ] Research MCP Protocol version
  - [ ] Research Python MCP SDK version
  - [ ] Research OpenAI Python library version
  - [ ] Research Anthropic Python library version
  - [ ] Research OLLAMA version (if using)
  - [ ] Create docs/EPIC-3-CANONICAL-VERSIONS.md
  - [ ] Update apps/api/requirements.txt
  - [ ] Test dependency installation
  - [ ] Document rationale for version choices

---

### Task 4: Story Developer Handoff Documents (AC12-AC16)

**Owner:** Product Owner (Sarah)
**Estimated Effort:** 10-15 hours (2-3 hours per story)

**Subtasks:**

- [ ] **Task 4.1: Create Story 3.1 Developer Handoff** (AC12)
  - [ ] Review Story 2.1 format (use as template)
  - [ ] Draft story context and user value
  - [ ] Draft detailed acceptance criteria (20+ criteria)
  - [ ] Add implementation guidance (MCP setup, API integrations, template parser)
  - [ ] Add testing strategy (unit, integration, manual)
  - [ ] Add dev notes (file locations, pitfalls, performance)
  - [ ] Add code examples for MCP Protocol integration
  - [ ] Dev Lead reviews for technical accuracy
  - [ ] Finalize and save to docs/stories/

- [ ] **Task 4.2: Create Story 3.2 Developer Handoff** (AC13)
  - [ ] Draft story context: Gate management and human/agent boundaries
  - [ ] Draft detailed acceptance criteria (18+ criteria)
  - [ ] Add implementation guidance (gate approval workflow, UI)
  - [ ] Add testing strategy (authorization, audit trails)
  - [ ] Add dev notes (coordination with Story 3.3)
  - [ ] Dev Lead reviews for technical accuracy
  - [ ] Finalize and save

- [ ] **Task 4.3: Create Story 3.3 Developer Handoff** (AC14)
  - [ ] Draft story context: Workflow progression engine
  - [ ] Draft detailed acceptance criteria (16+ criteria)
  - [ ] Add implementation guidance (state machine, progression rules)
  - [ ] Add testing strategy (state transitions, branching)
  - [ ] Add dev notes (coordination with Story 3.2)
  - [ ] Include workflow state machine diagram
  - [ ] Dev Lead reviews for technical accuracy
  - [ ] Finalize and save

- [ ] **Task 4.4: Create Story 3.4 Developer Handoff** (AC15)
  - [ ] Draft story context: Claude Code directory sync
  - [ ] Draft detailed acceptance criteria (15+ criteria)
  - [ ] Add implementation guidance (bidirectional sync, conflict detection)
  - [ ] Add testing strategy (conflict scenarios, large files)
  - [ ] Add dev notes (file system operations)
  - [ ] Dev Lead reviews for technical accuracy
  - [ ] Finalize and save

- [ ] **Task 4.5: Create Story 3.5 Developer Handoff** (AC16)
  - [ ] Draft story context: Conversational agent with LLM providers
  - [ ] Draft detailed acceptance criteria (18+ criteria)
  - [ ] Add implementation guidance (LLM abstraction, context management)
  - [ ] Add testing strategy (response quality, token tracking)
  - [ ] Add dev notes (prompt engineering, cost optimization)
  - [ ] Add LLM provider comparison
  - [ ] Dev Lead reviews for technical accuracy
  - [ ] Finalize and save

---

### Task 5: Process Improvements (AC17-AC19)

**Owner:** Product Owner (Sarah) + Dev Lead
**Estimated Effort:** 3-4 hours

**Subtasks:**

- [ ] **Task 5.1: Create Epic 3 Dependency Map** (AC17)
  - [ ] Create Mermaid diagram showing story dependencies
  - [ ] Document hard dependencies (blocking)
  - [ ] Document soft dependencies (coordination required)
  - [ ] Identify parallel execution opportunities (Stories 3.2/3.3)
  - [ ] Define coordination plan (daily syncs, shared interface design)
  - [ ] Add to Epic 3 Sprint Planning document
  - [ ] Review with team

- [ ] **Task 5.2: Update Story Template with Quality Gap Analysis** (AC18)
  - [ ] Create/update story template in .bmad-core/templates/
  - [ ] Add "Quality Gap Analysis" section
  - [ ] Add quality score threshold to Definition of Done (≥95/100)
  - [ ] Create quality score tracking spreadsheet
  - [ ] Train team (30-minute session)
  - [ ] Document workflow in architecture docs

- [ ] **Task 5.3: Update Story Template with Migration Validation** (AC19)
  - [ ] Add migration validation section to template
  - [ ] Add migration checklist
  - [ ] Document migration validation process
  - [ ] Add to Definition of Done
  - [ ] Create migration best practices guide
  - [ ] Train team (15-minute session)

---

### Task 6: Validation & Sign-off (AC20-AC21)

**Owner:** Dev Lead + QA Engineer (Quinn) + Product Owner (Sarah)
**Estimated Effort:** 2-3 hours

**Subtasks:**

- [ ] **Task 6.1: Create Prerequisites Validation Report** (AC20)
  - [ ] Create docs/qa/assessments/epic-3-prerequisites-validation-report.md
  - [ ] Document Epic 2 technical validation results (AC1-AC10)
  - [ ] Document Epic 3 technical foundation results (AC11)
  - [ ] Document process & documentation results (AC12-AC19)
  - [ ] Include test execution summaries
  - [ ] Include quality score updates (Stories 2.3, 2.4)
  - [ ] Include migration validation results
  - [ ] Include external dependency documentation
  - [ ] Add sign-off section

- [ ] **Task 6.2: Obtain Sign-offs** (AC21)
  - [ ] Dev Lead reviews and signs off validation report
  - [ ] QA Engineer (Quinn) reviews and signs off validation report
  - [ ] Product Owner (Sarah) reviews and signs off validation report
  - [ ] Schedule Epic 3 Sprint 1 planning meeting
  - [ ] Confirm team readiness to start Story 3.1
  - [ ] Mark Story 3.0 as Done ✅

---

## Testing Strategy

### Unit Tests

**Not applicable for Story 3.0** - This is a validation and configuration story with no new code requiring unit tests.

---

### Integration Tests

**Story 3.0 creates integration tests as deliverables:**

1. **Epic 2 → Epic 3 Integration Tests** (AC8, Task 3.1)
   - File: `apps/api/tests/integration/test_epic_2_to_epic_3.py`
   - 5+ tests validating integration points
   - Run with: `pytest apps/api/tests/integration/test_epic_2_to_epic_3.py -v`

2. **Existing Epic 2 Integration Tests** (AC5, AC7)
   - Validate all Epic 2 integration tests now execute with async driver fix
   - Run with: `pytest apps/api/tests/integration/ -v`
   - Expected: All Epic 2 integration tests passing (100%)

---

### Manual Testing

**Story 3.0 requires extensive manual validation:**

1. **Alembic Migration Validation** (AC2)
   - Manual verification of migration history linearity
   - Manual testing of upgrade/downgrade
   - Manual schema drift detection

2. **Seed Data Validation** (AC6)
   - Manual query of database to verify seed data counts
   - Manual verification of BMAD workflow template structure
   - Manual testing of sample workflow progressions

3. **Developer Handoff Document Review** (AC12-AC16)
   - Dev Lead manual review for technical accuracy
   - Product Owner manual review for completeness
   - Team manual review for clarity and usability

4. **CI/CD Pipeline Testing** (AC10)
   - Manual trigger of CI/CD pipeline with intentional migration issue
   - Manual verification of pipeline failure
   - Manual trigger of CI/CD pipeline after fix
   - Manual verification of pipeline success

---

### Test Coverage

**Target:** Not applicable (no new production code)

**Deliverables:**

- 5+ Epic 2 → Epic 3 integration tests created
- All Epic 2 integration tests (40+ tests) executing reliably
- Migration validation script with comprehensive checks

---

## Dev Notes

### Coordination Requirements

**Story 3.0 requires coordination across multiple team members:**

1. **Dev Lead:**
   - Fixes Epic 2 quality gaps (Tasks 1.1, 1.2)
   - Validates Epic 2 technical deliverables (Task 2)
   - Creates Epic 3 technical foundation (Task 3)
   - Reviews all developer handoff documents (Task 4)

2. **QA Engineer (Quinn):**
   - Validates Epic 2 API endpoints (Task 2.4)
   - Validates workflow event audit trail (Task 2.2)
   - Validates semantic search (Task 2.3)
   - Creates prerequisites validation report (Task 6.1)

3. **Product Owner (Sarah):**
   - Creates all 5 Epic 3 developer handoff documents (Task 4)
   - Updates story templates with process improvements (Task 5)
   - Reviews and signs off validation report (Task 6.2)

4. **Architect (Winston):**
   - Documents Epic 3 external dependency versions (Task 3.4)
   - Reviews Epic 3 technical foundation decisions
   - Advises on architecture documentation updates

---

### Time Management

**Story 3.0 estimated: 28-38 hours over 1 week (5 business days)**

**Recommended Schedule:**

**Day 1 (Monday):**

- Task 1: Epic 2 Quality Gap Resolution (3-5 hours) - Dev Lead
- Task 2.1: Alembic Migration Validation (1 hour) - Dev Lead

**Day 2 (Tuesday):**

- Task 2.2-2.5: Epic 2 Technical Validation (3-5 hours) - Dev Lead + QA
- Task 3.4: External Dependency Documentation (1-2 hours) - Winston

**Day 3 (Wednesday):**

- Task 3.1-3.3: Epic 3 Technical Foundation (4-6 hours) - Dev Lead
- Task 4.1: Story 3.1 Handoff Doc (2-3 hours) - Sarah

**Day 4 (Thursday):**

- Task 4.2-4.5: Stories 3.2-3.5 Handoff Docs (8-12 hours) - Sarah (full day)
- Task 5: Process Improvements (3-4 hours) - Sarah + Dev Lead

**Day 5 (Friday):**

- Task 6: Validation & Sign-off (2-3 hours) - Dev Lead + QA + Sarah
- Epic 3 Sprint 1 Planning Meeting (2 hours) - Full team

**Total: 28-38 hours across team**

---

### Common Pitfalls

#### Pitfall 1: Async Driver Fix Breaks Other Tests

**Symptom:** After fixing async driver configuration, some existing tests fail

**Cause:** Tests may have hard dependencies on synchronous driver behavior

**Solution:**

- Search codebase for `postgresql://` (synchronous) and update to `postgresql+asyncpg://`
- Update ALL test fixtures to use async driver
- Verify no mixed sync/async database connections

---

#### Pitfall 2: Story Handoff Docs Take Longer Than Estimated

**Symptom:** Creating 5 developer handoff docs takes >15 hours

**Cause:** Underestimating research, code examples, and review cycles

**Solution:**

- Start with Story 3.1 handoff doc (most complex)
- Use completed 3.1 doc as template for 3.2-3.5
- Parallelize: Sarah drafts while Dev Lead reviews
- Timebox each doc: 3 hours max, defer details to story execution

---

#### Pitfall 3: Migration Validation Script Too Complex

**Symptom:** validate_migration.py takes >4 hours to implement

**Cause:** Attempting to validate too many edge cases

**Solution:**

- Start with 5 core checks (linear history, current revision, schema alignment)
- Defer advanced checks (performance, data integrity) to future enhancement
- Use simple pass/fail output, detailed logging optional

---

#### Pitfall 4: External Dependency Version Conflicts

**Symptom:** OpenAI and Anthropic libraries have conflicting dependencies

**Cause:** Incompatible versions of shared dependencies (pydantic, httpx)

**Solution:**

- Use `pip install openai anthropic --dry-run` to preview conflicts
- Choose library versions that share compatible dependencies
- Document any version constraints in EPIC-3-CANONICAL-VERSIONS.md
- Test installation in clean virtual environment

---

### File Locations

**New Files Created:**

- `docs/stories/story-3.1-developer-handoff.md` (AC12)
- `docs/stories/story-3.2-developer-handoff.md` (AC13)
- `docs/stories/story-3.3-developer-handoff.md` (AC14)
- `docs/stories/story-3.4-developer-handoff.md` (AC15)
- `docs/stories/story-3.5-developer-handoff.md` (AC16)
- `docs/EPIC-3-CANONICAL-VERSIONS.md` (AC11)
- `apps/api/scripts/validate_migration.py` (AC9)
- `apps/api/tests/integration/test_epic_2_to_epic_3.py` (AC8)
- `docs/qa/assessments/epic-3-prerequisites-validation-report.md` (AC20)

**Modified Files:**

- `apps/api/tests/conftest.py` (AC7 - async driver fix)
- `apps/api/core/config.py` (AC7 - TEST_DATABASE_URL)
- `pytest.ini` (AC7 - asyncio_mode)
- `apps/api/requirements.txt` (AC11 - Epic 3 dependencies)
- `.github/workflows/ci.yml` (AC10 - migration validation)
- `docs/stories/2.3.bmad-workflow-state-management.story.md` (AC1 - QA score update)
- `docs/stories/2.4.document-metadata-management.story.md` (AC7 - QA score update)
- `.bmad-core/templates/story-tmpl.yaml` (AC18, AC19 - template updates)
- `docs/epics/epic-3-sprint-planning.md` (AC17 - dependency map)

---

## Change Log

| Date       | Version | Description                                                      | Author     |
| ---------- | ------- | ---------------------------------------------------------------- | ---------- |
| 2025-10-01 | 1.0     | Story 3.0 created from Epic 3 Sprint Planning prerequisites      | Sarah (PO) |
| 2025-10-01 | 1.0     | Integrated Epic 2 Quality Gap Analysis action items (QG-1, QG-2) | Sarah (PO) |
| 2025-10-01 | 1.0     | Added all 21 acceptance criteria with detailed validation steps  | Sarah (PO) |
| 2025-10-01 | 1.0     | Created 6 tasks with detailed subtasks                           | Sarah (PO) |

---

## Related Documents

- **Source:** [Epic 3 Sprint Planning](../epics/epic-3-sprint-planning.md)
- **Source:** [Epic 2 Retrospective: Action Items & Fixes](../qa/assessments/epic-2-retrospective-action-items.md)
- **Source:** [Epic 2 Quality Gap Analysis](../qa/assessments/epic-2-quality-gap-analysis.md)
- **Source:** [Epic 3 Lessons Learned from Epic 2](../epics/epic-3-lessons-learned-from-epic-2.md)
- **Target:** [Story 3.1: BMAD Template Import & External Service Setup](./story-3.1-bmad-template-import-external-service-setup.md) (to be created)
- **Reference:** [Story 2.1 Developer Handoff](./story-2.1-developer-handoff.md) (template for AC12-AC16)
