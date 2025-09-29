# Epic 1: Foundation & Infrastructure Setup

## Epic Goal

Establish the foundational development environment, infrastructure, and core project scaffolding for AgentLab, enabling subsequent feature development with a robust, scalable foundation.

## Epic Description

**Project Context:**
AgentLab is a greenfield productivity platform for DSI Product Owners managing 10-25 concurrent AI development projects. This epic establishes the fundamental infrastructure needed to support BMAD Method automation, Claude Code integration, and bilingual document management.

**Epic Scope:**
This epic creates the essential project foundation including:

- Project initialization and repository setup with external service documentation
- Docker-compose containerized development environment
- Core database infrastructure (PostgreSQL + pgvector)
- Basic API framework (FastAPI)
- Frontend foundation (Next.js + TypeScript + shadcn/ui)
- Development tooling and configuration
- CI/CD pipeline setup and automated testing infrastructure

## Stories (6 Total)

1. **Story 1.1:** Project Scaffolding and Repository Setup
   - **Initialize repository with explicit commands:**
     ```bash
     mkdir agentlab && cd agentlab
     git init
     npm init -w apps/web -w apps/api -w packages/types -w packages/ui -w packages/utils
     mkdir -p {apps/{web,api},packages/{types,ui,utils},docs,docker,.github/workflows}
     ```
   - **Create foundational files:**
     - .gitignore (Node.js + Python template)
     - .nvmrc (Node.js 18.17.0)
     - .python-version (Python 3.11.5)
     - .env.example with required environment variables
   - **Configure development tooling with specific versions:**
     - ESLint 8.45.0+ with TypeScript rules
     - Prettier 3.0.0+ with standardized configuration
     - TypeScript 5.1.0+ with strict mode enabled
     - Husky pre-commit hooks for code quality
   - **Create initial README with:**
     - Prerequisites (Docker 24.0+, Node.js 18.17.0, Python 3.11.5)
     - Quick start commands
     - Architecture overview
     - Development workflow
   - **Set up Git workflows:**
     - Branch protection rules for main
     - Initial commit: "feat: initial project scaffolding with monorepo structure"
     - Commit message standards (conventional commits)
     - PR template for code reviews
   - **External service setup documentation (USER ACTIONS REQUIRED):**
     - **Claude API Setup Process:**
       1. Create Anthropic account at console.anthropic.com
       2. Generate API key for AgentLab project
       3. Add CLAUDE_API_KEY to .env file
       4. Test API connectivity with simple ping request
       5. Document rate limits and usage monitoring setup
     - **Optional LLM Provider Setup:**
       1. OpenAI API setup (if using as fallback)
       2. OLLAMA local installation for offline development
       3. Provider selection configuration in environment variables
     - **Credential Security Guidelines:**
       - Never commit API keys to repository
       - Use .env files for local development
       - Use secure environment variable management for production
       - Rotate API keys quarterly for security
   - **API Key Environment Variables:**
     ```bash
     # Required for MCP and LLM integration
     CLAUDE_API_KEY=your_claude_api_key_here
     OPENAI_API_KEY=your_openai_api_key_here  # Optional
     OLLAMA_HOST=http://localhost:11434       # Optional for local LLM
     ```

2. **Story 1.2:** Docker Infrastructure Setup with IaC
   - **Create docker-compose.yml with pinned versions:**
     - PostgreSQL 15.4 with pgvector 0.5.0 extension (CANONICAL VERSION)
     - Redis 7.0-alpine for caching
     - nginx 1.25-alpine for reverse proxy
     - Python 3.11.5-slim base image for API (CANONICAL VERSION)
     - Node.js 18.17.0-alpine for frontend build (CANONICAL VERSION)

     **NOTE:** These versions are the canonical specifications for Epic 1. All architecture documents should align with these versions for foundation infrastructure.

   - **Infrastructure as Code (IaC) implementation:**
     - Terraform modules for cloud deployment (AWS, GCP, Azure)
     - Docker Swarm compose files for production orchestration
     - Kubernetes manifests for container orchestration (optional)
     - Infrastructure versioning and state management
   - **Environment-specific configurations:**
     - docker-compose.dev.yml (development with hot reload)
     - docker-compose.test.yml (testing with test database)
     - docker-compose.prod.yml (production with optimizations)
     - Environment variable templates for each stage
   - **Container networking and security:**
     - Internal network for services communication
     - Port mapping: 3000 (frontend), 8000 (API), 5432 (DB), 6379 (Redis)
     - Health checks for all services with restart policies
     - Security scanning for container vulnerabilities
   - **Volume and data management:**
     - PostgreSQL data persistence with backup volumes
     - Node modules caching optimization
     - Source code hot reload mounting (dev only)
     - Log aggregation and rotation strategy
   - **Deployment strategies definition:**
     - Local development: docker-compose up
     - Staging: Blue-green deployment with health checks
     - Production: Rolling updates with zero-downtime
     - Rollback procedures and database migration handling

3. **Story 1.3:** Backend API Foundation with Dependency Management
   - **Initialize FastAPI with pinned versions:**
     - FastAPI 0.103.0+ for latest features
     - Pydantic 2.0+ for data validation
     - SQLAlchemy 2.0+ with async support
     - Alembic 1.11+ for database migrations
   - **Python dependency conflict resolution:**
     - requirements.txt with exact versions
     - Virtual environment isolation strategy
     - Poetry or pip-tools for dependency management
     - Python version validation (3.11.5)
   - **Database integration with pgvector:**
     - PostgreSQL async driver (asyncpg 0.28+)
     - pgvector Python bindings validation
     - Connection pooling configuration
     - Migration scripts for pgvector extension
   - **MCP protocol preparation:**
     - Python MCP client library integration
     - Claude Code communication framework
     - File synchronization utilities
     - Error handling for external integrations
   - **Backend dependency installation order:**
     1. Python environment and package manager
     2. Core FastAPI and database libraries
     3. pgvector and specialized extensions
     4. Authentication and security packages
     5. MCP and external integration libraries

4. **Story 1.4:** Frontend Foundation Setup with Dependency Management
   - **Initialize Next.js with specific versions:**
     - Next.js 13.4.19+ with App Router
     - TypeScript 5.1.6+ with strict configuration
     - React 18.2.0+ for concurrent features
   - **Configure shadcn/ui component library:**
     - shadcn/ui CLI installation and setup
     - Tailwind CSS 3.3.0+ configuration
     - Radix UI primitives for accessibility
     - Lucide React icons for consistency
   - **Dependency conflict resolution strategy:**
     - Package.json with exact versions for critical dependencies
     - Npm audit and vulnerability checking
     - Peer dependency validation
     - Lock file strategy (npm ci for CI/CD)
   - **Frontend-backend integration setup:**
     - API client configuration with type safety
     - Environment variable management
     - CORS configuration validation
     - Authentication token handling
   - **Critical dependency installation order:**
     1. Next.js and React core
     2. TypeScript and build tools
     3. shadcn/ui and styling frameworks
     4. State management (React Query, Zustand)
     5. Development tools and testing frameworks

5. **Story 1.5:** Testing Infrastructure & Environment Validation
   - **Comprehensive testing framework setup:**
     - pytest 7.4+ for Python backend testing with async support
     - Jest 29+ and React Testing Library for frontend testing
     - Playwright for end-to-end testing across browsers
     - Coverage reporting with 80%+ target for critical paths
   - **Mock services and test data strategy:**
     - **Mock LLM providers** for isolated testing:
       - Claude API mock responses for workflow automation testing
       - OpenAI API mock for fallback provider testing
       - OLLAMA local mock for offline development scenarios
       - Response fixtures for common LLM interactions (completion, streaming)
     - **Mock Claude Code MCP server** for integration testing:
       - Python MCP server mock implementing AgentLab protocols
       - File synchronization mock operations (read, write, sync)
       - Workflow state transition mocking
       - Error scenario simulation (connection failures, timeouts)
       - Real-time status updates simulation
     - **Test database with realistic seed data:**
       - Client/Service/Project hierarchy test fixtures
       - BMAD workflow state samples in various stages
       - Document versioning and change tracking samples
       - Contact and category relationship test data
     - **External API mocking infrastructure:**
       - Wiremock or MSW for HTTP API mocking
       - Docker compose test services with mock endpoints
       - Request/response recording for integration test replay
   - **Test environment management:**
     - docker-compose.test.yml with isolated test services
     - Separate test database with automatic cleanup
     - Test-specific environment variables and configurations
     - CI/CD pipeline integration with test reporting
   - **Development environment validation:**
     - Automated setup verification scripts
     - Health check endpoints for all services
     - Integration test suite covering critical user flows
     - Performance baseline establishment and monitoring
   - **Fallback and recovery procedures:**
     - Docker environment recovery scripts
     - Database reset and migration procedures
     - Test environment cleanup and reset procedures
     - Alternative installation methods if primary fails
   - **Developer onboarding with testing validation:**
     - New developer setup time target: <10 minutes
     - Test suite runs successfully as onboarding verification
     - Documentation includes testing workflow and best practices
     - Setup success criteria including passing test suite

6. **Story 1.6:** CI/CD Pipeline Setup and Automated Testing
   - **GitHub Actions workflow configuration:**
     - .github/workflows/ci.yml for continuous integration
     - .github/workflows/cd.yml for deployment automation
     - Matrix testing across Node.js 18.17.0 and Python 3.11.5
     - Automated testing on pull requests and main branch pushes
   - **Testing automation pipeline:**
     - Backend testing: pytest with coverage reporting
     - Frontend testing: Jest and React Testing Library
     - End-to-end testing: Playwright automation
     - Integration testing: Docker-compose test environment
   - **Code quality automation:**
     - ESLint and Prettier validation on all commits
     - TypeScript compilation validation
     - Python code formatting with black and isort
     - Security vulnerability scanning with npm audit and safety
   - **Build and deployment automation:**
     - Docker image building and tagging
     - Multi-stage builds for production optimization
     - Container security scanning with trivy or similar
     - Automated deployment to staging environment
   - **Deployment strategies implementation:**
     - Pull request preview deployments
     - Staging deployment on merge to main
     - Production deployment approval gates
     - Rollback automation for failed deployments
   - **CI/CD performance targets:**
     - Total pipeline runtime < 15 minutes
     - Test feedback within 5 minutes of commit
     - Deployment to staging < 10 minutes
     - Zero-downtime production deployments

## Success Criteria

### Technical Requirements

- [ ] Docker environment starts cleanly with `docker-compose up` in <2 minutes
- [ ] All specified versions are pinned and validated (Node.js 18.17.0, Python 3.11.5, PostgreSQL 15.4)
- [ ] pgvector extension loads successfully with test queries
- [ ] Database migrations run successfully with rollback capability
- [ ] API health checks pass for all endpoints
- [ ] Frontend renders with authentication flow and API connectivity
- [ ] All containers communicate properly with internal networking
- [ ] MCP protocol preparation framework validates without errors
- [ ] IaC templates (Terraform) validate and deploy successfully
- [ ] Environment-specific configurations (dev/test/prod) work correctly
- [ ] Mock services start and respond to test requests

### Quality Requirements

- [ ] Code follows established linting standards (ESLint 8.45.0+, Prettier 3.0.0+)
- [ ] TypeScript compilation succeeds without errors (strict mode enabled)
- [ ] Comprehensive test suite passes with >80% coverage for critical paths
- [ ] Documentation is comprehensive and accurate with troubleshooting sections
- [ ] Development environment setup takes < 10 minutes (validated with new developers)
- [ ] Dependency conflicts are resolved with documented fallback procedures

### Testing Infrastructure Requirements

- [ ] All testing frameworks installed and configured (pytest, Jest, Playwright)
- [ ] Mock LLM providers respond correctly to test requests with realistic fixtures
- [ ] Mock Claude Code MCP server simulates file sync and workflow operations
- [ ] Test database seeds and resets properly with realistic project data
- [ ] External API mocking infrastructure handles error scenarios gracefully
- [ ] CI/CD pipeline runs full test suite successfully including MCP integration tests
- [ ] Coverage reporting generates and meets 80%+ targets for critical paths
- [ ] End-to-end tests cover critical user workflows including Claude Code integration

### Deployment & Infrastructure Requirements

- [ ] Terraform modules deploy infrastructure without errors
- [ ] Blue-green deployment strategy documented and tested
- [ ] Rollback procedures validated with test deployments
- [ ] Environment-specific configurations tested
- [ ] Security scanning passes for all container images
- [ ] Log aggregation and monitoring baseline established

### Dependency Management Requirements

- [ ] All critical dependencies installed in specified order without conflicts
- [ ] Version compatibility validated between Python and Node.js ecosystems
- [ ] Fallback procedures tested for common installation failures
- [ ] Lock files (package-lock.json, requirements.txt) committed and validated
- [ ] Vulnerability scanning passes for all dependencies

### Integration Requirements

- [ ] Frontend can communicate with backend API
- [ ] Database connectivity confirmed
- [ ] Authentication flow works end-to-end
- [ ] Static assets serve correctly
- [ ] Hot reload functions in development

### CI/CD Pipeline Requirements

- [ ] GitHub Actions workflows run successfully on all commits
- [ ] Automated testing pipeline completes in < 15 minutes
- [ ] Code quality checks pass (ESLint, Prettier, TypeScript, Black)
- [ ] Security vulnerability scanning passes for all dependencies
- [ ] Docker images build and deploy to staging automatically
- [ ] Pull request preview deployments work correctly
- [ ] Rollback procedures tested and documented

## Architectural Decisions

**Technology Stack:**

- Backend: Python FastAPI + PostgreSQL + pgvector + Redis
- Frontend: Next.js + TypeScript + shadcn/ui + Tailwind CSS
- Infrastructure: Docker-compose + nginx
- Package Management: npm workspaces

**Repository Structure:**

```
/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   ├── types/        # Shared TypeScript types
│   ├── ui/           # Shared UI components
│   └── utils/        # Shared utilities
└── docker-compose.yml
```

## Dependencies

- **External:** Docker, Node.js, Python 3.11+
- **Internal:** None (foundation epic)

## Risks & Mitigation

- **Risk:** Docker environment complexity
  - **Mitigation:** Comprehensive documentation and automated setup scripts
- **Risk:** Cross-platform compatibility issues
  - **Mitigation:** Test on multiple OS environments
- **Risk:** Dependency version conflicts
  - **Mitigation:** Pin specific versions in all configuration files

## Definition of Done

- [ ] All 5 stories completed with acceptance criteria met
- [ ] Development environment documented and validated
- [ ] Code quality gates pass (linting, typing, testing)
- [ ] Cross-team review completed
- [ ] Foundation ready for feature development
