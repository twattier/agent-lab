# Commit Message Standards

This document outlines the commit message standards for AgentLab, based on the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

### Primary Types

- **feat**: A new feature for the user
- **fix**: A bug fix for the user
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

### Extended Types

- **perf**: A code change that improves performance
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies
- **revert**: Reverts a previous commit

## Scopes

Scopes help identify which part of the codebase is affected:

### Frontend Scopes
- **web**: Next.js web application
- **ui**: Shared UI components
- **auth**: Authentication system
- **routing**: Navigation and routing
- **forms**: Form components and validation
- **api**: Frontend API integration

### Backend Scopes
- **api**: FastAPI backend
- **db**: Database models and migrations
- **auth**: Authentication and authorization
- **services**: Business logic services
- **middleware**: Request/response middleware
- **config**: Configuration management

### Infrastructure Scopes
- **docker**: Docker configuration
- **ci**: Continuous integration
- **deploy**: Deployment configuration
- **monitoring**: Logging and monitoring

### General Scopes
- **types**: TypeScript type definitions
- **utils**: Utility functions
- **deps**: Dependencies management
- **security**: Security-related changes

## Examples

### Good Examples

```bash
# Feature additions
feat(auth): add user registration endpoint
feat(ui): implement dark mode toggle component
feat(api): add project creation workflow

# Bug fixes
fix(auth): resolve token expiration handling
fix(ui): correct button alignment in mobile view
fix(db): fix migration script for user table

# Documentation
docs(readme): update installation instructions
docs(api): add authentication endpoints documentation
docs(contributing): add code review guidelines

# Refactoring
refactor(services): extract user validation logic
refactor(components): simplify form component architecture
refactor(utils): optimize data transformation functions

# Performance improvements
perf(api): optimize database queries for user lookup
perf(web): implement lazy loading for dashboard components
perf(db): add indexes for frequently queried columns

# Tests
test(auth): add unit tests for login validation
test(ui): add component tests for form inputs
test(api): add integration tests for project endpoints

# Chores
chore(deps): update TypeScript to version 5.2
chore(ci): update GitHub Actions workflow
chore(build): optimize webpack configuration
```

### Breaking Changes

For breaking changes, add `!` after the type/scope and include `BREAKING CHANGE:` in the footer:

```bash
feat(api)!: change user endpoint response format

BREAKING CHANGE: User endpoint now returns user object directly instead of wrapping it in a data property
```

### Multi-paragraph Body

```bash
fix(auth): resolve session timeout issues

The previous implementation did not properly handle session refresh
when the access token expired. This fix implements automatic token
refresh with proper error handling.

- Add token refresh mechanism
- Implement retry logic for expired tokens
- Add better error messages for auth failures

Fixes #123
```

## Rules and Guidelines

### Rules (Must Follow)

1. **Type is required**: Every commit must have a valid type
2. **Description is required**: Must be present and meaningful
3. **Lowercase**: Type and scope must be lowercase
4. **Present tense**: Use imperative mood ("add" not "added" or "adds")
5. **No period**: Don't end the description with a period
6. **50 character limit**: Keep the first line under 50 characters

### Guidelines (Should Follow)

1. **Meaningful descriptions**: Describe what and why, not how
2. **Reference issues**: Include issue numbers when applicable
3. **Atomic commits**: One logical change per commit
4. **Consistent scopes**: Use established scopes
5. **Breaking changes**: Always document breaking changes

## Bad Examples

❌ **Avoid these patterns:**

```bash
# Too vague
fix: bug fix
feat: new stuff
chore: updates

# Wrong tense
feat: added user authentication
fix: fixed the bug

# Too long
feat(auth): implement comprehensive user authentication system with JWT tokens and refresh mechanism

# Missing type
add user authentication endpoint

# Wrong capitalization
Feat(auth): add login endpoint
FEAT(AUTH): ADD LOGIN ENDPOINT

# Period at end
feat(auth): add login endpoint.
```

## Integration with Tools

### Pre-commit Hooks

Husky automatically validates commit messages using commitlint:

```bash
# Will pass validation
git commit -m "feat(auth): add user login"

# Will fail validation
git commit -m "add user login"
```

### VS Code Integration

Install the "Conventional Commits" extension for VS Code to get:
- Autocomplete for types and scopes
- Message templates
- Validation hints

### Git Aliases

Add these aliases to your `~/.gitconfig`:

```ini
[alias]
    cf = "!f() { git commit -m \"feat($1): $2\"; }; f"
    cx = "!f() { git commit -m \"fix($1): $2\"; }; f"
    cd = "!f() { git commit -m \"docs($1): $2\"; }; f"
    cr = "!f() { git commit -m \"refactor($1): $2\"; }; f"
```

Usage:
```bash
git cf auth "add user registration"
# Equivalent to: git commit -m "feat(auth): add user registration"
```

## Release Management

Conventional commits enable automatic:
- Version bumping (semantic versioning)
- Changelog generation
- Release note creation

### Version Impact

- `feat`: Minor version bump (1.1.0 → 1.2.0)
- `fix`: Patch version bump (1.1.0 → 1.1.1)
- `BREAKING CHANGE`: Major version bump (1.1.0 → 2.0.0)

## Enforcement

### Automated Validation

Commitlint runs on every commit and checks:
- Type is valid
- Format is correct
- Line length limits
- Case sensitivity

### Manual Review

During code review, check that:
- Commits are atomic and focused
- Messages are clear and descriptive
- Breaking changes are properly documented
- Related issues are referenced

## Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)

---

For questions about commit standards, refer to this document or ask in the team chat.