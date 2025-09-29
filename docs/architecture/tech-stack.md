# Tech Stack

## Technology Stack Table

| Category             | Technology                          | Version   | Purpose                                | Rationale                                                                                             |
| -------------------- | ----------------------------------- | --------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Frontend Language    | TypeScript                          | 5.3+      | Type-safe frontend development         | Prevents runtime errors, improves developer experience, essential for complex project management UI   |
| Frontend Framework   | Next.js                             | 13.4.19+  | React-based full-stack framework       | App Router, server components, built-in optimization, excellent TypeScript support (Epic 1 canonical) |
| UI Component Library | shadcn/ui                           | Latest    | Accessible, customizable components    | Radix UI foundation, Tailwind integration, matches PRD specifications                                 |
| State Management     | React Query + Zustand               | 5.x + 4.x | Server/client state management         | React Query for API state, Zustand for client state, optimal for complex data flows                   |
| Backend Language     | Python                              | 3.11.5+   | High-performance async backend         | Excellent AI/ML ecosystem, FastAPI compatibility, strong typing with Pydantic (Epic 1 canonical)      |
| Backend Framework    | FastAPI                             | 0.115+    | High-performance async API framework   | Auto-documentation, Pydantic integration, excellent async support                                     |
| API Style            | REST with OpenAPI                   | 3.0       | RESTful API with full documentation    | Standard approach, auto-generated docs, client SDK generation                                         |
| Database             | PostgreSQL                          | 15.4+     | Relational database with vector search | ACID compliance, pgvector 0.5.0 extension compatibility, mature ecosystem (Epic 1 canonical)          |
| Vector Database      | pgvector                            | 0.8+      | Vector similarity search extension     | Integrated with PostgreSQL, semantic search capabilities                                              |
| Cache                | Redis                               | 7.x       | In-memory caching and sessions         | High-performance caching, session storage, pub/sub capabilities                                       |
| File Storage         | Local filesystem                    | -         | Document and file management           | Aligns with local-first approach, simple deployment                                                   |
| Authentication       | NextAuth.js                         | 5.x       | Full-stack authentication solution     | OAuth integration, session management, TypeScript support                                             |
| Frontend Testing     | Vitest + React Testing Library      | Latest    | Fast unit testing for components       | Vite-based testing, excellent React support, TypeScript integration                                   |
| Backend Testing      | pytest + pytest-asyncio             | Latest    | Comprehensive Python testing           | Async support, excellent FastAPI integration, extensive ecosystem                                     |
| E2E Testing          | Playwright                          | Latest    | End-to-end browser testing             | Cross-browser support, excellent TypeScript integration, reliable automation                          |
| Build Tool           | Vite                                | 5.x+      | Fast frontend build and development    | Lightning-fast HMR, excellent TypeScript support, modern ecosystem                                    |
| Bundler              | Built into Vite/Next.js             | -         | Module bundling and optimization       | Integrated solutions, optimized for respective frameworks                                             |
| IaC Tool             | docker-compose                      | Latest    | Container orchestration                | Local-first deployment, simple service management                                                     |
| CI/CD                | GitHub Actions                      | -         | Automated testing and deployment       | Integrated with repository, excellent Docker support                                                  |
| Monitoring           | Built-in logging + Optional Sentry  | -         | Error tracking and performance         | Start simple, scale to Sentry for production                                                          |
| Logging              | Pino (Node.js) + structlog (Python) | Latest    | Structured logging across stack        | JSON logging, performance-optimized, consistent format                                                |
| CSS Framework        | Tailwind CSS                        | 3.4+      | Utility-first CSS framework            | Rapid styling, excellent with shadcn/ui, consistent design system                                     |

---

[← Back to High Level Architecture](high-level-architecture.md) | [Architecture Index](index.md) | [Next: Data Models →](data-models.md)
