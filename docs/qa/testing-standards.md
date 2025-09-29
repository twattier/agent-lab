# AgentLab Testing Standards

**Document Version:** 1.0
**Created:** 2025-09-29
**Author:** Quinn (Test Architect)
**Status:** Active

## Overview

This document establishes comprehensive testing standards for AgentLab development, ensuring consistent quality validation across unit tests, linters, code quality tools, and functional tests for every development cycle per story.

## Testing Pyramid Standards

### Unit Tests (60% of Test Effort)

#### Frontend Unit Testing (React/TypeScript)

**Framework:** Vitest + React Testing Library
**Location:** `apps/web/tests/__tests__/`

**Coverage Requirements:**
- **Business Logic:** 90%+ line coverage
- **React Components:** 80%+ coverage with user interaction testing
- **Utility Functions:** 95%+ coverage including edge cases
- **Custom Hooks:** 85%+ coverage with state management validation

**Standard Test Structure:**
```typescript
// Component Test Example
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ProjectStatusCard } from '@/components/projects/project-status-card'
import { TestProviders } from '../../setup/test-utils'

describe('ProjectStatusCard', () => {
  const mockProject = {
    id: '123',
    name: 'Test Project',
    status: 'active',
    workflowState: { currentStage: 'requirements' }
  }

  it('displays project information correctly', () => {
    render(
      <TestProviders>
        <ProjectStatusCard project={mockProject} />
      </TestProviders>
    )

    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('requirements')).toBeInTheDocument()
  })

  it('handles click events properly', async () => {
    const onClickMock = vi.fn()
    const user = userEvent.setup()

    render(
      <TestProviders>
        <ProjectStatusCard project={mockProject} onClick={onClickMock} />
      </TestProviders>
    )

    await user.click(screen.getByTestId('project-card'))
    expect(onClickMock).toHaveBeenCalledWith(mockProject.id)
  })

  it('handles error states gracefully', () => {
    render(
      <TestProviders>
        <ProjectStatusCard project={null} />
      </TestProviders>
    )

    expect(screen.getByText('No project data')).toBeInTheDocument()
  })
})
```

**Required Test Categories:**
1. **Rendering Tests:** Component displays correctly with valid props
2. **Interaction Tests:** User interactions trigger expected behavior
3. **Error Boundary Tests:** Graceful handling of invalid data/states
4. **Accessibility Tests:** WCAG compliance validation
5. **Performance Tests:** Component render time within limits

#### Backend Unit Testing (Python/FastAPI)

**Framework:** pytest + pytest-asyncio
**Location:** `apps/api/tests/unit/`

**Coverage Requirements:**
- **Service Layer:** 90%+ line coverage
- **Repository Pattern:** 85%+ coverage
- **API Handlers:** 80%+ coverage
- **Utilities:** 95%+ coverage

**Standard Test Structure:**
```python
# Service Test Example
import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock
from services.project_service import ProjectService
from models.project import Project
from exceptions import ValidationError, NotFoundError

class TestProjectService:
    @pytest.fixture
    async def service(self, mock_db, mock_repository):
        return ProjectService(mock_db, mock_repository)

    async def test_create_project_success(self, service, mock_project_data):
        # Arrange
        expected_project = Project(**mock_project_data)
        service.repository.create = AsyncMock(return_value=expected_project)

        # Act
        result = await service.create_project(mock_project_data)

        # Assert
        assert result.name == mock_project_data['name']
        service.repository.create.assert_called_once()

    async def test_create_project_validation_error(self, service):
        # Arrange
        invalid_data = {'name': ''}  # Missing required fields

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.create_project(invalid_data)

        assert 'name' in str(exc_info.value)

    async def test_get_project_not_found(self, service):
        # Arrange
        project_id = str(uuid4())
        service.repository.get = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await service.get_project(project_id)

        assert project_id in str(exc_info.value)
```

**Required Test Categories:**
1. **Business Logic Tests:** Core functionality validation
2. **Validation Tests:** Input validation and sanitization
3. **Error Handling Tests:** Exception scenarios and edge cases
4. **Database Operation Tests:** CRUD operations with mocked DB
5. **Integration Points Tests:** External service interaction mocks

### Integration Tests (30% of Test Effort)

#### API Integration Testing

**Framework:** FastAPI TestClient + pytest
**Location:** `apps/api/tests/integration/`

**Coverage Requirements:**
- **All API Endpoints:** 100% happy path + primary error scenarios
- **Database Operations:** Complete CRUD cycle validation
- **Authentication:** All protected endpoints validated

**Standard Test Structure:**
```python
import pytest
from fastapi.testclient import TestClient
from main import app
from tests.factories import ProjectFactory, ClientFactory

client = TestClient(app)

class TestProjectsAPI:
    def test_create_project_success(self, db_session, auth_headers):
        # Arrange
        client_obj = ClientFactory()
        db_session.add(client_obj)
        db_session.commit()

        project_data = {
            "name": "Test Project",
            "clientId": str(client_obj.id),
            "projectType": "new"
        }

        # Act
        response = client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["workflowState"]["currentStage"] == "init"

    def test_create_project_unauthorized(self, db_session):
        # Test without authentication headers
        response = client.post("/api/v1/projects/", json={})
        assert response.status_code == 401

    def test_list_projects_with_filters(self, db_session, auth_headers):
        # Arrange
        active_project = ProjectFactory(status="active")
        draft_project = ProjectFactory(status="draft")
        db_session.add_all([active_project, draft_project])
        db_session.commit()

        # Act
        response = client.get(
            "/api/v1/projects/?status=active",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["status"] == "active"
```

#### Frontend Integration Testing

**Framework:** React Testing Library + Mock Service Worker (MSW)
**Location:** `apps/web/tests/integration/`

**Standard Test Structure:**
```typescript
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { rest } from 'msw'
import { server } from '../setup/server'
import { ProjectList } from '@/components/projects/project-list'
import { TestProviders } from '../setup/test-utils'

describe('ProjectList Integration', () => {
  it('loads and displays projects from API', async () => {
    // Arrange
    const mockProjects = [
      { id: '1', name: 'Project 1', status: 'active' },
      { id: '2', name: 'Project 2', status: 'draft' }
    ]

    server.use(
      rest.get('/api/v1/projects', (req, res, ctx) => {
        return res(ctx.json(mockProjects))
      })
    )

    // Act
    render(
      <TestProviders>
        <ProjectList />
      </TestProviders>
    )

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Project 1')).toBeInTheDocument()
      expect(screen.getByText('Project 2')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    // Arrange
    server.use(
      rest.get('/api/v1/projects', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }))
      })
    )

    // Act
    render(
      <TestProviders>
        <ProjectList />
      </TestProviders>
    )

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Failed to load projects')).toBeInTheDocument()
    })
  })
})
```

### End-to-End Tests (10% of Test Effort)

#### E2E Testing Framework

**Framework:** Playwright
**Location:** `tests/e2e/`

**Coverage Requirements:**
- **Critical User Journeys:** 100% coverage
- **Cross-Browser:** Chrome, Firefox, Safari
- **Responsive Design:** Desktop and tablet viewports

**Standard Test Structure:**
```typescript
import { test, expect } from '@playwright/test'

test.describe('Project Creation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login setup
    await page.goto('/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-btn"]')
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible()
  })

  test('should create new project successfully', async ({ page }) => {
    // Navigate to project creation
    await page.click('[data-testid="new-project-btn"]')

    // Fill project form
    await page.fill('[data-testid="project-name"]', 'E2E Test Project')
    await page.selectOption('[data-testid="client-select"]', 'test-client')
    await page.selectOption('[data-testid="project-type"]', 'new')

    // Submit and verify
    await page.click('[data-testid="create-project-btn"]')
    await expect(page.locator('text=E2E Test Project')).toBeVisible()

    // Verify project appears in list
    await page.goto('/projects')
    await expect(page.locator('text=E2E Test Project')).toBeVisible()
  })

  test('should validate required fields', async ({ page }) => {
    await page.click('[data-testid="new-project-btn"]')
    await page.click('[data-testid="create-project-btn"]')

    await expect(page.locator('[data-testid="name-error"]'))
      .toContainText('Name is required')
  })
})
```

## Code Quality Standards

### Linting Standards

#### Frontend ESLint Configuration
```json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "plugin:security/recommended",
    "plugin:jsx-a11y/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "security/detect-object-injection": "error",
    "jsx-a11y/alt-text": "error",
    "no-console": "warn",
    "prefer-const": "error"
  }
}
```

#### Backend Python Linting (ruff)
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "S",   # flake8-bandit (security)
    "UP",  # pyupgrade
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
```

### Type Safety Standards

#### TypeScript Configuration
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true
  }
}
```

#### Python Type Checking (mypy)
```ini
[mypy]
python_version = 3.12
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Security Standards

#### Frontend Security Rules
- **Input Sanitization:** All user inputs sanitized before display
- **XSS Prevention:** Content Security Policy headers enforced
- **Authentication:** JWT tokens stored in httpOnly cookies
- **API Security:** All API calls include CSRF protection

#### Backend Security Rules
- **Input Validation:** Pydantic schemas validate all inputs
- **SQL Injection Prevention:** ORM usage, no raw SQL queries
- **Authentication:** JWT token validation on all protected routes
- **Authorization:** Role-based access control enforced

## Functional Testing Standards

### Manual Testing Checklist

#### User Interface Testing
- [ ] **Visual Design:** UI matches design specifications
- [ ] **Responsive Design:** Works on desktop and tablet
- [ ] **Accessibility:** WCAG AA compliance validated
- [ ] **Browser Compatibility:** Chrome, Firefox, Safari testing
- [ ] **Performance:** Page load times under 2 seconds

#### User Experience Testing
- [ ] **Navigation:** All navigation paths work correctly
- [ ] **Forms:** Form validation provides clear feedback
- [ ] **Error Handling:** Error messages are user-friendly
- [ ] **Loading States:** Loading indicators during async operations
- [ ] **Success Feedback:** Clear confirmation of successful actions

#### Business Logic Testing
- [ ] **Workflow Progression:** BMAD workflow stages advance correctly
- [ ] **Data Validation:** Business rules enforced properly
- [ ] **Permissions:** Users can only access authorized features
- [ ] **Audit Trails:** All significant actions are logged
- [ ] **Integration Points:** External services integrate correctly

### Performance Testing Standards

#### Load Testing Requirements

**Normal Load Testing:**
- **Concurrent Users:** 10 users
- **Duration:** 30 minutes
- **Scenarios:** Normal usage patterns

**Peak Load Testing:**
- **Concurrent Users:** 25 users
- **Duration:** 15 minutes
- **Scenarios:** Heavy document processing

**Stress Testing:**
- **Concurrent Users:** 50+ users
- **Duration:** 10 minutes
- **Purpose:** Identify breaking points

#### Performance Benchmarks

| Component | Response Time | Throughput | Success Rate |
|-----------|---------------|------------|--------------|
| Dashboard Load | < 1 second | 100/minute | 99.9% |
| Project Creation | < 2 seconds | 50/minute | 99.5% |
| Document Upload | < 3 seconds | 20/minute | 99.0% |
| Search Operations | < 500ms | 1000/hour | 99.5% |
| MCP File Sync | < 5 seconds | 10 concurrent | 99.0% |

## Continuous Integration Standards

### CI/CD Pipeline Requirements

#### Automated Testing Pipeline
```yaml
# Testing stages that must pass
stages:
  - lint-and-format
  - unit-tests
  - integration-tests
  - security-scan
  - build-verification
  - e2e-tests (on staging)
```

#### Quality Gates in CI/CD

**Pre-merge Requirements:**
- [ ] All linting rules pass
- [ ] Unit test coverage > 85%
- [ ] Integration tests pass
- [ ] Security scan shows no high/critical issues
- [ ] TypeScript compilation succeeds
- [ ] Build process completes successfully

**Pre-deployment Requirements:**
- [ ] E2E tests pass on staging environment
- [ ] Performance benchmarks met
- [ ] Security vulnerabilities addressed
- [ ] Database migrations tested
- [ ] Rollback procedures validated

### Test Data Management

#### Test Data Strategy
- **Unit Tests:** Mock data generated in test files
- **Integration Tests:** Test fixtures with cleanup
- **E2E Tests:** Dedicated test database with seed data
- **Performance Tests:** Production-like data volume

#### Test Environment Management
- **Development:** Local Docker containers
- **Integration:** Shared staging environment
- **E2E Testing:** Isolated test environment
- **Performance:** Production-scale infrastructure

## Quality Metrics and Reporting

### Coverage Reporting

#### Required Coverage Metrics
```typescript
// Jest/Vitest coverage configuration
{
  "collectCoverageFrom": [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/**/*.stories.tsx"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 85,
      "lines": 85,
      "statements": 85
    },
    "src/services/": {
      "lines": 90
    }
  }
}
```

#### Coverage Reporting Format
- **HTML Reports:** For detailed analysis
- **Console Output:** For CI/CD feedback
- **Badge Integration:** README.md coverage badges
- **Trend Tracking:** Coverage over time monitoring

### Quality Dashboards

#### Metrics to Track
- **Test Execution:** Pass/fail rates, execution time
- **Coverage:** Line, branch, function coverage by component
- **Performance:** Response times, throughput, error rates
- **Security:** Vulnerability counts, security scan results
- **Code Quality:** Complexity metrics, maintainability index

#### Reporting Frequency
- **Real-time:** CI/CD pipeline results
- **Daily:** Quality metric summaries
- **Weekly:** Trend analysis and improvement recommendations
- **Monthly:** Comprehensive quality review and planning

## Best Practices and Guidelines

### Test Organization
- **File Naming:** Test files mirror source structure with `.test.` or `.spec.` suffix
- **Test Grouping:** Related tests grouped in describe blocks
- **Test Data:** Shared test utilities and fixtures in dedicated folders
- **Documentation:** Clear test descriptions explaining intent

### Maintenance Standards
- **Test Maintenance:** Tests updated with code changes
- **Flaky Test Management:** Intermittent failures investigated and fixed
- **Test Performance:** Test execution time monitored and optimized
- **Tool Updates:** Testing frameworks and tools kept current

---

**Document Control:**
- **Review Schedule:** Monthly during development, quarterly in maintenance
- **Update Process:** All changes reviewed by Test Architect
- **Compliance:** Standards enforced through automated CI/CD pipeline
- **Training:** Team onboarding includes testing standards overview

*These testing standards ensure comprehensive quality validation for every AgentLab story, supporting the project's productivity enhancement goals through reliable, maintainable software delivery.*