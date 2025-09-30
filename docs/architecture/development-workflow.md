# Development Workflow

## Local Development Setup

### Prerequisites

```bash
# Install Node.js 18+ and Python 3.11.5
# Install Docker and Docker Compose
# Install global dependencies
npm install -g pnpm  # Optional: faster package manager
```

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd agentlab

# Install dependencies (root + all workspaces)
npm install

# Copy environment files
cp .env.example .env
cp apps/web/.env.local.example apps/web/.env.local

# Start infrastructure services
docker-compose up -d postgres redis

# Initialize database
cd apps/api
python -m alembic upgrade head
cd ../..

# Return to root and start development
npm run dev
```

### Development Commands

```bash
# Start all services
npm run dev

# Start frontend only
npm run dev:web

# Start backend only
npm run dev:api

# Run tests
npm run test           # All tests
npm run test:web       # Frontend tests only
npm run test:api       # Backend tests only

# Linting and formatting
npm run lint           # Lint all workspaces
npm run format         # Format all code

# Database operations
cd apps/api
python -m alembic revision --autogenerate -m "description"
python -m alembic upgrade head
```

## Environment Configuration

### Required Environment Variables

#### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
```

#### Backend (.env)

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/agentlab
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret
```

#### OpenAI API (optional)

```bash
OPENAI_API_KEY=your-openai-key
```

#### OLLAMA (optional, for local LLM)

```bash
OLLAMA_BASE_URL=http://localhost:11434
```

#### MCP Configuration

```bash
CLAUDE_CODE_MCP_URL=ws://localhost:3001/mcp
```

#### Shared

```bash
LOG_LEVEL=info
ENVIRONMENT=development
```

## Hot Reload and Development Experience

- **Frontend:** Next.js with fast refresh for instant UI updates
- **Backend:** FastAPI with auto-reload for API changes
- **Database:** Automatic migration detection and application
- **Types:** Shared types with TypeScript project references for instant type checking
- **Containers:** Development containers with volume mounts for code changes

## Development Database Management

```bash
# Reset database (caution: destroys data)
docker-compose down postgres
docker volume rm agentlab_postgres_data
docker-compose up -d postgres

# Run database migrations
cd apps/api
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "add new feature"

# Seed development data
python scripts/seed_dev_data.py
```

---

[← Back to Project Structure](project-structure.md) | [Architecture Index](index.md) | [Next: Deployment Architecture →](deployment-architecture.md)
