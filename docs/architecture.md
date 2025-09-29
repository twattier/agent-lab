# AgentLab Fullstack Architecture Document

**📁 This document has been sharded for better navigation. See the complete architecture in organized sections:**

## 📋 Navigate to Architecture Sections

### Core Architecture
- **[Complete Architecture Index](./architecture/index.md)** - Full table of contents and overview
- **[High Level Architecture](./architecture/high-level-architecture.md)** - Technical summary and architectural patterns
- **[Tech Stack](./architecture/tech-stack.md)** - Technology stack decisions and tool selection
- **[Data Models](./architecture/data-models.md)** - Database schema and data relationships
- **[API Specification](./architecture/api-specification.md)** - REST API endpoints and specifications

### System Components
- **[Components](./architecture/components.md)** - Frontend and backend service components
- **[External APIs](./architecture/external-apis.md)** - Claude Code MCP integration and LLM providers
- **[Core Workflows](./architecture/core-workflows.md)** - Business process implementations

### Implementation Details
- **[Database Schema](./architecture/database-schema.md)** - Complete PostgreSQL schema design
- **[Frontend Architecture](./architecture/frontend-architecture.md)** - Next.js component organization
- **[Backend Architecture](./architecture/backend-architecture.md)** - FastAPI service layer design

### Development & Operations
- **[Project Structure](./architecture/project-structure.md)** - Monorepo organization
- **[Development Workflow](./architecture/development-workflow.md)** - Local setup and commands
- **[Deployment Architecture](./architecture/deployment-architecture.md)** - Docker and CI/CD
- **[Testing Strategy](./architecture/testing-strategy.md)** - Testing pyramid and organization
- **[Coding Standards](./architecture/coding-standards.md)** - Naming conventions and patterns

### Operational Concerns
- **[Error Handling Strategy](./architecture/error-handling-strategy.md)** - Error flow and response formats
- **[Security and Performance](./architecture/security-and-performance.md)** - Security requirements and optimization
- **[Monitoring and Observability](./architecture/monitoring-and-observability.md)** - Monitoring stack and metrics

## 🎯 Quick Reference

**Architecture Type**: Containerized modular monolith
**Technology Stack**: Python FastAPI + Next.js + PostgreSQL + Docker
**Deployment**: Local-first with cloud deployment options
**Status**: ✅ Complete and ready for implementation

## 🏗️ Key Architectural Decisions

- **Local-First Design**: Complete application stack runnable via docker-compose
- **Monorepo Structure**: Single repository with clear frontend/backend separation
- **MCP Protocol Integration**: Native Claude Code connectivity for workflow automation
- **Bilingual Support**: French business requirements + English technical documentation
- **Accessibility First**: WCAG AA compliance built into design system

## 🔗 Related Documentation

- **[Product Requirements Document](./prd.md)** - Business requirements and goals
- **[Epic Documentation](./epics/index.md)** - Implementation phases and development plans
- **[Frontend Specification](./front-end-spec.md)** - UI/UX design and component specifications

---

**Note**: The complete architecture content is available in the organized sections above. This index provides quick navigation to all architecture components without content duplication.