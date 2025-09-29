#!/bin/bash

# AgentLab Infrastructure Testing Script
# Comprehensive testing of Docker infrastructure

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_ENVIRONMENT="${TEST_ENVIRONMENT:-test}"
COMPOSE_FILE="docker-compose.test.yml"
CLEANUP_AFTER_TEST="${CLEANUP_AFTER_TEST:-true}"
PARALLEL_TESTS="${PARALLEL_TESTS:-false}"

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
        Infrastructure Testing
EOF
    echo ""
}

check_test_dependencies() {
    log_info "Checking test dependencies..."

    local missing_deps=()

    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi

    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    if ! python3 -c "import pytest" 2>/dev/null; then
        missing_deps+=("pytest")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing test dependencies: ${missing_deps[*]}"
        echo ""
        echo "Install missing dependencies:"
        echo "  pip install pytest pytest-timeout requests docker redis psycopg2-binary"
        exit 1
    fi

    log_success "All test dependencies are available"
}

setup_test_environment() {
    log_info "Setting up test environment..."

    # Ensure test compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Test compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    # Create test data directories
    mkdir -p ./infrastructure/postgres/test-data
    mkdir -p ./infrastructure/redis
    mkdir -p ./tests/infrastructure
    mkdir -p ./test-results

    # Create test-specific Redis config if it doesn't exist
    if [[ ! -f "./infrastructure/redis/redis-test.conf" ]]; then
        log_info "Creating test Redis configuration..."
        cat > "./infrastructure/redis/redis-test.conf" << 'EOF'
# Redis test configuration
bind 0.0.0.0
protected-mode no
port 6379
databases 16
save ""
appendonly no
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF
    fi

    # Create test database initialization script
    if [[ ! -f "./infrastructure/postgres/test-data/test-data.sql" ]]; then
        log_info "Creating test database initialization script..."
        cat > "./infrastructure/postgres/test-data/test-data.sql" << 'EOF'
-- Test data initialization for AgentLab test database
-- This runs after the main initialization scripts

-- Create test schema
CREATE SCHEMA IF NOT EXISTS test_data;

-- Insert some test data for testing
INSERT INTO agentlab.test_table (name, value) VALUES
    ('test1', 'value1'),
    ('test2', 'value2')
ON CONFLICT DO NOTHING;

-- Verify pgvector extension is working
CREATE TABLE IF NOT EXISTS test_data.vector_test (
    id SERIAL PRIMARY KEY,
    embedding vector(128),
    metadata JSONB
);

INSERT INTO test_data.vector_test (embedding, metadata) VALUES
    (ARRAY_FILL(0.1, ARRAY[128])::vector, '{"test": true}'),
    (ARRAY_FILL(0.2, ARRAY[128])::vector, '{"test": true}')
ON CONFLICT DO NOTHING;

RAISE NOTICE 'Test data initialization completed';
EOF
    fi

    log_success "Test environment setup completed"
}

start_test_infrastructure() {
    log_info "Starting test infrastructure..."

    # Stop any existing test containers
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans --volumes 2>/dev/null || true

    # Start test infrastructure
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        log_success "Test infrastructure started"
    else
        log_error "Failed to start test infrastructure"
        return 1
    fi

    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 15

    # Check service health
    local max_retries=30
    local retry_delay=5

    for ((i=1; i<=max_retries; i++)); do
        log_info "Health check attempt $i/$max_retries"

        local all_healthy=true

        # Check PostgreSQL
        if ! docker-compose -f "$COMPOSE_FILE" exec -T postgres-test pg_isready -U agentlab_test_user -d agentlab_test >/dev/null 2>&1; then
            all_healthy=false
        fi

        # Check Redis
        if ! docker-compose -f "$COMPOSE_FILE" exec -T redis-test redis-cli ping >/dev/null 2>&1; then
            all_healthy=false
        fi

        if [[ "$all_healthy" == true ]]; then
            log_success "All test services are ready"
            return 0
        fi

        if [[ $i -lt $max_retries ]]; then
            log_info "Waiting ${retry_delay}s before next check..."
            sleep "$retry_delay"
        fi
    done

    log_error "Test services did not become ready within timeout"
    return 1
}

run_infrastructure_tests() {
    log_info "Running infrastructure tests..."

    local test_args=(
        "./tests/infrastructure/test_docker_infrastructure.py"
        "-v"
        "--tb=short"
        "--timeout=300"
        "--color=yes"
        "--junitxml=./test-results/infrastructure-test-results.xml"
    )

    if [[ "$PARALLEL_TESTS" == "true" ]]; then
        test_args+=("-n" "auto")
    fi

    # Set environment variables for tests
    export TEST_COMPOSE_FILE="$COMPOSE_FILE"
    export TEST_POSTGRES_HOST="localhost"
    export TEST_POSTGRES_PORT="5433"
    export TEST_POSTGRES_USER="agentlab_test_user"
    export TEST_POSTGRES_PASSWORD="test_password"
    export TEST_POSTGRES_DB="agentlab_test"
    export TEST_REDIS_HOST="localhost"
    export TEST_REDIS_PORT="6380"
    export TEST_REDIS_PASSWORD="test_redis_password"

    if python3 -m pytest "${test_args[@]}"; then
        log_success "Infrastructure tests passed"
        return 0
    else
        log_error "Infrastructure tests failed"
        return 1
    fi
}

run_security_scan() {
    log_info "Running security scan..."

    if [[ -f "./infrastructure/security/security-scan.sh" ]]; then
        if ./infrastructure/security/security-scan.sh; then
            log_success "Security scan passed"
        else
            log_warning "Security scan found issues (check scan results)"
        fi
    else
        log_warning "Security scan script not found, skipping"
    fi
}

run_performance_tests() {
    log_info "Running performance tests..."

    # Basic performance tests
    local performance_passed=true

    # Test database startup time
    log_info "Testing database startup performance..."
    local start_time=$(date +%s)
    if docker-compose -f "$COMPOSE_FILE" restart postgres-test; then
        # Wait for database to be ready
        local ready=false
        for ((i=1; i<=30; i++)); do
            if docker-compose -f "$COMPOSE_FILE" exec -T postgres-test pg_isready -U agentlab_test_user >/dev/null 2>&1; then
                ready=true
                break
            fi
            sleep 1
        done

        local end_time=$(date +%s)
        local startup_time=$((end_time - start_time))

        if [[ "$ready" == true && $startup_time -lt 60 ]]; then
            log_success "Database startup time: ${startup_time}s (target: <60s)"
        else
            log_warning "Database startup time: ${startup_time}s (slower than target)"
            performance_passed=false
        fi
    else
        log_error "Failed to restart database for performance test"
        performance_passed=false
    fi

    # Test Redis startup time
    log_info "Testing Redis startup performance..."
    start_time=$(date +%s)
    if docker-compose -f "$COMPOSE_FILE" restart redis-test; then
        # Wait for Redis to be ready
        local ready=false
        for ((i=1; i<=30; i++)); do
            if docker-compose -f "$COMPOSE_FILE" exec -T redis-test redis-cli ping >/dev/null 2>&1; then
                ready=true
                break
            fi
            sleep 1
        done

        local end_time=$(date +%s)
        local startup_time=$((end_time - start_time))

        if [[ "$ready" == true && $startup_time -lt 30 ]]; then
            log_success "Redis startup time: ${startup_time}s (target: <30s)"
        else
            log_warning "Redis startup time: ${startup_time}s (slower than target)"
            performance_passed=false
        fi
    else
        log_error "Failed to restart Redis for performance test"
        performance_passed=false
    fi

    if [[ "$performance_passed" == true ]]; then
        log_success "Performance tests passed"
        return 0
    else
        log_warning "Some performance tests did not meet targets"
        return 1
    fi
}

generate_test_report() {
    log_info "Generating test report..."

    local report_file="./test-results/infrastructure-test-report-$(date +%Y%m%d-%H%M%S).txt"

    cat > "$report_file" << EOF
AgentLab Infrastructure Test Report
Generated: $(date)
Environment: $TEST_ENVIRONMENT
Compose File: $COMPOSE_FILE

Test Summary:
EOF

    # Add container status
    echo "" >> "$report_file"
    echo "Container Status:" >> "$report_file"
    docker-compose -f "$COMPOSE_FILE" ps >> "$report_file" 2>/dev/null || echo "Could not get container status" >> "$report_file"

    # Add system resources
    echo "" >> "$report_file"
    echo "System Resources:" >> "$report_file"
    echo "Memory:" >> "$report_file"
    free -h >> "$report_file" 2>/dev/null || echo "Memory info not available" >> "$report_file"

    echo "" >> "$report_file"
    echo "Disk:" >> "$report_file"
    df -h >> "$report_file" 2>/dev/null || echo "Disk info not available" >> "$report_file"

    # Add Docker info
    echo "" >> "$report_file"
    echo "Docker System:" >> "$report_file"
    docker system df >> "$report_file" 2>/dev/null || echo "Docker system info not available" >> "$report_file"

    log_success "Test report generated: $report_file"
}

cleanup_test_environment() {
    if [[ "$CLEANUP_AFTER_TEST" == "true" ]]; then
        log_info "Cleaning up test environment..."

        # Stop and remove test containers
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans --volumes

        # Remove test images if they were built
        docker image prune -f --filter "label=test=true" 2>/dev/null || true

        log_success "Test environment cleaned up"
    else
        log_info "Test environment cleanup skipped"
    fi
}

# Main test function
main() {
    show_banner

    log_info "Starting AgentLab infrastructure tests..."
    echo "Environment: $TEST_ENVIRONMENT"
    echo "Compose File: $COMPOSE_FILE"
    echo "Cleanup After Test: $CLEANUP_AFTER_TEST"
    echo ""

    local overall_success=true

    # Setup and run tests
    check_test_dependencies || overall_success=false
    setup_test_environment || overall_success=false

    if [[ "$overall_success" == true ]]; then
        start_test_infrastructure || overall_success=false
    fi

    if [[ "$overall_success" == true ]]; then
        run_infrastructure_tests || overall_success=false
    fi

    # Run additional tests (don't fail overall on these)
    run_security_scan || true
    run_performance_tests || true

    generate_test_report

    # Cleanup
    cleanup_test_environment

    if [[ "$overall_success" == true ]]; then
        log_success "All infrastructure tests completed successfully!"
        exit 0
    else
        log_error "Some infrastructure tests failed"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
AgentLab Infrastructure Testing Script

Usage: $0 [OPTIONS]

Options:
    -h, --help                      Show this help message
    -e, --environment ENV           Test environment (default: test)
    -f, --file FILE                 Docker Compose file (default: docker-compose.test.yml)
    --no-cleanup                    Don't cleanup after tests
    --parallel                      Run tests in parallel
    --security-only                 Run only security scan
    --performance-only              Run only performance tests

Examples:
    $0                              # Run all tests with defaults
    $0 --no-cleanup                 # Keep test environment after tests
    $0 --parallel                   # Run tests in parallel
    $0 --security-only              # Run only security scan

EOF
}

# Parse command line arguments
SECURITY_ONLY=false
PERFORMANCE_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--environment)
            TEST_ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        --no-cleanup)
            CLEANUP_AFTER_TEST=false
            shift
            ;;
        --parallel)
            PARALLEL_TESTS=true
            shift
            ;;
        --security-only)
            SECURITY_ONLY=true
            shift
            ;;
        --performance-only)
            PERFORMANCE_ONLY=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Modify execution based on flags
if [[ "$SECURITY_ONLY" == true ]]; then
    run_security_scan
    exit $?
elif [[ "$PERFORMANCE_ONLY" == true ]]; then
    setup_test_environment
    start_test_infrastructure
    run_performance_tests
    cleanup_test_environment
    exit $?
fi

# Run main function
main "$@"