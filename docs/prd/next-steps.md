# Next Steps

## 🚀 Implementation Guidance

### UX Expert Prompt

Create comprehensive UX/UI designs for AgentLab based on this PRD. Focus on:

**Dashboard-First Design:** Multi-level project views (list/card/detail) with workflow status visualization and portfolio overview optimized for Product Owner efficiency.

**Key Design Priorities:** BMAD Method workflow progression indicators, GitHub-style document change tracking, bilingual content management, and Claude Code integration status displays.

**Target Users:** DSI Product Owners managing 10-25 concurrent projects requiring quick context switching and minimal cognitive overhead.

Review the [UI Design Goals](ui-design-goals.md) section and create wireframes, user flows, and design system specifications for the 5 epic delivery sequence.

### Architect Prompt

Design technical architecture for AgentLab using this PRD as foundation. Key focus areas:

**Local-First Architecture:** Docker-compose deployment with Python FastAPI backend, Next.js frontend, PostgreSQL+pgvector database, all running on developer desktop and deployable to any Docker host.

**Critical Integration:** MCP protocol client implementation for bidirectional Claude Code file synchronization, context sharing, and feedback writing systems.

**Technology Stack:** Implement using specified stack (FastAPI, Next.js, shadcn/ui, PostgreSQL+pgvector, Docker) with open-source foundation and LLM provider flexibility (OpenAI API, OLLAMA, OpenAI-compatible services).

Review [Technical Assumptions](technical-assumptions.md) section and [Epic breakdown](epic-structure.md) to create detailed architecture documentation, database schema, API specifications, and deployment strategy.

---
[← Back to Epic Structure](epic-structure.md) | [PRD Index](index.md)