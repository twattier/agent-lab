# AgentLab Documentation Index

Welcome to the AgentLab project documentation. This index provides a comprehensive overview of all documentation files and their contents to help you navigate the project effectively.

## 📋 Quick Navigation

- [Core Project Documents](#core-project-documents)
- [Epic Documentation](#epic-documentation)
- [Quality Assurance](#quality-assurance)
- [Research & Analysis](#research--analysis)
- [How to Navigate](#how-to-navigate)

## 📁 Document Sharding Notice

**Large documents have been sharded for better navigation and maintenance:**
- **PRD**: Organized into `docs/prd/` with focused sections
- **Architecture**: Organized into `docs/architecture/` with implementation-focused files
- **Benefits**: Easier to find specific information, better team collaboration, reduced duplication

---

## 🎯 Core Project Documents

### [📄 Product Requirements Document (PRD)](./prd.md)
**Purpose**: Complete product specification and requirements (📁 **Sharded**)
**Content**: Goals, functional/non-functional requirements, technical stack, epic structure
**Key Sections**: [Requirements](./prd/requirements.md), [UI/UX goals](./prd/ui-design-goals.md), [Technical assumptions](./prd/technical-assumptions.md), [Epic dependencies](./prd/epic-structure.md)
**Status**: ✅ Validated by PO Master Checklist
**Navigate**: [Complete PRD Index](./prd/index.md) for organized sections

### [🏗️ Architecture Document](./architecture.md)
**Purpose**: Complete fullstack technical architecture (📁 **Sharded**)
**Content**: System design, technology choices, infrastructure, deployment strategy
**Key Sections**: [High-level architecture](./architecture/high-level-architecture.md), [Tech stack](./architecture/tech-stack.md), [API specification](./architecture/api-specification.md)
**Status**: ✅ Comprehensive, aligned with PRD requirements
**Navigate**: [Complete Architecture Index](./architecture/index.md) for organized sections

### [🎨 Frontend Specification](./front-end-spec.md)
**Purpose**: Complete UI/UX design specification
**Content**: User flows, wireframes, component library, accessibility requirements
**Key Sections**: Design system, responsive strategy, accessibility (WCAG AA)
**Status**: ✅ Ready for development implementation

---

## 📚 Epic Documentation

Epic documentation follows the dependency sequence: **Epic 1 → Epic 2 → (Epic 3, Epic 4) → Epic 5**

### [⚡ Epic 1: Foundation & Infrastructure Setup](./epics/epic-1-foundation-infrastructure.md)
**Goal**: Establish foundational development environment and infrastructure
**Stories**: 5 stories (Project scaffolding, Docker setup, Backend foundation, Frontend foundation, Environment validation)
**Key Features**:
- Complete project scaffolding with explicit commands
- Docker-compose with IaC (Terraform modules)
- Comprehensive testing framework with mock services
- Version pinning and dependency conflict resolution
**Status**: ✅ PO Validated - Ready for development

### [📊 Epic 2: Core Data Management & Client Hierarchy](./epics/epic-2-core-data-management.md)
**Goal**: Implement fundamental data management system
**Stories**: 5 stories (Client hierarchy, Project models, BMAD workflow state, Document metadata, Data validation)
**Key Features**:
- Client → Service → Project hierarchy
- Comprehensive seed data strategy
- BMAD workflow state management
- Data validation and integrity constraints
**Status**: ✅ PO Validated - Dependent on Epic 1

### [🔄 Epic 3: BMAD Method Workflow Integration](./epics/epic-3-bmad-workflow-integration.md)
**Goal**: Integrate BMAD Method workflow automation with Claude Code
**Stories**: 5 stories (Template import, Gate management, Workflow progression, Claude Code sync, Agent interface)
**Key Features**:
- MCP protocol integration with fallback procedures
- External API setup (OpenAI, Anthropic, OLLAMA)
- Clear user/agent responsibility framework
- Gate review interface with human oversight
**Status**: ✅ PO Validated - Parallel with Epic 4

### [📱 Epic 4: Portfolio Dashboard & Core UI](./epics/epic-4-portfolio-dashboard-ui.md)
**Goal**: Implement user-facing dashboard interface
**Stories**: 5 stories (Authentication, Portfolio dashboard, Activity feed, Client/project management, Navigation)
**Key Features**:
- Dashboard-first navigation for 10-25 concurrent projects
- Real-time activity feed and status visualization
- Responsive design with accessibility compliance
**Status**: ✅ PO Validated - Parallel with Epic 3

### [📝 Epic 5: Document Management & Bilingual Support](./epics/epic-5-document-management-bilingual.md)
**Goal**: Implement comprehensive document management with bilingual support
**Stories**: 5 stories (Markdown display, Mermaid integration, Version control, Bilingual management, Document sync)
**Key Features**:
- GitHub-style markdown rendering and change tracking
- Mermaid diagram support for architecture documentation
- French/English bilingual document management
- MVP scope validation and post-MVP feature separation
**Status**: ✅ PO Validated - Dependent on all previous epics

---

## 🔍 Quality Assurance

### [📋 QA Assessment Framework](./qa/qa-assessment-framework.md)
**Purpose**: Comprehensive quality assessment methodology
**Content**: Testing standards, validation procedures, quality gates
**Key Sections**: Testing strategy, quality metrics, validation workflows

### [✅ Testing Standards](./qa/testing-standards.md)
**Purpose**: Testing requirements and standards
**Content**: Unit testing, integration testing, end-to-end testing requirements
**Key Sections**: Coverage targets, testing frameworks, CI/CD integration

### [🚪 Quality Gates](./qa/gates/)
**Purpose**: Quality gate templates and validation procedures
**Content**: Story quality gate template for validation workflows
**Files**:
- `story-quality-gate-template.yml` - Template for story validation

---

## 📈 Research & Analysis

### [🎯 Project Brief](./brief.md)
**Purpose**: Initial project concept and objectives
**Content**: Executive summary, problem statement, solution approach
**Key Sections**: Business case, target users, success metrics
**Status**: Foundation document for PRD development

### [📊 Market Research Report](./market-research.md)
**Purpose**: Market analysis and competitive landscape
**Content**: Research methodology, market analysis, competitive positioning
**Key Sections**: Market size, competitor analysis, differentiation strategy

### [🏆 Competitor Analysis](./competitor-analysis.md)
**Purpose**: Detailed competitive analysis
**Content**: Feature comparison, strengths/weaknesses, market positioning
**Key Sections**: Direct competitors, indirect competitors, competitive advantages

### [💡 Brainstorming Session Results](./brainstorming-session-results.md)
**Purpose**: Ideation and concept development session outcomes
**Content**: Feature ideas, user stories, technical approaches
**Key Sections**: Feature prioritization, technical considerations, next steps

### [📝 Initial Use Case Specification](./INITIAL.md)
**Purpose**: Original use case and requirements specification
**Content**: Executive summary, use cases, system requirements
**Key Sections**: Business objectives, functional requirements, technical constraints

---

## 🧭 How to Navigate

### For Project Managers
1. Start with [Project Brief](./brief.md) for context
2. Review [PRD](./prd.md) for complete requirements
3. Follow epic sequence: [Epic 1](./epics/epic-1-foundation-infrastructure.md) → [Epic 2](./epics/epic-2-core-data-management.md) → ([Epic 3](./epics/epic-3-bmad-workflow-integration.md), [Epic 4](./epics/epic-4-portfolio-dashboard-ui.md)) → [Epic 5](./epics/epic-5-document-management-bilingual.md)

### For Developers
1. Read [Architecture Document](./architecture.md) for technical overview
2. Review [Epic 1](./epics/epic-1-foundation-infrastructure.md) for setup procedures
3. Check [QA Framework](./qa/qa-assessment-framework.md) for quality standards
4. Follow [Frontend Specification](./front-end-spec.md) for UI implementation

### For UX Designers
1. Start with [Frontend Specification](./front-end-spec.md)
2. Review [PRD UI/UX Goals](./prd.md#user-interface-design-goals)
3. Check [Epic 4](./epics/epic-4-portfolio-dashboard-ui.md) for dashboard requirements
4. Review [Epic 5](./epics/epic-5-document-management-bilingual.md) for document UI needs

### For QA Teams
1. Review [QA Assessment Framework](./qa/qa-assessment-framework.md)
2. Check [Testing Standards](./qa/testing-standards.md)
3. Use [Quality Gates](./qa/gates/) for validation procedures
4. Follow epic-specific testing requirements in each epic document

---

## 📊 Document Status Legend

- ✅ **Complete & Validated**: Ready for implementation
- 🔄 **In Progress**: Under active development
- 📝 **Draft**: Initial version, needs review
- 🔍 **Under Review**: Pending stakeholder validation

---

## 🔄 Last Updated

**Date**: September 29, 2025
**Version**: 1.0
**Validated By**: Sarah (Product Owner) via PO Master Checklist
**Status**: ✅ **APPROVED** - Ready for development

---

## 📞 Support

For questions about documentation or navigation:
- Contact the Product Owner for requirements clarification
- Contact the Architect for technical architecture questions
- Contact the UX Expert for design specification questions
- Use the QA framework for quality-related guidance

**Project Status**: 🚀 **Ready for Epic 1 Implementation**