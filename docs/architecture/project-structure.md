# Unified Project Structure

AgentLab uses a monorepo structure with npm workspaces for coordinated frontend/backend development and shared utilities.

## Repository Organization

```
agentlab/
├── README.md                 # Project overview and setup
├── package.json              # Root package.json with workspaces
├── docker-compose.yml        # Local development environment
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
│
├── apps/                    # Application packages
│   ├── web/                 # Next.js frontend application
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── tailwind.config.js
│   │   ├── src/
│   │   │   ├── app/         # Next.js App Router
│   │   │   ├── components/  # React components
│   │   │   ├── lib/         # Utilities and configurations
│   │   │   ├── hooks/       # Custom React hooks
│   │   │   ├── store/       # Zustand state management
│   │   │   └── types/       # TypeScript definitions
│   │   └── public/          # Static assets
│   │
│   └── api/                 # FastAPI backend application
│       ├── pyproject.toml   # Python dependencies
│       ├── Dockerfile       # API container configuration
│       ├── main.py          # FastAPI application entry
│       ├── api/             # API endpoints
│       ├── services/        # Business logic
│       ├── repositories/    # Data access layer
│       ├── models/          # Pydantic models
│       ├── core/            # Core utilities
│       ├── migrations/      # Database migrations
│       └── tests/           # API tests
│
├── packages/                # Shared packages
│   ├── types/               # Shared TypeScript types
│   │   ├── package.json
│   │   └── src/
│   │       ├── client.ts    # Client data types
│   │       ├── project.ts   # Project data types
│   │       └── api.ts       # API response types
│   │
│   ├── ui/                  # Shared UI components
│   │   ├── package.json
│   │   └── src/
│   │       ├── components/  # Reusable components
│   │       └── styles/      # Shared styles
│   │
│   └── utils/               # Shared utilities
│       ├── package.json
│       └── src/
│           ├── validation.ts # Data validation
│           ├── formatting.ts # Data formatting
│           └── constants.ts  # Shared constants
│
├── docs/                    # Documentation (sharded)
│   ├── prd/                 # Product Requirements (sharded)
│   ├── architecture/        # Technical Architecture (sharded)
│   ├── epics/               # Epic specifications
│   └── stories/             # User story details
│
├── infrastructure/          # Infrastructure configuration
│   ├── docker/              # Docker configurations
│   ├── postgres/            # Database setup
│   └── nginx/               # Reverse proxy config
│
└── scripts/                 # Development and deployment scripts
    ├── setup.sh             # Initial project setup
    ├── dev.sh               # Development environment
    ├── test.sh              # Run all tests
    └── deploy.sh            # Deployment script
```

## Workspace Configuration

### Root package.json
```json
{
  "name": "agentlab",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "concurrently \"npm run dev:api\" \"npm run dev:web\"",
    "dev:web": "npm run dev --workspace=apps/web",
    "dev:api": "npm run dev --workspace=apps/api",
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces",
    "lint": "npm run lint --workspaces",
    "type-check": "npm run type-check --workspaces"
  },
  "devDependencies": {
    "concurrently": "^8.2.0",
    "typescript": "^5.3.0"
  }
}
```

### Inter-Package Dependencies
- **apps/web** depends on **packages/types**, **packages/ui**, **packages/utils**
- **apps/api** depends on **packages/types** (for shared data models)
- **packages/ui** depends on **packages/types** (for component props)

## Development Benefits

1. **Coordinated Changes:** Modify shared types and see updates across frontend/backend
2. **Consistent Tooling:** Shared linting, formatting, and testing configurations
3. **Simplified Deployment:** Single repository with coordinated versioning
4. **Code Reuse:** Shared utilities and components across applications
5. **Type Safety:** End-to-end type safety from API to frontend

---
[← Back to Backend Architecture](backend-architecture.md) | [Architecture Index](index.md) | [Next: Development Workflow →](development-workflow.md)