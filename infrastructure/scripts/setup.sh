#!/bin/bash

# AgentLab One-Command Setup Script
# Quick setup for local development

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_banner() {
    cat << 'EOF'
    _                    _   _       _
   / \   __ _  ___ _ __ | |_| | __ _| |__
  / _ \ / _` |/ _ \ '_ \| __| |/ _` | '_ \
 / ___ \ (_| |  __/ | | | |_| | (_| | |_) |
/_/   \_\__, |\___|_| |_|\__|_|\__,_|_.__/
        |___/
        Setup & Development
EOF
    echo ""
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    else
        if ! docker info >/dev/null 2>&1; then
            log_error "Docker is installed but not running"
            exit 1
        fi
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node.js")
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo ""
        echo "Please install the missing dependencies:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Node.js: https://nodejs.org/"
        echo "  Python 3: https://python.org/"
        exit 1
    fi

    log_success "All prerequisites are available"
}

setup_environment() {
    log_info "Setting up environment configuration..."

    # Copy environment files if they don't exist
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.development" ]]; then
            log_info "Creating .env from .env.development template"
            cp .env.development .env
        elif [[ -f ".env.example" ]]; then
            log_info "Creating .env from .env.example template"
            cp .env.example .env
        else
            log_warning "No environment template found, creating basic .env"
            cat > .env << 'EOF'
# AgentLab Environment Configuration
POSTGRES_DB=agentlab_dev
POSTGRES_USER=agentlab_user
POSTGRES_PASSWORD=dev_password
REDIS_PASSWORD=dev_redis_password
NEXTAUTH_SECRET=dev_nextauth_secret_change_in_production
NODE_ENV=development
ENV=development
DEBUG=true
EOF
        fi

        log_warning "Please edit .env file and add your API keys:"
        echo "  - CLAUDE_API_KEY=your_claude_api_key_here"
        echo "  - OPENAI_API_KEY=your_openai_api_key_here (optional)"
    else
        log_info "Environment file already exists"
    fi

    # Create necessary directories
    local dirs=(
        "./infrastructure/logs"
        "./coverage"
        "./test-results"
        "./playwright-report"
    )

    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done

    log_success "Environment setup completed"
}

install_dependencies() {
    log_info "Installing project dependencies..."

    # Install Node.js dependencies
    if [[ -f "package.json" ]]; then
        log_info "Installing Node.js dependencies..."
        npm install
        log_success "Node.js dependencies installed"
    fi

    # Build packages
    if [[ -f "package.json" ]]; then
        log_info "Building packages..."
        npm run build --workspaces
        log_success "Packages built successfully"
    fi

    log_success "Dependencies installation completed"
}

start_infrastructure() {
    log_info "Starting AgentLab infrastructure..."

    # Use development compose file
    local compose_file="docker-compose.dev.yml"

    if [[ ! -f "$compose_file" ]]; then
        compose_file="docker-compose.yml"
    fi

    log_info "Using compose file: $compose_file"

    # Start services
    docker-compose -f "$compose_file" up -d --remove-orphans

    log_info "Waiting for services to be ready..."
    sleep 10

    # Check if services are running
    if docker-compose -f "$compose_file" ps | grep -q "Up"; then
        log_success "Infrastructure started successfully"
    else
        log_error "Some services failed to start"
        docker-compose -f "$compose_file" ps
        return 1
    fi
}

run_health_checks() {
    log_info "Running health checks..."

    # Wait a bit longer for services to fully initialize
    sleep 15

    # Run health check script if available
    if [[ -f "./infrastructure/scripts/health-check.sh" ]]; then
        if ./infrastructure/scripts/health-check.sh -f docker-compose.dev.yml; then
            log_success "Health checks passed"
        else
            log_warning "Some health checks failed (this is normal during initial setup)"
        fi
    else
        # Basic manual checks
        local services=("postgres" "redis")
        for service in "${services[@]}"; do
            if docker-compose -f docker-compose.dev.yml ps "$service" | grep -q "Up"; then
                log_success "$service is running"
            else
                log_warning "$service is not running properly"
            fi
        done
    fi
}

show_next_steps() {
    log_success "AgentLab setup completed!"
    echo ""
    echo "🚀 Next steps:"
    echo ""
    echo "1. Edit .env file and add your API keys:"
    echo "   - CLAUDE_API_KEY=your_claude_api_key_here"
    echo "   - OPENAI_API_KEY=your_openai_api_key_here (optional)"
    echo ""
    echo "2. Start development servers:"
    echo "   cd apps/api && python -m uvicorn main:app --reload"
    echo "   cd apps/web && npm run dev"
    echo ""
    echo "3. Access the application:"
    echo "   - Web App: http://localhost:3000"
    echo "   - API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - PgAdmin: http://localhost:8080"
    echo "   - Redis Commander: http://localhost:8081"
    echo ""
    echo "4. Run tests:"
    echo "   npm run test"
    echo "   npm run test:e2e"
    echo ""
    echo "5. Use deployment script for other environments:"
    echo "   ./infrastructure/scripts/deploy.sh -e prod"
    echo ""
    echo "📚 Documentation:"
    echo "   - Architecture: docs/architecture/"
    echo "   - Stories: docs/stories/"
    echo "   - Infrastructure: infrastructure/"
    echo ""
}

# Main setup function
main() {
    show_banner

    log_info "Starting AgentLab setup..."
    echo ""

    check_prerequisites
    setup_environment
    install_dependencies
    start_infrastructure
    run_health_checks

    echo ""
    show_next_steps
}

# Help function
show_help() {
    cat << EOF
AgentLab Setup Script

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    --skip-deps             Skip dependency installation
    --skip-build            Skip package building
    --skip-start            Skip infrastructure startup
    --skip-health           Skip health checks

Examples:
    $0                      # Full setup
    $0 --skip-deps          # Setup without installing dependencies

EOF
}

# Parse command line arguments
SKIP_DEPS=false
SKIP_BUILD=false
SKIP_START=false
SKIP_HEALTH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-start)
            SKIP_START=true
            shift
            ;;
        --skip-health)
            SKIP_HEALTH=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Modify functions based on skip flags
if [[ "$SKIP_DEPS" == true ]]; then
    install_dependencies() { log_info "Skipping dependency installation"; }
fi

if [[ "$SKIP_START" == true ]]; then
    start_infrastructure() { log_info "Skipping infrastructure startup"; }
fi

if [[ "$SKIP_HEALTH" == true ]]; then
    run_health_checks() { log_info "Skipping health checks"; }
fi

# Run main function
main "$@"