# Epic 3: BMAD Workflow Integration - External Dependencies

**Epic:** Epic 3 - BMAD Workflow Integration
**Created:** 2025-10-01
**Owner:** Developer (James) / Architect (Winston)
**Status:** 📋 Documented
**Purpose:** Canonical reference for all external dependencies required for Epic 3 implementation

---

## Overview

Epic 3 integrates external services and protocols for BMAD workflow automation. This document defines the **canonical versions** of all external dependencies to prevent version conflicts and ensure compatibility.

---

## Core Dependencies

### MCP (Model Context Protocol)

**Package:** `mcp`
**Version:** `0.9.0` (Python SDK)
**Protocol Version:** v1.0.0
**Installation:**

```bash
pip install mcp==0.9.0
```

**Purpose:** Claude Code integration protocol for workflow automation
**Stories:** 3.1, 3.5
**Documentation:** https://modelcontextprotocol.io/

---

### OpenAI Python Library

**Package:** `openai`
**Version:** `1.6.0`
**Installation:**

```bash
pip install openai==1.6.0
```

**Purpose:** LLM provider for workflow automation, document embeddings
**Stories:** 3.1, 3.5
**Models Used:**

- `gpt-4-turbo-preview` (workflow automation)
- `text-embedding-ada-002` (document embeddings, 1536 dimensions)

**Documentation:** https://platform.openai.com/docs

---

### Anthropic Python Library

**Package:** `anthropic`
**Version:** `0.8.0`
**Installation:**

```bash
pip install anthropic==0.8.0
```

**Purpose:** Alternative LLM provider for workflow automation
**Stories:** 3.1, 3.5
**Models Used:**

- `claude-3-opus-20240229` (workflow automation)
- `claude-3-sonnet-20240229` (fallback)

**Documentation:** https://docs.anthropic.com/

---

### OLLAMA (Optional)

**Version:** Latest stable (Docker image)
**Installation:**

```bash
docker pull ollama/ollama:latest
```

**Purpose:** Local LLM provider for offline workflow automation
**Stories:** 3.1, 3.5
**Models Supported:**

- `llama2` (13B parameter model)
- `codellama` (code-specific tasks)

**Documentation:** https://ollama.ai/

---

## Epic 2 Dependencies (Inherited)

These dependencies were established in Epic 2 and carry forward to Epic 3:

### Python Core

**Version:** `3.11.5`
**Rationale:** Stable release with performance improvements for async operations

### PostgreSQL

**Version:** `15.4+`
**Extensions:**

- `pgvector 0.5.0+` (semantic search)
- `uuid-ossp` (UUID generation)

### FastAPI

**Version:** `0.115.0+`
**Purpose:** API framework

### SQLAlchemy

**Version:** `2.0.0+`
**Purpose:** ORM with async support

### Alembic

**Version:** `1.11.0+`
**Purpose:** Database migration management

### asyncpg

**Version:** `0.29.0+`
**Purpose:** PostgreSQL async driver

---

## Frontend Dependencies (Epic 3 Stories 3.4, 3.5)

### Next.js

**Version:** `13.4.19+`
**Purpose:** React framework for conversational UI
**Installation:**

```bash
npm install next@13.4.19
```

### TypeScript

**Version:** `5.1.6+`
**Purpose:** Type safety for frontend
**Installation:**

```bash
npm install typescript@5.1.6
```

### React

**Version:** `18.2.0+` (bundled with Next.js)
**Purpose:** UI library

---

## Development & Testing Dependencies

### pytest

**Version:** `7.4.0+`
**Extensions:**

- `pytest-asyncio 0.21.0+`
- `pytest-cov 4.1.0+`

### Docker

**Required Services:**

- PostgreSQL with pgvector (port 5434)
- OLLAMA (optional, port 11434)

---

## Version Compatibility Matrix

| Component     | Epic 2 Version | Epic 3 Version | Breaking Changes? |
| ------------- | -------------- | -------------- | ----------------- |
| Python        | 3.11.5         | 3.11.5         | No                |
| PostgreSQL    | 15.4+          | 15.4+          | No                |
| pgvector      | 0.5.0+         | 0.5.0+         | No                |
| FastAPI       | 0.115.0+       | 0.115.0+       | No                |
| Next.js       | 13.4.19+       | 13.4.19+       | No                |
| **MCP**       | N/A            | **0.9.0**      | **New**           |
| **OpenAI**    | N/A            | **1.6.0**      | **New**           |
| **Anthropic** | N/A            | **0.8.0**      | **New**           |

---

## Installation Commands

### Epic 3 New Dependencies (Python)

```bash
pip install mcp==0.9.0 openai==1.6.0 anthropic==0.8.0
```

### Epic 3 New Dependencies (Node.js)

```bash
npm install @modelcontextprotocol/sdk@latest
```

---

## Environment Variables

Epic 3 requires the following new environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Configuration
ANTHROPIC_API_KEY=<your-anthropic-api-key>
ANTHROPIC_MODEL=claude-3-opus-20240229

# OLLAMA Configuration (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# MCP Configuration
MCP_ENABLED=true
MCP_TIMEOUT=30000

# Claude Code Integration
CLAUDE_CODE_PATH=/path/to/workspace
```

---

## Validation

To verify all dependencies are correctly installed:

```bash
# Python dependencies
pip list | grep -E "mcp|openai|anthropic"

# Verify versions
python3 -c "import mcp; print(f'MCP: {mcp.__version__}')"
python3 -c "import openai; print(f'OpenAI: {openai.__version__}')"
python3 -c "import anthropic; print(f'Anthropic: {anthropic.__version__}')"

# PostgreSQL + pgvector
docker exec agentlab-postgres psql -U agentlab -d agentlab -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

---

## Conflict Resolution

### Known Conflicts

1. **OpenAI 1.6.0 vs 1.7.0+**: Breaking API changes in 1.7.0. Stick to 1.6.0.
2. **Anthropic 0.8.0 vs 0.9.0+**: Message format changes in 0.9.0. Stick to 0.8.0.
3. **MCP 0.9.0 vs 1.0.0+**: Protocol changes expected. Verify compatibility before upgrading.

### Version Lock Strategy

- All Epic 3 dependencies are **version-locked** in `requirements.txt`
- Use `pip freeze` after successful installation
- Document any manual version updates in this file

---

## References

- [Epic 3 Sprint Planning](./epic-3-sprint-planning.md)
- [Story 3.0 Prerequisites](../stories/story-3.0-epic-3-prerequisites-and-blockers.md)
- [Story 3.1 Developer Handoff](../stories/story-3.1-bmad-template-import-external-service-setup.md)
- [Tech Stack Documentation](../architecture/tech-stack.md)

---

**Last Updated:** 2025-10-01
**Review Frequency:** Before each Epic 3 story kickoff
**Owner:** Architect (Winston)
