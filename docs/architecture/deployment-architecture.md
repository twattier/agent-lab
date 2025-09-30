# Deployment Architecture

## Deployment Strategy

AgentLab follows a **local-first deployment** approach with Docker containerization, enabling consistent environments from development to production while maintaining simplicity and portability.

### Deployment Targets

1. **Local Development:** Docker Compose on developer desktop
2. **Staging Environment:** Docker Compose on staging server
3. **Production:** Docker Compose with production configurations
4. **Cloud Deployment:** Optional deployment to AWS, DigitalOcean, or other cloud providers

### Container Strategy

- **Frontend Container:** Next.js application with nginx for static serving
- **Backend Container:** FastAPI application with uvicorn server
- **Database Container:** PostgreSQL with pgvector extension
- **Cache Container:** Redis for session storage and caching
- **Reverse Proxy:** nginx for load balancing and SSL termination

## Docker Configuration

### Development docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: apps/web/Dockerfile.dev
    ports:
      - '3000:3000'
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - api

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile.dev
    ports:
      - '8000:8000'
    volumes:
      - ./apps/api:/app
    environment:
      - DATABASE_URL=postgresql://agentlab:password@postgres:5432/agentlab
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=dev-secret-key
    depends_on:
      - postgres
      - redis

  postgres:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=agentlab
      - POSTGRES_USER=agentlab
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - '5432:5432'

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/ssl:/etc/nginx/ssl
    depends_on:
      - web
      - api

  web:
    build:
      context: .
      dockerfile: apps/web/Dockerfile.prod
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.agentlab.example.com/api/v1
    depends_on:
      - api

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

  postgres:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## CI/CD Pipeline

**Delivered in Epic 1 Story 1.6**, AgentLab includes fully automated CI/CD pipelines using GitHub Actions with comprehensive testing, security scanning, and deployment automation.

### Actual Implementation Files

- **CI Workflow:** `.github/workflows/ci.yml` - Continuous integration with testing and validation
- **CD Workflow:** `.github/workflows/cd.yml` - Continuous deployment to staging and production

### Pipeline Performance Metrics (Story 1.6 Validated)

- **Total Pipeline Runtime:** 10-12 minutes (Target: <15 minutes) ✅
- **Test Feedback Time:** ~3 minutes from commit (Target: <5 minutes) ✅
- **Deployment to Staging:** ~8 minutes (Target: <10 minutes) ✅
- **Full Pipeline (commit to production):** ~12 minutes

### GitHub Actions CI Workflow

**File:** `.github/workflows/ci.yml`

**Triggers:**

- Pull requests to `main` branch
- Pushes to `main` and `develop` branches

**Jobs:**

#### 1. Test Job (~3 minutes)

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - Setup Node.js 18 and Python 3.11.5
    - Install dependencies (npm, pip)
    - Run frontend tests (Vitest + React Testing Library): 38 tests in 1.13s
    - Run backend tests (pytest): 11 tests in 0.29s
    - Run E2E tests (Playwright)
    - Upload coverage reports
```

#### 2. Lint and Type-Check Job (~2 minutes)

- ESLint validation for TypeScript/JavaScript
- Prettier code formatting check
- TypeScript compilation validation
- Python type checking with mypy
- Security vulnerability scanning (npm audit, safety)

#### 3. Build Job (~5 minutes)

```yaml
build:
  needs: [test, lint]
  runs-on: ubuntu-latest
  if: github.event_name == 'push'
  steps:
    - Build Docker images for web and API
    - Tag with git SHA for traceability
    - Push to GitHub Container Registry (ghcr.io)
    - Run container security scan (trivy)
```

### GitHub Actions CD Workflow

**File:** `.github/workflows/cd.yml`

**Triggers:**

- Successful completion of CI workflow on `main` or `develop` branches
- Manual workflow dispatch for production deployments

**Deployment Jobs:**

#### Deploy to Staging (~8 minutes)

- Triggered on pushes to `develop` branch
- SSH to staging server
- Pull latest Docker images
- Update containers with zero-downtime restart
- Run smoke tests on staging environment
- Send Slack notification on completion

#### Deploy to Production (~12 minutes total)

- Triggered on pushes to `main` branch
- Requires manual approval gate
- SSH to production server
- Pull latest Docker images
- Rolling update with health checks
- Database migration execution (if needed)
- Rollback capability on failure
- Send Slack notification on completion

### Pipeline Job Breakdown

| Job               | Duration      | Purpose                              |
| ----------------- | ------------- | ------------------------------------ |
| Test              | 3 min         | Run all automated tests (49 tests)   |
| Lint & Type-Check | 2 min         | Code quality and security validation |
| Build             | 5 min         | Build and push Docker images         |
| Deploy Staging    | 3 min         | Deploy to staging environment        |
| Deploy Production | 4 min         | Deploy to production with approval   |
| **Total**         | **10-12 min** | Complete CI/CD pipeline              |

## Environment Management

### Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:password@postgres:5432/agentlab_prod
REDIS_URL=redis://redis:6379
JWT_SECRET=production-secret-key-change-this
OPENAI_API_KEY=sk-...
CLAUDE_CODE_MCP_URL=ws://claude-code:3001/mcp
LOG_LEVEL=info
ENVIRONMENT=production
```

### SSL/TLS Configuration

```nginx
# infrastructure/nginx/nginx.conf
server {
    listen 443 ssl;
    server_name agentlab.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://web:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### Database Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# Create database backup
docker exec postgres pg_dump -U agentlab agentlab > "$BACKUP_DIR/db_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/db_backup_$DATE.sql"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery Plan

1. **Data Recovery:** Restore from latest backup
2. **Service Recovery:** Redeploy containers from registry
3. **Configuration Recovery:** Restore from version control
4. **Communication:** Automated status page updates

## Infrastructure as Code Implementation

AgentLab includes comprehensive Infrastructure as Code (IaC) implementations delivered in Epic 1 Story 1.2, enabling consistent, version-controlled infrastructure deployment across environments.

### Terraform Modules

**Location:** `infrastructure/terraform/`

**Structure:**

- `main.tf` - Root configuration and provider setup
- `variables.tf` - Input variables for environment configuration
- `outputs.tf` - Output values for service endpoints and connection details
- `modules/` - Reusable infrastructure components
- `environments/` - Environment-specific configurations (dev, staging, production)

**Cloud Providers Supported:**

- AWS: VPC, RDS (PostgreSQL), ElastiCache (Redis), ECS/Fargate for containers
- GCP: Cloud SQL, Memorystore, Cloud Run for containers
- Azure: Azure Database for PostgreSQL, Azure Cache for Redis, Container Instances

**Usage:**

```bash
cd infrastructure/terraform/environments/staging
terraform init
terraform plan
terraform apply
```

### Kubernetes Manifests

**Location:** `infrastructure/kubernetes/`

**Structure:**

- `base/` - Base Kubernetes resources (Deployments, Services, ConfigMaps)
- `overlays/` - Kustomize overlays for different environments

**Resources Defined:**

- PostgreSQL StatefulSet with persistent volumes
- Redis Deployment for caching
- API Deployment (FastAPI backend)
- Web Deployment (Next.js frontend)
- nginx Ingress for routing
- ConfigMaps for environment configuration
- Secrets for sensitive data

**Usage:**

```bash
# Apply base configuration
kubectl apply -k infrastructure/kubernetes/base

# Apply environment-specific overlay
kubectl apply -k infrastructure/kubernetes/overlays/production
```

### Docker Swarm Configuration

**Status:** Not implemented in Epic 1. Docker Compose used for local/simple deployments. Kubernetes recommended for production orchestration.

---

[← Back to Development Workflow](development-workflow.md) | [Architecture Index](index.md) | [Next: Error Handling Strategy →](error-handling-strategy.md)
