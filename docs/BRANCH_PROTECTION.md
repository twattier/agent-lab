# Branch Protection Guidelines

This document outlines recommended branch protection rules for AgentLab to ensure code quality and prevent direct pushes to protected branches.

## Branch Strategy

### Protected Branches

- **main** - Production-ready code
- **develop** - Integration branch (optional, if using GitFlow)

### Branch Naming Conventions

```
feature/description-of-feature
bugfix/description-of-bug
hotfix/critical-issue-description
release/version-number
```

## Recommended Protection Rules

### Main Branch Protection

#### Required Settings

1. **Require a pull request before merging**
   - ✅ Required number of reviewers: 1
   - ✅ Dismiss stale reviews when new commits are pushed
   - ✅ Require review from code owners (if CODEOWNERS file exists)

2. **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - ✅ Required status checks:
     - `ci/lint` - ESLint and Prettier checks
     - `ci/type-check` - TypeScript compilation
     - `ci/test-frontend` - Frontend unit tests
     - `ci/test-backend` - Backend unit tests
     - `ci/build` - Build verification

3. **Require signed commits**
   - ✅ Require signed commits for additional security

4. **Include administrators**
   - ✅ Include administrators in these restrictions

5. **Allow specified actors to bypass required pull requests**
   - ❌ Do not allow bypassing (recommended for strict workflow)

#### Optional Settings

- **Require linear history**: Prevents merge commits, requires rebase or squash
- **Require deployments to succeed**: If using deployment checks
- **Lock branch**: Prevents all pushes (for maintenance)

### Develop Branch Protection (if using GitFlow)

Similar to main branch but with relaxed requirements:
- Required reviewers: 1
- Allow administrators to bypass
- Required status checks (same as main)

## GitHub Configuration

### Setting Up Protection Rules

1. **Navigate to Repository Settings**
   ```
   Repository → Settings → Branches
   ```

2. **Add Branch Protection Rule**
   - Branch name pattern: `main`
   - Configure protection settings as outlined above

3. **Required Status Checks Setup**
   - Ensure CI/CD pipeline creates the required checks
   - Configure branch protection to require these checks

### Example GitHub Actions Required Checks

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.17.0'
      - name: Install dependencies
        run: npm ci
      - name: Lint
        run: npm run lint
      - name: Format check
        run: npm run format:check

  type-check:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.17.0'
      - name: Install dependencies
        run: npm ci
      - name: Type check
        run: npm run type-check

  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.17.0'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test --workspace=@agentlab/web

  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11.5'
      - name: Install dependencies
        run: |
          cd apps/api
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd apps/api
          pytest

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.17.0'
      - name: Install dependencies
        run: npm ci
      - name: Build
        run: npm run build
```

## Code Owners

### CODEOWNERS File

Create `.github/CODEOWNERS` to require specific reviewers:

```
# Global owners
* @team-leads @senior-developers

# Frontend specific
/apps/web/ @frontend-team
/packages/ui/ @frontend-team @design-team

# Backend specific
/apps/api/ @backend-team
/infrastructure/ @devops-team

# Documentation
/docs/ @tech-writers @team-leads

# Configuration files
/.github/ @devops-team @team-leads
/package.json @team-leads
/docker-compose*.yml @devops-team
```

## Workflow Enforcement

### Pull Request Requirements

Before merging, ensure:

1. **Code Review Completed**
   - At least one approval from required reviewers
   - No outstanding change requests
   - All conversations resolved

2. **Automated Checks Passed**
   - Linting and formatting checks
   - Type checking without errors
   - All tests passing
   - Successful build

3. **Documentation Updated**
   - README updated if needed
   - API documentation current
   - CHANGELOG updated for significant changes

4. **Security Considerations**
   - No secrets committed
   - Dependencies scanned for vulnerabilities
   - Security implications reviewed

### Emergency Procedures

For critical hotfixes:

1. **Create hotfix branch** from main
2. **Make minimal fix** addressing only the critical issue
3. **Fast-track review** with senior developer approval
4. **Merge with expedited process**
5. **Create follow-up tasks** for proper testing/documentation

### Branch Protection Bypass

Only allow bypass for:
- Repository administrators
- Emergency hotfixes (with proper justification)
- Automated dependency updates (with proper checks)

## Local Development Guidelines

### Pre-push Checklist

Before pushing to any branch:

```bash
# 1. Ensure branch is up to date
git pull origin main
git rebase main  # or merge main into feature branch

# 2. Run local quality checks
npm run lint
npm run type-check
npm run test
npm run build

# 3. Create meaningful commit messages
git commit -m "feat(scope): descriptive message"

# 4. Push to feature branch
git push origin feature/branch-name
```

### Git Hooks

Local pre-push hook to prevent direct pushes to protected branches:

```bash
#!/bin/sh
# .git/hooks/pre-push

protected_branch='main'
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

if [ $protected_branch = $current_branch ]; then
    echo "Direct pushes to the $protected_branch branch are not allowed."
    echo "Please create a feature branch and open a pull request."
    exit 1
fi
```

## Monitoring and Metrics

### Branch Protection Metrics

Track:
- Number of direct push attempts blocked
- Pull request review completion time
- Failed status check frequency
- Emergency bypass usage

### Code Quality Trends

Monitor:
- Test coverage percentage
- Linting violations over time
- Build failure rates
- Security vulnerability detection

## Troubleshooting

### Common Issues

1. **Status Check Not Required**
   - Verify CI workflow creates the expected check name
   - Ensure check runs on pull request events
   - Check branch protection rule configuration

2. **Unable to Merge Despite Approvals**
   - Check if branch is up to date with base branch
   - Verify all required status checks are passing
   - Ensure no outstanding change requests

3. **Emergency Access Needed**
   - Contact repository administrator
   - Document reason for bypass
   - Create follow-up issue for proper process

### Best Practices

1. **Regular Review** of protection rules
2. **Team Training** on Git workflow
3. **Documentation** of exceptions and reasoning
4. **Automation** of repetitive checks
5. **Monitoring** of compliance and effectiveness

---

For questions about branch protection, contact the DevOps team or create an issue in the repository.