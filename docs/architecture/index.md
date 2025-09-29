# AgentLab Fullstack Architecture Document

This document outlines the complete fullstack architecture for **AgentLab**, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

## Table of Contents

### Core Architecture
- [High Level Architecture](high-level-architecture.md) - Technical summary, platform choices, and architectural patterns
- [Tech Stack](tech-stack.md) - Technology stack decisions and tool selection
- [Data Models](data-models.md) - Database schema and data relationships
- [API Specification](api-specification.md) - REST API endpoints and specifications

### System Components
- [Components](components.md) - Frontend and backend service components
- [External APIs](external-apis.md) - Claude Code MCP integration and LLM provider APIs
- [Core Workflows](core-workflows.md) - Business process implementations

### Implementation Architecture
- [Database Schema](database-schema.md) - Complete database design and relationships
- [Frontend Architecture](frontend-architecture.md) - Component organization, state management, and routing
- [Backend Architecture](backend-architecture.md) - Service architecture, controllers, and data access

### Development & Operations
- [Project Structure](project-structure.md) - Unified monorepo organization
- [Development Workflow](development-workflow.md) - Local setup and development commands
- [Deployment Architecture](deployment-architecture.md) - Deployment strategy and CI/CD pipeline
- [Testing Strategy](testing-strategy.md) - Testing pyramid and test organization
- [Coding Standards](coding-standards.md) - Critical fullstack rules and naming conventions

### Operational Concerns
- [Error Handling Strategy](error-handling-strategy.md) - Error flow and response formats
- [Security and Performance](security-and-performance.md) - Security requirements and performance optimization
- [Monitoring and Observability](monitoring-and-observability.md) - Monitoring stack and key metrics

## Overview

AgentLab employs a **containerized modular monolith architecture** with Docker-compose orchestration, enabling local-first deployment while maintaining enterprise-grade capabilities. The system combines Python FastAPI backend services with Next.js App Router frontend, connected through RESTful APIs and real-time MCP protocol integration for Claude Code synchronization.

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-09-29 | 1.0 | Initial architecture creation from PRD analysis | Winston (Architect) |
| 2025-09-29 | 1.1 | Added epic-specific implementation details and MCP protocol specifications | Sarah (PO) |

---
*For detailed information on any section, please refer to the individual documents listed in the Table of Contents above.*