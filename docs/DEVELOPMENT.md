# Development Workflow Guide

This guide outlines the development workflow, best practices, and conventions for AgentLab.

## Getting Started

### Initial Setup

1. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd agentlab

   # Setup environment
   cp .env.example .env
   # Edit .env with your configuration

   # Install dependencies
   npm install
   ```

2. **Docker Services**
   ```bash
   # Start infrastructure services
   docker-compose up -d postgres redis

   # Verify services are running
   docker-compose ps
   ```

3. **Development Servers**
   ```bash
   # Start all development servers
   npm run dev

   # Or start individually
   npm run dev --workspace=@agentlab/web
   cd apps/api && python -m uvicorn main:app --reload
   ```

## Code Organization

### Monorepo Structure

```
agentlab/
├── apps/
│   ├── web/                 # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/        # Next.js App Router pages
│   │   │   ├── components/ # React components
│   │   │   ├── hooks/      # Custom React hooks
│   │   │   ├── lib/        # Utility libraries
│   │   │   └── types/      # Component-specific types
│   │   └── public/         # Static assets
│   └── api/                # FastAPI backend
│       ├── app/
│       │   ├── routers/    # API route handlers
│       │   ├── models/     # Database models
│       │   ├── services/   # Business logic
│       │   └── utils/      # Utility functions
│       └── tests/          # Backend tests
├── packages/
│   ├── types/              # Shared TypeScript types
│   ├── ui/                 # Shared UI components
│   └── utils/              # Shared utilities
└── docs/                   # Documentation
```

### Naming Conventions

**TypeScript/React (Frontend)**
- Components: `PascalCase` (`ProjectCard`, `UserProfile`)
- Files: `kebab-case` (`project-card.tsx`, `user-profile.tsx`)
- Functions: `camelCase` (`handleSubmit`, `fetchUserData`)
- Constants: `UPPER_SNAKE_CASE` (`API_BASE_URL`, `MAX_RETRY_ATTEMPTS`)

**Python (Backend)**
- Classes: `PascalCase` (`ProjectService`, `UserRepository`)
- Files: `snake_case` (`project_service.py`, `user_repository.py`)
- Functions: `snake_case` (`create_project`, `get_user_by_id`)
- Constants: `UPPER_SNAKE_CASE` (`DATABASE_URL`, `JWT_SECRET`)

## Development Commands

### Workspace Commands

```bash
# Root level commands (affect all workspaces)
npm run dev              # Start all development servers
npm run build            # Build all packages
npm run test             # Run all tests
npm run lint             # Lint all code
npm run type-check       # Type check all TypeScript

# Individual workspace commands
npm run dev --workspace=@agentlab/web     # Frontend only
npm run build --workspace=@agentlab/ui    # UI package only
npm run test --workspace=@agentlab/utils  # Utils tests only
```

### Code Quality Commands

```bash
# Linting
npm run lint                    # Check all files
npm run lint:fix               # Fix auto-fixable issues
eslint src --ext .ts,.tsx      # Lint specific directory

# Formatting
npm run format                 # Format all files
npm run format:check          # Check if files are formatted
prettier --write src/         # Format specific directory

# Type Checking
npm run type-check            # Check all TypeScript
tsc --noEmit                  # Check current directory
```

## Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Conventional Commits

Use the conventional commit format for all commits:

```bash
# Format: type(scope): description

# Types:
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting, missing semicolons, etc.
refactor: code change that neither fixes a bug nor adds a feature
test: adding missing tests
chore: updating build tasks, package manager configs, etc.

# Examples:
git commit -m "feat(auth): add user authentication system"
git commit -m "fix(api): resolve validation error in user endpoint"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(utils): extract common validation functions"
```

### Pre-commit Hooks

Husky automatically runs before each commit:

```bash
# What runs automatically:
1. ESLint check and fix
2. Prettier formatting
3. Type checking
4. Basic tests (if configured)

# To bypass (use sparingly):
git commit --no-verify -m "emergency fix"
```

## Testing Strategy

### Frontend Testing

```bash
# Test structure
apps/web/src/
├── components/
│   └── __tests__/           # Component tests
├── hooks/
│   └── __tests__/           # Hook tests
└── __tests__/               # Page and integration tests

# Running tests
npm run test --workspace=@agentlab/web
npm run test:watch --workspace=@agentlab/web
npm run test:coverage --workspace=@agentlab/web
```

### Backend Testing

```bash
# Test structure
apps/api/
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test data

# Running tests
cd apps/api
pytest                      # Run all tests
pytest tests/unit          # Run unit tests only
pytest --cov=app          # Run with coverage
pytest -v                 # Verbose output
```

### E2E Testing

```bash
# Playwright tests
npx playwright test         # Run all E2E tests
npx playwright test --ui    # Run with UI mode
npx playwright codegen     # Generate test code
```

## Environment Management

### Local Development

```bash
# Environment files
.env                    # Local development (never commit)
.env.example           # Template file (commit this)
.env.test             # Test environment
.env.production       # Production template
```

### Environment Variables

```bash
# Development
NODE_ENV=development
LOG_LEVEL=debug
BMAD_DEBUG=true

# API Configuration
CLAUDE_API_KEY=your_key_here
DATABASE_URL=postgresql://localhost:5432/agentlab
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=development_secret
SESSION_SECRET=development_session_secret
```

## Database Development

### Migrations

```bash
# PostgreSQL migrations (using Alembic)
cd apps/api
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Database Reset

```bash
# Reset local database
docker-compose down
docker volume rm agentlab_postgres_data
docker-compose up -d postgres
# Run migrations
```

## Debugging

### Frontend Debugging

```bash
# Next.js debugging
npm run dev               # Starts with debugger attached
# Use browser dev tools
# React Developer Tools extension
```

### Backend Debugging

```bash
# FastAPI debugging
cd apps/api
python -m debugpy --listen 5678 --wait-for-client -m uvicorn main:app --reload

# Or with VS Code launch configuration
# See .vscode/launch.json
```

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's running on ports
   lsof -i :3000  # Frontend
   lsof -i :8000  # Backend
   lsof -i :5432  # PostgreSQL
   ```

2. **Node Modules Issues**
   ```bash
   # Clean install
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Docker Issues**
   ```bash
   # Reset Docker environment
   docker-compose down -v
   docker system prune -a
   docker-compose up -d
   ```

## Performance

### Frontend Optimization

- Use Next.js built-in optimization
- Implement code splitting
- Optimize images with next/image
- Use React Query for efficient data fetching

### Backend Optimization

- Implement database query optimization
- Use Redis for caching
- Implement rate limiting
- Monitor with structured logging

## Security Checklist

- [ ] Never commit secrets or API keys
- [ ] Use environment variables for configuration
- [ ] Implement proper input validation
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Regular dependency updates
- [ ] Security headers configured

## Deployment

### Development Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d
```

---

For additional help, see the [troubleshooting guide](./TROUBLESHOOTING.md) or create an issue in the repository.