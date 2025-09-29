# Project Brief: AgentLab

## Executive Summary

AgentLab is an internal AI-powered project management platform designed to streamline DSI's software development workflow through BMAD Method automation. The platform addresses critical efficiency bottlenecks in project qualification processes by providing agent-assisted workflows, centralized project context, and seamless Claude Code integration. Initially developed for internal DSI usage to validate workflow automation value, with potential future open-source release to leverage community contributions for accelerated improvement.

## Problem Statement

**Current State:** DSI faces significant productivity challenges managing multiple AI-powered development projects across client portfolios:

- **Fragmented Information:** Project documentation, requirements, and technical specifications scattered across tools and formats, leading to context switching overhead and information loss
- **Manual Overhead:** Repetitive qualification activities and documentation management consuming 20-30% of Product Owner time that could be redirected to higher-value activities
- **Lost Context:** Difficulty tracking project history, decisions, and current state across 10+ active projects and existing applications, resulting in rework and quality issues
- **Integration Gap:** Disconnect between business requirements (often in French) and technical implementation requirements (English for Claude Code), creating translation and synchronization overhead
- **Portfolio Invisibility:** No centralized view of client services, project status, or resource allocation across the DSI organization

**Impact Quantification:** Based on current DSI operations with 3 Product Owners managing 10-25 concurrent projects each, inefficiencies result in:

- Estimated 20-30% productivity loss due to context switching and information search
- Rework cycles due to incomplete qualification and gate validation processes
- Client delivery delays from project management overhead

**Why Existing Solutions Fall Short:** Traditional project management tools (Jira, Azure DevOps) lack:

- BMAD Method workflow specialization and automation
- Native AI development tool integration (Claude Code)
- Bilingual document management capabilities
- Agent-assisted qualification and validation processes

**Urgency:** With increasing adoption of AI development tools across the industry, DSI needs workflow optimization to maintain competitive advantage in client delivery speed and quality.

## Proposed Solution

**Core Concept:** AgentLab provides an integrated platform that automates BMAD Method qualification workflows, maintains centralized project context, and seamlessly integrates with Claude Code for AI-powered development processes.

**Key Differentiators:**

- **BMAD Method Native:** First platform designed specifically around BMAD Method workflow automation with intelligent gate validation
- **Claude Code Deep Integration:** Bidirectional file synchronization and context sharing with development environment via MCP protocol
- **Bilingual by Design:** Native French/English document management with AI-assisted translation and synchronization
- **Agent-Assisted Workflows:** AI agents guide users through qualification, requirements gathering, and validation processes

**Why This Solution Will Succeed:** Unlike generic project management tools that require extensive customization, AgentLab is purpose-built for modern AI development methodologies, providing immediate value through specialized workflows and intelligent automation.

**High-Level Vision:** Transform DSI into a highly efficient AI development organization where project qualification happens seamlessly, context is never lost, and teams can focus on creative problem-solving rather than administrative overhead.

## Target Users

### Primary User Segment: DSI Product Owners

**Profile:** Senior IT professionals with 5-15 years experience managing multiple AI-powered development projects across client portfolios

- Currently manage 10-25 concurrent projects
- Bilingual capabilities (French/English) for client and technical communication
- Responsible for project qualification, requirements gathering, and stakeholder coordination
- Decision-making authority for project progression through BMAD Method gates

**Current Behaviors:**

- Switch between multiple tools (Excel, email, Jira, Claude Code) for project management
- Manually track project status and context across client portfolios
- Coordinate between French-speaking business stakeholders and English-based technical requirements
- Spend 20-30% of time on administrative project management tasks

**Specific Pain Points:**

- Information fragmentation leading to lost context and repeated work
- Manual gate validation processes prone to inconsistency and oversight
- Language switching overhead between business and technical documentation
- Difficulty maintaining project history and decision rationale

**Goals:** Streamline project management workflows, reduce administrative overhead, improve project delivery consistency, maintain comprehensive project context throughout development lifecycle.

### Secondary User Segment: DSI Leadership

**Profile:** IT Directors, CTOs responsible for DSI strategic direction and productivity optimization

- Oversight responsibility for 3+ Product Owners and their project portfolios
- Budget authority for productivity improvement initiatives
- Accountability for client delivery performance and team efficiency

**Goals:** Portfolio visibility, productivity metrics, resource optimization, competitive advantage through operational excellence.

## Goals & Success Metrics

### Business Objectives

- **Productivity Improvement:** Achieve 30-50% reduction in Product Owner administrative overhead within 3 months of MVP deployment
- **Quality Enhancement:** Reduce project rework rate by 25% through improved gate validation and context management
- **Delivery Acceleration:** Decrease average project qualification time from concept to development-ready by 40%
- **Knowledge Retention:** Eliminate information loss during project transitions and team changes

### User Success Metrics

- **Time Savings:** Measure actual time spent on project management tasks before/after AgentLab implementation
- **Context Switching Reduction:** Track frequency of tool switching during project management workflows
- **User Satisfaction:** Survey Product Owner satisfaction with workflow efficiency and tool usability
- **Adoption Rate:** Monitor daily active usage and feature utilization across DSI team

### Key Performance Indicators (KPIs)

- **Efficiency KPI:** Average time from project idea to "Ready for Dev Cycle" status < 5 business days
- **Quality KPI:** Gate rejection rate < 10% (vs. current baseline to be measured)
- **Adoption KPI:** 100% of new projects managed through AgentLab within 1 month of deployment
- **Value KPI:** Measurable productivity improvement enabling DSI to handle 25% more concurrent projects with same resources

## MVP Scope

### Core Features (Must Have)

- **Client Reference Management:** Two-level hierarchy (Client → Service) with contact management (name + email) and standard business domain classification
- **Project Repository:** Complete project lifecycle with categorization (new/old + implementation type + user type + business domain), confirmation before deletion, application catalog for dashboard reference
- **BMAD Method Workflow Integration:** Import workflow templates from Claude Code configuration, visualize workflow progression, markdown document display with GitHub-style changes and mermaid graph support
- **Basic Gate Management:** Simple review and feedback interface at each BMAD Method stage, human validation with approval/rejection and comment capture
- **File System Integration:** On-demand sync with Claude Code project files, feedback writing via dedicated markdown folders for development environment integration
- **Essential Dashboard:** Portfolio overview (per client or cross-functional), project status visualization, date-based activity feed showing latest project updates
- **Project-Level Agent Interface:** Conversational interface for project-specific queries and assistance during qualification workflow

### Out of Scope for MVP

- Multi-user collaboration features
- Advanced reporting and analytics
- Automated workflow triggers and notifications
- Integration with external project management tools
- Mobile application interface
- Advanced security and compliance features
- Multi-language interface (focus on bilingual document content only)
- Real-time synchronization (on-demand sync sufficient)

### MVP Success Criteria

**MVP is successful when:**

1. RSS Reader test project successfully progresses through complete BMAD qualification workflow using AgentLab
2. At least one real DSI project demonstrates measurable time savings compared to manual qualification process
3. All 3 Product Owners can successfully use the system for basic project management tasks
4. Integration with Claude Code enables seamless context transfer for development handoff
5. User feedback indicates workflow improvement and willingness to continue using AgentLab for all projects

## Post-MVP Vision

### Phase 2 Features

- **Advanced Agent Capabilities:** Transversal search across all projects and applications, intelligent recommendations based on similar past projects
- **MCP Service Layer:** Full bidirectional integration with Claude Code, real-time context synchronization, support for OpenCode and other AI development tools
- **Enhanced Templates:** Multiple workflow templates for different project types, solution templates for common application patterns (RAG, web apps, etc.)
- **Advanced Dashboard:** Comprehensive analytics, resource allocation insights, predictive project timeline estimation
- **Collaboration Features:** Multi-user project access, role-based permissions, team workflow coordination

### Long-term Vision

- **Open Source Platform:** Release as open-source project to build community around BMAD Method automation and gain external contributions for faster improvement
- **Methodology Engine:** Expand beyond BMAD Method to support other development methodologies (SAFe, Scrum, etc.)
- **AI Development Ecosystem Hub:** Become central platform for managing AI-powered development workflows across multiple tools and methodologies
- **Client Portal Integration:** Direct client visibility into project status and progress for enhanced transparency

### Expansion Opportunities

- **Multi-language Support:** Expand beyond French/English to support other language pairs for international clients
- **Industry Specialization:** Develop specialized workflows for specific industries (healthcare, finance, manufacturing)
- **Enterprise Platform:** Scale to support multiple organizations with tenant isolation and advanced security features

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Web application accessible via modern browsers, responsive design for desktop and tablet usage
- **Browser/OS Support:** Chrome, Firefox, Safari, Edge (latest 2 versions), Windows, macOS, Linux compatibility
- **Performance Requirements:** Sub-second page load times, handle 50+ concurrent projects, 1000+ documents, support for 10 concurrent users

### Technology Preferences

- **Frontend:** React or Next.js for modern, responsive UI with Tailwind CSS and shadcn/ui for rapid development
- **Backend:** Node.js/TypeScript or Python (FastAPI/Django) for rapid development and strong AI/ML ecosystem support
- **Database:** PostgreSQL for relational data (clients, projects, users) with potential vector database addition for semantic search
- **AI Integration:** OpenAI/Anthropic API for agent capabilities, MCP protocol implementation for Claude Code integration

### Architecture Considerations

- **Repository Structure:** Monorepo with clear separation between frontend, backend, and shared types/utilities
- **Service Architecture:** Modular backend services (auth, projects, workflows, file sync, agents) with REST/GraphQL API
- **Integration Requirements:** MCP server implementation, S3/GitHub API integration, webhook support for external notifications
- **Security/Compliance:** GDPR compliance for European operations, data encryption at rest and in transit, secure API token management

## Constraints & Assumptions

### Constraints

- **Budget:** Internal development project with limited external vendor budget, prioritize open-source tools and existing infrastructure
- **Timeline:** 6-8 weeks for MVP development, 2-4 weeks for validation period, must demonstrate value by end of Q4 2025
- **Resources:** 2-3 developers available part-time, limited UX/design resources, Product Owner time for testing and feedback
- **Technical:** Must integrate with existing Claude Code workflows, support current BMAD Method processes, maintain French/English bilingual capabilities

### Key Assumptions

- DSI team will actively participate in testing and provide regular feedback during development
- Current BMAD Method workflow templates are well-documented and can be imported programmatically
- Claude Code integration via MCP protocol will be stable and performant for production usage
- RSS Reader test project will provide sufficient complexity to validate core workflow automation
- Internal users will adapt to new workflow tools with appropriate training and support
- Future open-source release will generate sufficient community interest for continued development

## Risks & Open Questions

### Key Risks

- **Adoption Risk:** Internal users may resist changing established workflows, potentially limiting usage and value demonstration
- **Integration Complexity:** Claude Code and MCP integration may be more complex than anticipated, leading to development delays or reduced functionality
- **Scope Creep:** Feature requests during development may expand beyond MVP scope, delaying validation timeline
- **Resource Availability:** Developer availability may decrease due to client project priorities, impacting delivery timeline
- **Technology Risk:** Dependency on Anthropic's Claude API and MCP protocol creates external risk factors beyond DSI control

### Open Questions

- What specific BMAD Method workflow templates are currently available in Claude Code configuration?
- How will we measure baseline productivity metrics before AgentLab implementation for comparison?
- What level of Claude API usage can be sustained within budget constraints?
- How will we handle version control and conflict resolution for shared project documents?
- What criteria will determine readiness for open-source release?

### Areas Needing Further Research

- **MCP Protocol Implementation:** Detailed technical requirements for bidirectional file sync and context sharing
- **BMAD Method Automation:** Specific gate validation criteria and automation opportunities within current workflow
- **User Experience Design:** Interface design patterns for agent-assisted workflows and conversational project management
- **Performance Requirements:** Realistic usage patterns and system load requirements for MVP scaling
- **Security Architecture:** Data protection requirements for client project information and compliance considerations

## Appendices

### A. Research Summary

**Market Research Insights:**

- AI development tools market growing at 25.2% CAGR, validating strategic direction toward AI-powered workflows
- MCP ecosystem reaching $10.3B market with major platform adoptions (OpenAI, Microsoft), confirming integration feasibility
- 90% of automation projects fail due to complexity and change resistance, supporting start-simple approach

**Competitive Analysis Insights:**

- No direct competitors offer BMAD Method + Claude Code + multilingual capabilities combination
- Traditional PM tools (Jira, Azure DevOps) have AI features but lack workflow specialization
- Open source approach differentiates from commercial competitors and enables community contributions

**Brainstorming Session Insights:**

- Internal-first strategy eliminates commercial market pressure and enables value-focused development
- RSS Reader test case provides concrete validation approach without client project risk
- Start simple philosophy aligns with proven MVP development best practices

### B. Stakeholder Input

**DSI Leadership Priorities:**

- Demonstrated productivity improvement through measurable metrics
- Seamless integration with existing development workflows and tools
- Clear path to value demonstration without disrupting current client project delivery

**Product Owner Requirements:**

- Simplified workflow management reducing administrative overhead
- Maintained project context and history throughout development lifecycle
- Support for bilingual documentation requirements for client communication

### C. References

- AgentLab Initial Specification: `docs/INITIAL.md`
- Market Research Analysis: `docs/market-research.md`
- Competitive Analysis: `docs/competitor-analysis.md`
- Brainstorming Session Results: `docs/brainstorming-session-results.md`
- BMAD Method Documentation: `.bmad-core/` configuration files
- Claude Code Documentation: https://docs.claude.com/en/docs/claude-code
- MCP Protocol Specification: https://docs.claude.com/en/docs/mcp

## Next Steps

### Immediate Actions

1. **Validate BMAD Method Templates** - Review existing `.bmad-core/` configuration to confirm workflow import feasibility and identify any gaps
2. **Establish Baseline Metrics** - Measure current Product Owner time allocation and project qualification duration for comparison benchmarks
3. **Technical Architecture Planning** - Design MCP integration approach and file synchronization strategy with Claude Code environment
4. **Development Environment Setup** - Configure development infrastructure, API access, and initial project structure
5. **RSS Reader Test Case Definition** - Create detailed RSS Reader project specification for workflow validation testing
6. **User Testing Framework** - Design measurement approach for productivity improvements and user satisfaction metrics

### PM Handoff

This Project Brief provides the full context for AgentLab. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.
