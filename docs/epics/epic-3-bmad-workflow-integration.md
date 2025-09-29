# Epic 3: BMAD Method Workflow Integration

## Epic Goal
Integrate BMAD Method workflow automation with Claude Code configuration files, implementing gate management, workflow progression tracking, and conversational agent interfaces for qualification assistance.

## Epic Description

**Project Context:**
The core value proposition of AgentLab is automating BMAD Method qualification workflows. This epic implements the specialized workflow engine that imports templates from Claude Code, tracks progression, and provides human gate validation with AI assistance.

**Epic Scope:**
This epic implements:
- BMAD workflow template import from Claude Code configuration
- Gate management interface for human reviewers
- Workflow progression and state management
- Conversational agent interface for qualification assistance
- Integration with Claude Code project directories
- Feedback and validation result writing to markdown folders

## Stories

1. **Story 3.1:** BMAD Template Import & External Service Setup
   - **Claude Code MCP Integration Prerequisites:**
     - Set up MCP protocol client library (Python MCP SDK)
     - Configure Claude Code connection authentication
     - Implement connection retry logic and timeout handling
     - Add MCP server discovery and validation
   - **External API Dependencies:**
     - OpenAI API key acquisition and secure storage
     - Anthropic Claude API setup and rate limit handling
     - OLLAMA local LLM installation and configuration (optional)
     - API client libraries with error handling and fallbacks
   - **Template Import with External Validation:**
     - Claude Code configuration file parsing with schema validation
     - Workflow template storage and versioning
     - External template validation against BMAD Method standards
     - Fallback procedures when external services unavailable

2. **Story 3.2:** Gate Management & User/Agent Responsibility Framework
   - **Human-Only Actions (User Responsibilities):**
     - Gate approval/rejection decisions (cannot be automated)
     - External service account creation (OpenAI, Anthropic, Claude Code)
     - API key provision and credential management
     - Business domain validation and client contact verification
   - **Agent-Only Actions (Developer Agent Responsibilities):**
     - Code generation and automated development tasks
     - Configuration file parsing and validation
     - Database operations and data management
     - API integration and error handling implementation
   - **Gate Review Interface:**
     - Human review interface with clear approval/rejection controls
     - Comment capture requiring human input for rejections
     - Workflow progression validation (human oversight required)
     - Agent assistance during review process (but final decision human)
   - Add reviewer assignment and notification
   - Build gate history and audit trail
   - Implement gate dependency and sequencing logic

3. **Story 3.3:** Workflow Progression Engine
   - Create workflow state machine implementation
   - Add automatic progression triggers
   - Implement conditional workflow branching
   - Create workflow completion detection
   - Build progression analytics and reporting

4. **Story 3.4:** Claude Code Directory Synchronization
   - Implement on-demand file synchronization
   - Create bidirectional sync with Claude Code projects
   - Add conflict detection and resolution
   - Build file change monitoring
   - Implement sync status reporting

5. **Story 3.5:** Conversational Agent Interface
   - Integrate LLM providers (OpenAI, Anthropic, OLLAMA)
   - Create project-level conversational context
   - Implement qualification workflow assistance
   - Add conversation history and context management
   - Build agent response quality monitoring

## Success Criteria

### BMAD Integration Requirements
- [ ] All BMAD workflow templates import correctly
- [ ] Gate progression follows defined sequencing
- [ ] Human reviewers can approve/reject with comments
- [ ] Workflow states sync with external systems
- [ ] Template updates propagate to active workflows

### Claude Code Integration Requirements
- [ ] File synchronization maintains data integrity
- [ ] Sync conflicts detected and resolved gracefully
- [ ] Real-time sync status visible to users
- [ ] Markdown feedback files written correctly
- [ ] Project directory structure preserved

### AI Agent Requirements
- [ ] Conversational interface responds appropriately
- [ ] Project context maintained across conversations
- [ ] Multiple LLM providers supported seamlessly
- [ ] Response times under 5 seconds for standard queries
- [ ] Agent assistance improves qualification efficiency

## Technical Architecture

### BMAD Workflow Engine
```
WorkflowTemplate
├── id: UUID
├── name: String
├── version: String
├── configuration: JSONB
├── gates: [Gate]
└── created_at: Timestamp

Gate
├── id: UUID
├── template_id: UUID (FK)
├── name: String
├── dependencies: [Gate]
├── criteria: JSONB
└── position: Integer

WorkflowInstance
├── id: UUID
├── project_id: UUID (FK)
├── template_id: UUID (FK)
├── current_state: JSONB
├── gate_statuses: JSONB
└── progression_history: JSONB
```

### LLM Integration
- Unified LLM abstraction layer
- Provider-specific configuration management
- Context window optimization
- Token usage tracking and limits
- Response caching for efficiency

## Dependencies
- **Internal:** Epic 2 (Core Data Management) - Project and workflow data models
- **External:** LLM provider APIs, Claude Code MCP protocol, File system access

## Risks & Mitigation
- **Risk:** LLM provider rate limits or service disruption
  - **Mitigation:** Multiple provider support with automatic failover
- **Risk:** File synchronization conflicts
  - **Mitigation:** Conflict detection with manual resolution workflow
- **Risk:** Workflow template compatibility issues
  - **Mitigation:** Comprehensive template validation and error reporting
- **Risk:** Agent response quality degradation
  - **Mitigation:** Response monitoring and quality metrics

## BMAD Method Compliance
- Supports all standard BMAD qualification gates
- Maintains audit trail for compliance requirements
- Enables gate dependency enforcement
- Provides workflow progression analytics
- Supports custom workflow template creation

## Definition of Done
- [ ] All 5 stories completed with acceptance criteria met
- [ ] BMAD workflows import and execute correctly
- [ ] Gate management interface fully functional
- [ ] Claude Code synchronization working reliably
- [ ] Conversational agent provides helpful assistance
- [ ] Security review completed for LLM integrations
- [ ] Performance benchmarks met for workflow operations