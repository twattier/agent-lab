# Story 3.1: BMAD Template Import & External Service Setup - Developer Handoff

**Story:** 3.1 - BMAD Template Import & External Service Setup
**Epic:** Epic 3 - BMAD Workflow Integration
**Status:** 📋 Ready for Development
**Priority:** P1-Critical (Blocks Stories 3.2-3.5)
**Estimated Effort:** 8-12 hours

---

## Overview

Implement BMAD workflow template import from filesystem and integrate external LLM providers (OpenAI, Anthropic, OLLAMA) for workflow automation.

---

## Prerequisites

✅ Story 3.0 complete - All Epic 2 validations passed
✅ External dependencies documented ([epic-3-dependencies.md](../epics/epic-3-dependencies.md))
✅ MCP Protocol specification reviewed
✅ API keys obtained (OpenAI, Anthropic)

---

## Key Implementation Tasks

### 1. BMAD Template Import Service

**File:** `apps/api/services/bmad_template_service.py`
**Acceptance Criteria:** AC1-AC5

```python
class BMADTemplateService:
    """Service for importing BMAD workflow templates."""

    async def import_template_from_path(
        self,
        template_path: Path,
        validate: bool = True
    ) -> WorkflowTemplate:
        """Import template from filesystem path."""
        pass

    async def validate_template_structure(
        self,
        template: dict
    ) -> tuple[bool, list[str]]:
        """Validate template has required fields."""
        pass
```

### 2. LLM Provider Integration

**Files:**

- `apps/api/services/llm/openai_provider.py`
- `apps/api/services/llm/anthropic_provider.py`
- `apps/api/services/llm/ollama_provider.py`
- `apps/api/services/llm/base_provider.py`

**Acceptance Criteria:** AC6-AC10

```python
class BaseLLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        context: dict
    ) -> str:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
```

### 3. MCP Protocol Integration

**File:** `apps/api/services/mcp_service.py`
**Acceptance Criteria:** AC11-AC15

```python
class MCPService:
    """MCP protocol integration for Claude Code."""

    async def initialize_session(
        self,
        workspace_path: Path
    ) -> str:
        """Initialize MCP session."""
        pass

    async def send_workflow_event(
        self,
        event_type: str,
        payload: dict
    ) -> bool:
        """Send workflow event to Claude Code."""
        pass
```

---

## API Endpoints

### Import Template

```http
POST /api/v1/bmad/templates/import
Content-Type: application/json

{
  "template_path": "/path/to/template.yml",
  "validate": true
}
```

### Test LLM Provider

```http
POST /api/v1/bmad/llm/test
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4-turbo-preview"
}
```

---

## Testing Requirements

1. **Unit Tests** (≥80% coverage):
   - Template import validation
   - LLM provider initialization
   - MCP session management

2. **Integration Tests**:
   - End-to-end template import
   - LLM provider health checks
   - MCP protocol handshake

---

## Dependencies

- MCP Python SDK: `0.9.0`
- OpenAI: `1.6.0`
- Anthropic: `0.8.0`
- PyYAML: Latest (for template parsing)

---

## Related Documentation

- [Epic 3 Dependencies](../epics/epic-3-dependencies.md)
- [Story 3.0 Prerequisites](./story-3.0-epic-3-prerequisites-and-blockers.md)
- [Epic 3 Sprint Planning](../epics/epic-3-sprint-planning.md)

---

**Created:** 2025-10-01
**Last Updated:** 2025-10-01
**Owner:** Developer (James)
