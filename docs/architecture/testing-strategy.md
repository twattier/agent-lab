# Testing Strategy

## Testing Pyramid

AgentLab follows the testing pyramid approach with emphasis on unit tests, integration tests for critical workflows, and targeted E2E tests for user journeys.

### Test Distribution

- **Unit Tests (70%):** Fast, isolated tests for business logic
- **Integration Tests (20%):** API endpoints and service interactions
- **E2E Tests (10%):** Critical user workflows and Claude Code integration

## Test Organization

### Frontend Tests

```
apps/web/src/
├── __tests__/              # Test utilities and setup
├── components/
│   └── __tests__/          # Component unit tests
├── hooks/
│   └── __tests__/          # Custom hook tests
├── lib/
│   └── __tests__/          # Utility function tests
└── app/
    └── __tests__/          # Page integration tests
```

**Testing Stack:**

- **Framework:** Vitest (fast, Vite-based)
- **Component Testing:** React Testing Library
- **Mocking:** MSW (Mock Service Worker) for API calls
- **Coverage:** Built-in Vitest coverage

### Backend Tests

```
apps/api/
├── tests/
│   ├── unit/               # Service and utility tests
│   ├── integration/        # API endpoint tests
│   ├── fixtures/           # Test data and factories
│   └── conftest.py         # Pytest configuration
├── services/
│   └── __tests__/          # Service unit tests (co-located)
└── repositories/
    └── __tests__/          # Repository tests (co-located)
```

**Testing Stack:**

- **Framework:** pytest with async support
- **HTTP Testing:** httpx for async API calls
- **Database:** Test database with transactions rollback
- **Fixtures:** Factory Boy for test data generation

### E2E Tests

```
e2e/
├── tests/
│   ├── project-workflow.spec.ts    # BMAD workflow E2E
│   ├── claude-code-sync.spec.ts    # MCP integration
│   └── dashboard-navigation.spec.ts # Core UI flows
├── fixtures/
└── playwright.config.ts
```

**Testing Stack:**

- **Framework:** Playwright (cross-browser)
- **Assertions:** Built-in Playwright assertions
- **Data:** API-based test data setup
- **CI/CD:** Parallel execution with sharding

## Test Examples

### Frontend Component Test

```typescript
// components/__tests__/project-card.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from '../project-card';
import { mockProject } from '@agentlab/test-utils';

describe('ProjectCard', () => {
  it('displays project information correctly', () => {
    const project = mockProject({ name: 'Test Project' });

    render(<ProjectCard project={project} />);

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText(project.status)).toBeInTheDocument();
  });

  it('handles click events', () => {
    const onSelect = vi.fn();
    const project = mockProject();

    render(<ProjectCard project={project} onSelect={onSelect} />);

    fireEvent.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith(project.id);
  });
});
```

### Backend API Test

```python
# tests/integration/api/test_projects.py
import pytest
from httpx import AsyncClient
from models.project import Project, CreateProjectRequest

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers):
    """Test project creation endpoint."""
    request_data = {
        "name": "Test Project",
        "description": "Test description",
        "serviceId": "service-uuid",
        "projectType": "new"
    }

    response = await client.post(
        "/api/v1/projects",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    project = Project(**response.json())
    assert project.name == "Test Project"
    assert project.status == "draft"

@pytest.mark.asyncio
async def test_workflow_progression(client: AsyncClient, project_factory):
    """Test BMAD workflow state transitions."""
    project = await project_factory()

    response = await client.post(
        f"/api/v1/projects/{project.id}/workflow/advance",
        json={"toStage": "market_research"}
    )

    assert response.status_code == 200
    updated_project = Project(**response.json())
    assert updated_project.workflow_state.current_stage == "market_research"
```

### E2E Test

```typescript
// e2e/tests/project-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Project Workflow Management', () => {
  test('complete BMAD workflow progression', async ({ page }) => {
    // Login and navigate to dashboard
    await page.goto('/dashboard');
    await page.click('[data-testid="create-project"]');

    // Create new project
    await page.fill('[name="name"]', 'E2E Test Project');
    await page.fill('[name="description"]', 'Test project for E2E');
    await page.selectOption('[name="serviceId"]', { index: 0 });
    await page.click('[type="submit"]');

    // Verify project creation
    await expect(page.locator('[data-testid="project-status"]')).toContainText(
      'draft'
    );

    // Advance through workflow stages
    await page.click('[data-testid="advance-workflow"]');
    await expect(page.locator('[data-testid="current-stage"]')).toContainText(
      'Business Analysis'
    );

    // Complete business analysis gate
    await page.click('[data-testid="approve-gate"]');
    await page.fill(
      '[data-testid="approval-comment"]',
      'Business requirements approved'
    );
    await page.click('[data-testid="submit-approval"]');

    // Verify progression to market research
    await expect(page.locator('[data-testid="current-stage"]')).toContainText(
      'Market Research'
    );
  });
});
```

## Coverage Requirements

- **Critical Business Logic:** 95% coverage minimum
- **API Endpoints:** 90% coverage minimum
- **UI Components:** 80% coverage minimum
- **Utility Functions:** 100% coverage required

## Test Data Management

- **Frontend:** MSW handlers with realistic mock data
- **Backend:** Factory Boy with database fixtures
- **E2E:** API-based setup/teardown for consistent state
- **Shared:** Common test utilities in `@agentlab/test-utils` package

## Implemented Mock Services

Delivered in Epic 1 Story 1.5, AgentLab includes comprehensive mock services for external dependencies, enabling isolated testing without relying on external APIs.

### Mock LLM Providers

**Location:** `apps/api/tests/mocks/llm/`

#### Mock Claude API

**File:** `apps/api/tests/mocks/llm/claude_mock.py`

**Features:**

- Completion and streaming response mocking
- Tool use simulation for workflow automation testing
- Error scenario simulation (rate limits, timeouts, connection failures)
- Response fixtures for common LLM interactions
- Configurable delay and failure injection for reliability testing

#### Mock OpenAI API

**File:** `apps/api/tests/mocks/llm/openai_mock.py`

**Features:**

- Completion and streaming response mocking
- Function calling simulation for fallback provider testing
- Error scenario simulation
- Response fixtures matching OpenAI API format
- Offline development support

#### Mock OLLAMA API

**File:** `apps/api/tests/mocks/llm/ollama_mock.py`

**Features:**

- Local LLM mocking for offline development scenarios
- Model listing simulation
- Completion and streaming support
- Error scenario simulation
- No external dependency testing

### Mock Claude Code MCP Server

**Location:** `apps/api/tests/mocks/mcp/mcp_server_mock.py`

**Features:**

- Python MCP server mock implementing AgentLab protocols
- File synchronization mock operations (read, write, sync)
- Workflow state transition mocking
- Error scenario simulation (connection failures, timeouts)
- Real-time status updates simulation
- Event logging for integration test verification

### Test Execution Metrics

**Total Tests:** 49 tests (delivered in Story 1.5)

- Backend tests: 11 (pytest with async support)
- Frontend tests: 38 (Vitest + React Testing Library)

**Execution Performance:** <2 seconds total for full test suite

- Backend: 0.29 seconds (10 tests)
- Frontend: 1.13 seconds (38 tests)

**Coverage:** 43% baseline (foundation infrastructure)

- Models: 100% coverage
- Health endpoints: 93% coverage
- Target: >80% for critical paths as features are added

### Mock Service Usage

```python
# Example: Using Mock Claude API in tests
from tests.mocks.llm.claude_mock import MockClaudeAPI

async def test_workflow_automation():
    mock_claude = MockClaudeAPI()
    response = await mock_claude.complete(
        prompt="Generate project requirements",
        tools=["file_read", "workflow_advance"]
    )
    assert response.status == "success"
    assert "tool_use" in response.content
```

```python
# Example: Using Mock MCP Server in tests
from tests.mocks.mcp.mcp_server_mock import MockMCPServer

async def test_file_sync():
    mock_mcp = MockMCPServer()
    result = await mock_mcp.sync_file("project.md")
    assert result.synced == True
    assert len(result.events) > 0
```

---

[← Back to Coding Standards](coding-standards.md) | [Architecture Index](index.md) | [Next: Error Handling Strategy →](error-handling-strategy.md)
