# Technical Assumptions

## ⚙️ Repository Structure: Monorepo

Single repository containing frontend, backend, shared utilities, and documentation. Aligns with rapid development timeline and small team size, enabling coordinated changes across full stack and simplified deployment pipeline.

## Service Architecture

**Modular Monolith within Monorepo:** Single application with clear service boundaries (auth, projects, workflows, file-sync, agents) but deployed as unified system. Provides development simplicity for MVP while maintaining clean architecture for future microservice extraction if needed.

## Testing Requirements

**Unit + Integration Testing:** Focus on API endpoints and critical workflow logic with integration tests for Claude Code/MCP interactions. Manual testing for UI workflows given limited timeline. Automated testing for file sync and gate validation processes to ensure reliability.

## Additional Technical Assumptions and Requests

### Frontend Stack
- **Framework:** Next.js with TypeScript + shadcn/ui components for modern, accessible UI development
- **Styling:** Tailwind CSS for rapid, consistent styling with shadcn design system
- **State Management:** React Query + Zustand for server/client state management

### Backend Stack
- **Runtime:** Python with FastAPI for high-performance async API development
- **Data Validation:** Pydantic for robust data modeling and validation throughout the system
- **Database:** pgvector (PostgreSQL extension) for relational data + vector similarity search capabilities
- **Graph Database:** Neo4j for complex project relationship modeling and workflow dependencies (optional/future)

### Architecture & Infrastructure
- **Containerization:** Docker applications with docker-compose orchestration
- **Database Services:** Open-source PostgreSQL + pgvector extension via Docker containers
- **Service Discovery:** Docker networking for inter-service communication
- **Development Environment:** Full stack runnable via docker-compose for consistent dev experience

### Local-First Design
- **Local-First Design:** Complete application stack runnable on developer desktop via docker-compose
- **Portable Deployment:** Single docker-compose configuration deployable on any Docker host without external dependencies
- **Open Source Foundation:** All infrastructure components use open-source solutions (PostgreSQL, Redis, nginx)
- **Self-Contained:** No external services required except optional LLM providers

### LLM Integration
- **Provider Agnostic:** OpenAI-compatible API interface supporting multiple providers
- **Local Options:** OLLAMA integration for fully self-hosted LLM capabilities
- **External Options:** OpenAI, Anthropic, or other OpenAI-compatible APIs
- **Fallback Strategy:** Graceful degradation when LLM services unavailable

### Integration & AI
- **Agent Framework:** Pydantic-based agent definitions for structured AI interactions
- **Claude Code Integration:** Python MCP client implementation for file sync and context sharing
- **AI Services:** Anthropic Claude API with Pydantic request/response models

---
[← Back to UI Design Goals](ui-design-goals.md) | [PRD Index](index.md) | [Next: Epic Structure →](epic-structure.md)