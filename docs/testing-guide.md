# AgentLab Testing Guide

## Overview

This guide provides comprehensive documentation for testing in the AgentLab project, including unit tests, integration tests, end-to-end tests, and best practices.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Mock Services](#mock-services)
- [Test Environment](#test-environment)
- [Coverage Requirements](#coverage-requirements)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Testing Philosophy

AgentLab follows the testing pyramid strategy:

- **70% Unit Tests**: Fast, isolated tests for business logic
- **20% Integration Tests**: API endpoints and service interactions
- **10% E2E Tests**: Critical user workflows

## Test Types

### Unit Tests

Test isolated components, functions, and classes without external dependencies.

### Integration Tests

Test API endpoints, database operations, and service interactions.

### End-to-End Tests

Test complete user workflows across the full application stack.

## Running Tests

### Run All Tests

```bash
npm test
```

### Backend Tests Only

```bash
cd apps/api
pytest
```

### Frontend Tests Only

```bash
cd apps/web
npx vitest run
```

### E2E Tests Only

```bash
npm run test:e2e
```

### With Coverage

```bash
# Backend
cd apps/api
pytest --cov=. --cov-report=html

# Frontend
cd apps/web
npx vitest run --coverage
```

## Backend Testing

### Framework: pytest + pytest-asyncio

### Directory Structure

```
apps/api/tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/          # Test data fixtures
│   ├── llm/          # LLM response fixtures
│   └── mcp/          # MCP workflow fixtures
└── mocks/            # Mock services
    ├── llm/          # Mock LLM providers
    └── mcp/          # Mock MCP server
```

### Writing Backend Tests

**Unit Test Example:**

```python
import pytest
from models.database import Client

@pytest.mark.unit
def test_client_creation():
    """Test creating a client model."""
    client = Client(
        name="Test Client",
        business_domain="technology"
    )
    assert client.name == "Test Client"
    assert client.business_domain == "technology"
```

**Integration Test Example:**

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_create_client(test_client: AsyncClient):
    """Test creating a client via API."""
    response = await test_client.post(
        "/api/v1/clients",
        json={"name": "Test Client", "business_domain": "technology"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Client"
```

### Fixtures Available

- `test_client`: HTTP client with database override
- `db_session`: Test database session
- `test_settings`: Test configuration settings
- `test_engine`: Test database engine

## Frontend Testing

### Framework: Vitest + React Testing Library

### Directory Structure

```
apps/web/src/
├── __tests__/         # Test utilities
│   ├── setup.ts       # Test setup
│   ├── test-utils.tsx # Custom render utilities
│   └── mocks/         # MSW handlers
└── components/
    ├── Button.tsx
    └── __tests__/
        └── Button.test.tsx
```

### Writing Frontend Tests

**Component Test Example:**

```tsx
import { render, screen } from '@/__tests__/test-utils';
import { Button } from '../Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await userEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

## End-to-End Testing

### Framework: Playwright

### Directory Structure

```
e2e/
├── tests/             # E2E test specs
├── fixtures/          # Test data
└── playwright.config.ts
```

### Writing E2E Tests

**Example:**

```typescript
import { test, expect } from '@playwright/test';

test.describe('API Health Check', () => {
  test('should return healthy status', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/health');
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body.status).toBe('healthy');
  });
});
```

### Running E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug
```

## Mock Services

### Mock LLM Providers

Located in `apps/api/tests/mocks/llm/`:

```python
from tests.mocks.llm import MockClaudeAPI

mock_claude = MockClaudeAPI()
response = await mock_claude.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

See `apps/api/tests/mocks/llm/README.md` for detailed usage.

### Mock MCP Server

Located in `apps/api/tests/mocks/mcp/`:

```python
from tests.mocks.mcp import MockMCPServer

mock_mcp = MockMCPServer()
await mock_mcp.connect()
result = await mock_mcp.read_file("/path/to/file.py")
```

## Test Environment

### Environment Variables

Test environment uses `.env.test`:

```bash
ENVIRONMENT=test
DATABASE_URL=postgresql+asyncpg://agentlab:agentlab@localhost:5434/agentlab
CLAUDE_API_KEY=test_claude_key_mock
```

### Test Database

- **Port**: 5434 (separate from dev on 5432)
- **Docker**: `docker-compose.test.yml`
- **Reset**: `./scripts/db-reset.sh`

### Starting Test Environment

```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Verify services
./scripts/validate-setup.sh
```

## Coverage Requirements

- **Critical Business Logic**: 95% minimum
- **API Endpoints**: 90% minimum
- **UI Components**: 80% minimum
- **Utility Functions**: 100% required

### Viewing Coverage Reports

```bash
# Backend - generates htmlcov/
cd apps/api
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Frontend - generates coverage/
cd apps/web
npx vitest run --coverage
open coverage/index.html
```

## Best Practices

### General Guidelines

1. **Test Behavior, Not Implementation**: Focus on what the code does, not how
2. **Keep Tests Isolated**: Each test should run independently
3. **Use Descriptive Names**: Test names should clearly describe what they test
4. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
5. **Mock External Dependencies**: Use mock services for external APIs

### Backend Best Practices

```python
# Good: Descriptive test name
async def test_create_client_returns_201_and_client_data():
    ...

# Bad: Vague test name
async def test_client():
    ...

# Good: Clear AAA structure
async def test_create_client(test_client):
    # Arrange
    client_data = {"name": "Test", "business_domain": "tech"}

    # Act
    response = await test_client.post("/api/v1/clients", json=client_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

### Frontend Best Practices

```tsx
// Good: Use data-testid for complex queries
<button data-testid="submit-button">Submit</button>;

// Good: Use userEvent for interactions
await userEvent.click(screen.getByRole('button', { name: 'Submit' }));

// Bad: Use fireEvent
fireEvent.click(screen.getByRole('button'));

// Good: Test accessible queries
screen.getByRole('button', { name: 'Submit' });

// Bad: Test implementation details
screen.getByClassName('submit-btn');
```

## Troubleshooting

### Common Issues

**Tests fail with database connection error:**

```bash
# Check if database is running
docker ps | grep postgres

# Start database
docker-compose up -d postgres

# Reset database
./scripts/db-reset.sh
```

**Frontend tests fail with "Cannot find module":**

```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

**E2E tests timeout:**

```bash
# Check if services are running
curl http://localhost:3000
curl http://localhost:8001/api/v1/health

# Start services
npm run dev
```

**Coverage below threshold:**

```bash
# View coverage report
pytest --cov=. --cov-report=term-missing

# Identify missing coverage
# Add tests for uncovered lines
```

### Recovery Scripts

```bash
# Reset Docker environment
./scripts/docker-recovery.sh

# Reset database
./scripts/db-reset.sh

# Clean test artifacts
./scripts/test-cleanup.sh

# Validate setup
./scripts/validate-setup.sh
```

## CI/CD Integration

Tests run automatically on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### CI Workflow

1. Lint check (ESLint + Prettier)
2. Type check (TypeScript + mypy)
3. Backend tests with coverage
4. Frontend tests with coverage
5. E2E tests (on PR only)

### Viewing CI Results

- GitHub Actions tab shows test results
- Coverage reports uploaded to Codecov
- Test artifacts available for download

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Playwright documentation](https://playwright.dev/)
- [React Testing Library](https://testing-library.com/react)
- [MSW (Mock Service Worker)](https://mswjs.io/)

## Support

For testing issues:

1. Check this guide first
2. Run `./scripts/validate-setup.sh`
3. Check GitHub Issues
4. Ask in team chat
