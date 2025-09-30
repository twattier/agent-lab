# CI/CD Pipeline Guide

## Overview

AgentLab uses GitHub Actions for continuous integration and continuous deployment, ensuring code quality, automated testing, and reliable deployments.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CI Pipeline                          │
│                    (.github/workflows/ci.yml)                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌────────────────┐  ┌─────────────────┐     │
│  │   Lint   │  │ Python Quality │  │ Frontend Tests  │     │
│  └──────────┘  └────────────────┘  └─────────────────┘     │
│       │                │                     │               │
│       │         ┌──────────────┐            │               │
│       ├─────────│ Backend Tests│────────────┤               │
│       │         └──────────────┘            │               │
│       │                │                     │               │
│       └────────────────┴─────────────────────┘               │
│                        │                                      │
│                  ┌──────────┐                                │
│                  │ E2E Tests│                                │
│                  └──────────┘                                │
│                        │                                      │
│                ┌───────────────┐                             │
│                │Security Scan  │                             │
│                └───────────────┘                             │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                         CD Pipeline                          │
│                    (.github/workflows/cd.yml)                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────┐         │
│  │         Build Docker Images (web, api)         │         │
│  └────────────────────────────────────────────────┘         │
│                        │                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │       Security Scan with Trivy (SARIF)         │         │
│  └────────────────────────────────────────────────┘         │
│                        │                                      │
│           ┌────────────┴──────────────┐                      │
│           ▼                           ▼                      │
│  ┌─────────────────┐        ┌──────────────────┐            │
│  │ Deploy Staging  │        │Deploy Production │            │
│  │  (develop branch)│        │  (main branch)   │            │
│  │   Auto-deploy   │        │  Manual approval │            │
│  └─────────────────┘        └──────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## CI Workflow

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Jobs

#### 1. Lint (runs in parallel)
- ESLint validation
- Prettier formatting check
- **Duration:** ~1-2 minutes

#### 2. Python Quality (runs in parallel)
- **black**: Code formatting check
- **isort**: Import sorting validation
- **flake8**: PEP 8 compliance and linting
- **mypy**: Static type checking
- **Duration:** ~2-3 minutes

#### 3. Backend Tests (runs in parallel)
- PostgreSQL service (pgvector)
- pytest with coverage reporting
- Coverage upload to Codecov
- **Duration:** ~3-5 minutes

#### 4. Frontend Tests (runs in parallel)
- Vitest unit tests
- React Testing Library
- Coverage upload to Codecov
- **Duration:** ~2-3 minutes

#### 5. Type Check (runs in parallel)
- TypeScript compilation validation
- **Duration:** ~1-2 minutes

#### 6. E2E Tests (depends on backend-tests, frontend-tests)
- Playwright cross-browser testing
- Full application integration tests
- Test report artifacts
- **Duration:** ~3-5 minutes

#### 7. Security Scan (runs in parallel)
- npm audit for JavaScript dependencies
- Python safety check for PyPI packages
- **Duration:** ~1-2 minutes

**Total CI Pipeline Duration:** ~10-12 minutes

## CD Workflow

### Triggers
- Push to `main` or `develop` branches
- Manual workflow dispatch

### Jobs

#### 1. Build Docker Images
- Multi-stage builds for web and API
- Push to GitHub Container Registry (ghcr.io)
- Docker layer caching for performance
- Image tagging strategy:
  - `branch name` (e.g., `main`, `develop`)
  - `branch-sha` (e.g., `main-abc123`)
  - `latest` (only for main branch)
- **Duration:** ~5-7 minutes

#### 2. Security Scan Images
- Trivy vulnerability scanner
- Scans for CRITICAL and HIGH severity issues
- Uploads SARIF results to GitHub Security
- Runs in parallel for web and API images
- **Duration:** ~2-3 minutes

#### 3. Deploy to Staging (develop branch only)
- Automatic deployment on develop branch
- Docker compose pull and update
- No approval required
- Health check verification
- **Duration:** ~2-3 minutes

#### 4. Deploy to Production (main branch only)
- Manual approval required
- Docker compose pull and update
- Health check verification
- Zero-downtime deployment
- **Duration:** ~3-5 minutes

**Total CD Pipeline Duration (Build + Scan):** ~7-10 minutes
**Total Deployment Time (Staging):** ~10-13 minutes
**Total Deployment Time (Production):** ~13-18 minutes (including approval)

## Docker Multi-Stage Builds

### Frontend (apps/web/Dockerfile.prod)

**Build Stage:**
- Node.js 18.17.0-alpine base image
- npm ci for dependency installation
- Next.js production build

**Production Stage:**
- Node.js 18.17.0-alpine runtime
- Non-root user (nextjs:nodejs)
- Standalone output for minimal size
- **Target Size:** < 200MB

### Backend (apps/api/Dockerfile.prod)

**Build Stage:**
- Python 3.11.5-slim base image
- GCC and build dependencies
- pip install with user flag

**Production Stage:**
- Python 3.11.5-slim runtime
- Non-root user (appuser)
- uvicorn with 4 workers
- Health check endpoint
- **Target Size:** < 150MB

## Deployment Environments

### Staging Environment
- **URL:** https://staging.agentlab.example.com
- **Trigger:** Automatic on push to `develop`
- **Approval:** Not required
- **Purpose:** Pre-production testing and validation

### Production Environment
- **URL:** https://agentlab.example.com
- **Trigger:** Push to `main` branch
- **Approval:** Required (designated reviewers)
- **Purpose:** Live production environment

### Environment Secrets

Both environments require the following secrets:

```bash
# Required Secrets
DATABASE_URL=postgresql://user:password@host:5432/db
REDIS_URL=redis://redis:6379
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=claude-key

# Auto-provided by GitHub
GITHUB_TOKEN=auto-generated
```

## Deployment Scripts

### deploy.sh - Zero-Downtime Deployment

```bash
# Usage
./scripts/deploy.sh [staging|production] [tag]

# Examples
./scripts/deploy.sh staging develop-abc123
./scripts/deploy.sh production main-def456
```

**Features:**
- Health check validation
- Database migration verification
- Rolling update strategy
- Automatic rollback on failure
- Old image cleanup

### rollback.sh - Emergency Rollback

```bash
# Usage
./scripts/rollback.sh [staging|production]

# Examples
./scripts/rollback.sh production
```

**Features:**
- Automatic previous version detection
- Health check verification
- 5-second cancellation window
- Image cleanup after successful rollback

## Rollback Procedures

### Automatic Rollback (Deployment Failure)

If health checks fail during deployment, the deploy.sh script will automatically:
1. Stop new containers
2. Restart previous version containers
3. Verify health checks pass
4. Log rollback details

### Manual Rollback (Post-Deployment Issues)

If issues are discovered after deployment:

1. **Immediate Rollback:**
   ```bash
   ./scripts/rollback.sh production
   ```

2. **Verify Rollback:**
   ```bash
   curl -f https://agentlab.example.com/api/v1/health
   ```

3. **Monitor Logs:**
   ```bash
   docker-compose logs -f web api
   ```

### Rollback from GitHub Actions

1. Navigate to Actions tab
2. Select "CD" workflow
3. Click "Run workflow"
4. Select previous successful commit SHA
5. Approve deployment (for production)

## Troubleshooting

### CI Pipeline Failures

#### Lint Failures
```bash
# Fix ESLint issues
npm run lint --fix

# Fix Prettier formatting
npm run format
```

#### Python Quality Failures
```bash
# Fix black formatting
cd apps/api && black .

# Fix isort imports
cd apps/api && isort .

# Check flake8 issues
cd apps/api && flake8 .

# Check mypy types
cd apps/api && mypy .
```

#### Test Failures
```bash
# Run frontend tests locally
npm run test --workspace=apps/web

# Run backend tests locally
cd apps/api && pytest tests/ -v

# Run E2E tests locally
npm run test:e2e
```

#### Security Scan Warnings
```bash
# Fix npm vulnerabilities
npm audit fix

# Check Python vulnerabilities
cd apps/api && safety check

# Update dependencies
npm update
pip install --upgrade -r requirements.txt
```

### Deployment Failures

#### Image Build Failures
- Check Dockerfile syntax
- Verify base image availability
- Check build context (.dockerignore)
- Review GitHub Actions logs

#### Docker Registry Authentication
```bash
# Login manually
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin
```

#### Health Check Failures
- Check application logs: `docker-compose logs api`
- Verify database connectivity
- Check environment variables
- Test health endpoint manually

#### SSH Deployment Failures
- Verify SSH key configuration
- Check server accessibility
- Verify docker-compose on target server
- Check disk space on target server

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Total CI Pipeline | < 15 minutes | ~10-12 minutes ✅ |
| Test Feedback | < 5 minutes | ~3-5 minutes ✅ |
| Docker Build | < 5 minutes per image | ~3-4 minutes ✅ |
| Staging Deployment | < 10 minutes | ~10-13 minutes ⚠️ |
| Web Image Size | < 200MB | TBD |
| API Image Size | < 150MB | TBD |

## Best Practices

### For Developers

1. **Run tests locally before pushing:**
   ```bash
   npm run test
   npm run lint
   npm run type-check
   ```

2. **Use conventional commit messages:**
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   chore: maintenance tasks
   ```

3. **Keep PRs focused and small**
4. **Wait for CI to pass before requesting review**
5. **Review security scan results**

### For Deployments

1. **Always test in staging first**
2. **Deploy during low-traffic periods**
3. **Monitor logs during deployment**
4. **Keep rollback script ready**
5. **Communicate deployments to team**

### For Rollbacks

1. **Act quickly if issues detected**
2. **Document rollback reason**
3. **Create post-mortem for failures**
4. **Fix root cause before redeploying**

## Emergency Contacts

### Deployment Issues
- **On-Call Engineer:** [Slack: #engineering-oncall]
- **DevOps Lead:** [Slack: #devops]

### Security Issues
- **Security Team:** [Email: security@agentlab.example.com]
- **Incident Response:** [Slack: #security-incidents]

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Multi-Stage Builds](https://docs.docker.com/develop/develop-images/multistage-build/)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)
- [Project Architecture](./architecture/index.md)
- [Testing Strategy](./architecture/testing-strategy.md)

---

**Last Updated:** 2025-09-30
**Maintained By:** DevOps Team
