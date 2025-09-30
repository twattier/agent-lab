#!/bin/bash
# AgentLab Development Environment Validation Script
#
# This script validates that all required services and dependencies
# are properly installed and configured for development.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo ""
    echo "================================================"
    echo "$1"
    echo "================================================"
}

# Check command exists
check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Check Node.js version
check_node_version() {
    local required_version="18.17.0"
    local current_version=$(node --version | sed 's/v//')

    if [ "$(printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1)" = "$required_version" ]; then
        print_success "Node.js version $current_version (>= $required_version required)"
    else
        print_error "Node.js version $current_version is too old (>= $required_version required)"
    fi
}

# Check Python version
check_python_version() {
    local required_version="3.11.0"
    local current_version=$(python3 --version | awk '{print $2}')

    if [ "$(printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1)" = "$required_version" ]; then
        print_success "Python version $current_version (>= $required_version required)"
    else
        print_error "Python version $current_version is too old (>= $required_version required)"
    fi
}

# Check Docker status
check_docker() {
    if docker ps &> /dev/null; then
        print_success "Docker is running"
    else
        print_error "Docker is not running"
    fi
}

# Check PostgreSQL service
check_postgres() {
    if docker ps | grep -q "agentlab-postgres"; then
        print_success "PostgreSQL container is running"

        # Check connectivity
        if pg_isready -h localhost -p 5434 -U agentlab &> /dev/null || nc -z localhost 5434 &> /dev/null; then
            print_success "PostgreSQL is accepting connections on port 5434"
        else
            print_error "PostgreSQL is not accepting connections on port 5434"
        fi
    else
        print_error "PostgreSQL container is not running"
    fi
}

# Check Redis service
check_redis() {
    if docker ps | grep -q "redis"; then
        print_success "Redis container is running"
    else
        print_warning "Redis container is not running (optional)"
    fi
}

# Check API health endpoint
check_api_health() {
    if curl -sf http://localhost:8001/api/v1/health > /dev/null 2>&1; then
        print_success "API health endpoint is responsive"
    else
        print_warning "API is not running (run 'npm run dev' to start)"
    fi
}

# Check Python dependencies
check_python_deps() {
    cd apps/api
    if python3 -c "import fastapi, sqlalchemy, alembic, pytest" 2>/dev/null; then
        print_success "Core Python dependencies are installed"
    else
        print_error "Some Python dependencies are missing (run 'pip install -e .[dev]')"
    fi
    cd ../..
}

# Check Node dependencies
check_node_deps() {
    if [ -d "node_modules" ]; then
        print_success "Node dependencies are installed"
    else
        print_error "Node dependencies are missing (run 'npm install')"
    fi
}

# Check environment files
check_env_files() {
    if [ -f ".env" ] || [ -f ".env.development" ]; then
        print_success "Environment file exists"
    else
        print_warning "No .env file found (copy .env.example to .env)"
    fi

    if [ -f ".env.test" ]; then
        print_success "Test environment file exists"
    else
        print_warning "No .env.test file found"
    fi
}

# Main validation
main() {
    print_header "AgentLab Environment Validation"

    print_header "System Dependencies"
    check_command node
    check_command npm
    check_command python3
    check_command pip3
    check_command docker
    check_command docker-compose
    check_command git

    print_header "Version Checks"
    check_node_version
    check_python_version

    print_header "Docker Services"
    check_docker
    check_postgres
    check_redis

    print_header "Dependencies"
    check_python_deps
    check_node_deps
    check_env_files

    print_header "Service Health"
    check_api_health

    # Summary
    print_header "Validation Summary"
    echo "Checks passed: $CHECKS_PASSED"
    echo "Checks failed: $CHECKS_FAILED"

    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All critical checks passed!${NC}"
        echo "Your development environment is ready."
        exit 0
    else
        echo -e "${RED}Some checks failed.${NC}"
        echo "Please resolve the issues above before proceeding."
        exit 1
    fi
}

# Run main
main
