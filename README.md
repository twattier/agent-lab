# AgentLab 🤖

AgentLab is a comprehensive AI development platform built with the BMAD Method automation and Claude Code integration. It provides a robust, scalable foundation for building AI-powered applications with a focus on productivity, automation, and best practices.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** 24.0+ ([Get Docker](https://docs.docker.com/get-docker/))
- **Node.js** 18.17.0 ([Download](https://nodejs.org/))
- **Python** 3.11.5 ([Download](https://www.python.org/downloads/))
- **Git** (for version control)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd agentlab
   ```

2. **Setup environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Install dependencies**

   ```bash
   npm install
   ```

4. **Start development environment**

   ```bash
   # Start all services (web, api, database)
   docker-compose up -d

   # Start development servers
   npm run dev
   ```

5. **Access the application**
   - Web Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - API Health Check: http://localhost:8000/health

## 🏗️ Architecture Overview

AgentLab follows a **containerized modular monolith** architecture with clear separation of concerns:

### Repository Structure

```
agentlab/
├── apps/                    # Application services
│   ├── web/                # Next.js frontend application
│   └── api/                # FastAPI backend service
├── packages/               # Shared libraries
│   ├── types/             # Shared TypeScript types
│   ├── ui/                # Shared UI components (shadcn/ui)
│   └── utils/             # Shared utility functions
├── docs/                  # Documentation
├── infrastructure/        # Docker & deployment configs
└── scripts/              # Build & utility scripts
```

### Technology Stack

**Frontend**

- TypeScript 5.3+ with strict mode
- Next.js 15.x with App Router
- shadcn/ui component library
- React Query + Zustand for state management
- Tailwind CSS for styling

**Backend**

- Python 3.12 with FastAPI 0.115+
- PostgreSQL 17.x with pgvector extension
- Redis 7.x for caching and sessions
- Pydantic for data validation

**Development**

- npm workspaces monorepo
- ESLint + Prettier + TypeScript
- Vitest + React Testing Library (frontend)
- pytest + pytest-asyncio (backend)
- Playwright for E2E testing
- Husky pre-commit hooks

## 🛠️ Development Workflow

### Running Services

```bash
# Start all services in development mode
npm run dev

# Start individual services
npm run dev --workspace=@agentlab/web    # Frontend only
npm run dev --workspace=@agentlab/api    # Backend only (use Python env)
```

### Code Quality

```bash
# Linting and formatting
npm run lint              # Check all workspaces
npm run lint:fix          # Fix auto-fixable issues
npm run format            # Format code with Prettier
npm run format:check      # Check formatting

# Type checking
npm run type-check        # Check TypeScript types

# Testing
npm run test              # Run all tests
npm run test:e2e          # Run E2E tests with Playwright
npm run test:e2e:ui       # Run E2E tests with UI
npm test:coverage         # Run tests with coverage reports

# Environment validation
./scripts/validate-setup.sh  # Verify development environment
```

### Testing Workflow

See [Testing Guide](./docs/testing-guide.md) for comprehensive testing documentation.

**Quick Commands:**

```bash
# Backend tests
cd apps/api
pytest                    # Run all backend tests
pytest tests/unit/        # Run unit tests only
pytest --cov=.           # With coverage

# Frontend tests
cd apps/web
npx vitest run           # Run all frontend tests
npx vitest run --coverage # With coverage

# E2E tests
npm run test:e2e         # Run Playwright tests
npm run test:e2e:ui      # Interactive mode
npm run test:e2e:debug   # Debug mode
```

**Coverage Requirements:**

- Critical Business Logic: 95%+
- API Endpoints: 90%+
- UI Components: 80%+
- Utility Functions: 100%

**Test Environment:**

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Verify setup
./scripts/validate-setup.sh

# Clean test artifacts
./scripts/test-cleanup.sh
```

### Git Workflow

1. **Create feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes with conventional commits**

   ```bash
   git commit -m "feat: add user authentication system"
   git commit -m "fix: resolve API validation error"
   git commit -m "docs: update installation instructions"
   ```

3. **Pre-commit hooks automatically run:**
   - ESLint checks and fixes
   - Prettier formatting
   - Type checking

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR via GitHub interface
   ```

## 🔧 External Services Setup

### Claude API (Required)

1. **Create Account**
   - Visit [console.anthropic.com](https://console.anthropic.com)
   - Sign up or log in to your account

2. **Generate API Key**
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key immediately (won't be shown again)

3. **Configure Environment**

   ```bash
   # Add to .env file
   CLAUDE_API_KEY=your_claude_api_key_here
   ```

4. **Security Guidelines**
   - Never commit API keys to version control
   - Rotate keys quarterly or if compromised
   - Monitor usage and rate limits
   - Use different keys for dev/staging/production

### OpenAI API (Optional)

For fallback or testing purposes:

1. Visit [platform.openai.com](https://platform.openai.com)
2. Create API key
3. Add to `.env`: `OPENAI_API_KEY=your_openai_key_here`

### OLLAMA (Optional)

For local/offline development:

1. **Install OLLAMA**

   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Configure Environment**
   ```bash
   # Add to .env file
   OLLAMA_HOST=http://localhost:11434
   ```

## 🔐 Security & Credentials

### Environment Variables

- **Development**: Use `.env` file (never commit)
- **Production**: Use secure environment variable injection
- **CI/CD**: Use repository secrets

### API Key Management

- Generate separate keys for each environment
- Implement key rotation policy (quarterly)
- Monitor API usage and set alerts
- Use least-privilege access principles

### Best Practices

- Regular security audits
- Dependency vulnerability scanning
- Code security reviews
- Secure coding standards compliance

## 📚 Documentation

- [Architecture Documentation](./docs/architecture/)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Component Library](./packages/ui/src/)
- [Development Guides](./docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow conventional commit format
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Create an issue for bug reports
- Use discussions for questions
- Check documentation for common solutions
- Review existing issues before creating new ones

---

Built with ❤️ using the BMAD Method and Claude Code integration.
