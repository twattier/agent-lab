#!/bin/bash

# AgentLab Health Check Script
# Comprehensive health monitoring for all services

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
TIMEOUT="${TIMEOUT:-30}"
RETRY_COUNT="${RETRY_COUNT:-5}"
RETRY_DELAY="${RETRY_DELAY:-5}"

# Services to check
SERVICES=(
    "postgres:5432"
    "redis:6379"
    "api:8000"
    "web:3000"
    "nginx:80"
)

# Health check endpoints
HEALTH_ENDPOINTS=(
    "http://localhost:8000/health:API Health Check"
    "http://localhost:3000/api/health:Web App Health Check"
    "http://localhost/health:Nginx Health Check"
)

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

check_docker_compose() {
    log_info "Checking Docker Compose setup..."

    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    log_success "Docker Compose is available"
}

check_container_status() {
    log_info "Checking container status..."

    local all_healthy=true

    # Get container status
    if command -v docker-compose &> /dev/null; then
        containers=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.State}}\t{{.Status}}")
    else
        containers=$(docker compose -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.State}}\t{{.Status}}")
    fi

    echo "$containers"
    echo ""

    # Check each service
    for service_port in "${SERVICES[@]}"; do
        service=${service_port%:*}
        port=${service_port#*:}

        log_info "Checking service: $service"

        # Check if container is running
        if command -v docker-compose &> /dev/null; then
            container_status=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" | xargs docker inspect --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
        else
            container_status=$(docker compose -f "$COMPOSE_FILE" ps -q "$service" | xargs docker inspect --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
        fi

        case "$container_status" in
            "running")
                log_success "Container $service is running"
                ;;
            "exited")
                log_error "Container $service has exited"
                all_healthy=false
                ;;
            "not_found")
                log_warning "Container $service not found (may not be started)"
                all_healthy=false
                ;;
            *)
                log_warning "Container $service status: $container_status"
                ;;
        esac
    done

    if [[ "$all_healthy" != true ]]; then
        log_error "Some containers are not running properly"
        return 1
    fi

    log_success "All containers are running"
    return 0
}

check_port_connectivity() {
    log_info "Checking port connectivity..."

    local all_ports_open=true

    for service_port in "${SERVICES[@]}"; do
        service=${service_port%:*}
        port=${service_port#*:}

        log_info "Checking port connectivity: $service:$port"

        # Check if port is accessible
        if timeout "$TIMEOUT" bash -c "</dev/tcp/localhost/$port" 2>/dev/null; then
            log_success "Port $port is accessible"
        else
            log_error "Port $port is not accessible"
            all_ports_open=false
        fi
    done

    if [[ "$all_ports_open" != true ]]; then
        log_error "Some ports are not accessible"
        return 1
    fi

    log_success "All ports are accessible"
    return 0
}

check_health_endpoints() {
    log_info "Checking health endpoints..."

    local all_endpoints_healthy=true

    for endpoint_info in "${HEALTH_ENDPOINTS[@]}"; do
        endpoint=${endpoint_info%:*}
        description=${endpoint_info#*:}

        log_info "Checking: $description"

        local retry_count=0
        local endpoint_healthy=false

        while [[ $retry_count -lt $RETRY_COUNT ]]; do
            if curl -f -s --max-time "$TIMEOUT" "$endpoint" >/dev/null 2>&1; then
                log_success "$description is healthy"
                endpoint_healthy=true
                break
            else
                ((retry_count++))
                if [[ $retry_count -lt $RETRY_COUNT ]]; then
                    log_warning "$description not ready, retrying ($retry_count/$RETRY_COUNT)..."
                    sleep "$RETRY_DELAY"
                fi
            fi
        done

        if [[ "$endpoint_healthy" != true ]]; then
            log_error "$description failed health check after $RETRY_COUNT attempts"
            all_endpoints_healthy=false
        fi
    done

    if [[ "$all_endpoints_healthy" != true ]]; then
        log_error "Some health endpoints are not responding"
        return 1
    fi

    log_success "All health endpoints are responding"
    return 0
}

check_database_connectivity() {
    log_info "Checking database connectivity..."

    # Check PostgreSQL
    log_info "Testing PostgreSQL connection..."
    if docker exec -it agentlab-postgres-dev pg_isready -U agentlab_user -d agentlab_dev >/dev/null 2>&1 ||
       docker exec -it agentlab-postgres pg_isready -U agentlab_user -d agentlab >/dev/null 2>&1; then
        log_success "PostgreSQL is accepting connections"
    else
        log_error "PostgreSQL is not accepting connections"
        return 1
    fi

    # Check Redis
    log_info "Testing Redis connection..."
    if docker exec -it agentlab-redis-dev redis-cli ping >/dev/null 2>&1 ||
       docker exec -it agentlab-redis redis-cli ping >/dev/null 2>&1; then
        log_success "Redis is accepting connections"
    else
        log_error "Redis is not accepting connections"
        return 1
    fi

    log_success "Database connectivity check passed"
    return 0
}

check_logs_for_errors() {
    log_info "Checking logs for critical errors..."

    local critical_errors_found=false

    for service_port in "${SERVICES[@]}"; do
        service=${service_port%:*}

        log_info "Checking logs for service: $service"

        # Get recent logs and check for errors
        if command -v docker-compose &> /dev/null; then
            recent_logs=$(docker-compose -f "$COMPOSE_FILE" logs --tail=50 "$service" 2>/dev/null || echo "")
        else
            recent_logs=$(docker compose -f "$COMPOSE_FILE" logs --tail=50 "$service" 2>/dev/null || echo "")
        fi

        # Look for critical error patterns
        error_patterns=("ERROR" "FATAL" "CRITICAL" "Exception" "failed" "error")

        for pattern in "${error_patterns[@]}"; do
            if echo "$recent_logs" | grep -i "$pattern" >/dev/null 2>&1; then
                log_warning "Found '$pattern' in $service logs"
                critical_errors_found=true
            fi
        done
    done

    if [[ "$critical_errors_found" == true ]]; then
        log_warning "Some services have error messages in logs (check individual service logs for details)"
        return 1
    fi

    log_success "No critical errors found in recent logs"
    return 0
}

generate_health_report() {
    log_info "Generating health report..."

    local report_file="health-check-report-$(date +%Y%m%d-%H%M%S).txt"

    cat > "$report_file" << EOF
AgentLab Health Check Report
Generated: $(date)
Compose File: $COMPOSE_FILE

Container Status:
EOF

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" ps >> "$report_file" 2>/dev/null || echo "Unable to get container status" >> "$report_file"
    else
        docker compose -f "$COMPOSE_FILE" ps >> "$report_file" 2>/dev/null || echo "Unable to get container status" >> "$report_file"
    fi

    cat >> "$report_file" << EOF

System Resources:
EOF

    # Add system resource information
    echo "Memory Usage:" >> "$report_file"
    free -h >> "$report_file" 2>/dev/null || echo "Unable to get memory info" >> "$report_file"

    echo "" >> "$report_file"
    echo "Disk Usage:" >> "$report_file"
    df -h >> "$report_file" 2>/dev/null || echo "Unable to get disk info" >> "$report_file"

    echo "" >> "$report_file"
    echo "Docker System Info:" >> "$report_file"
    docker system df >> "$report_file" 2>/dev/null || echo "Unable to get Docker system info" >> "$report_file"

    log_success "Health report generated: $report_file"
}

# Main health check function
main() {
    log_info "Starting AgentLab health check..."
    echo "Timeout: ${TIMEOUT}s, Retries: ${RETRY_COUNT}, Delay: ${RETRY_DELAY}s"
    echo ""

    local overall_health=true

    # Run all health checks
    check_docker_compose || overall_health=false
    echo ""

    check_container_status || overall_health=false
    echo ""

    check_port_connectivity || overall_health=false
    echo ""

    check_health_endpoints || overall_health=false
    echo ""

    check_database_connectivity || overall_health=false
    echo ""

    check_logs_for_errors || true  # Don't fail overall health for log warnings
    echo ""

    generate_health_report

    if [[ "$overall_health" == true ]]; then
        log_success "AgentLab health check passed - all systems operational"
        exit 0
    else
        log_error "AgentLab health check failed - issues detected"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
AgentLab Health Check Script

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -f, --file FILE         Docker Compose file to use (default: $COMPOSE_FILE)
    -t, --timeout SECONDS   Timeout for individual checks (default: $TIMEOUT)
    -r, --retries COUNT     Number of retries for health endpoints (default: $RETRY_COUNT)
    -d, --delay SECONDS     Delay between retries (default: $RETRY_DELAY)

Examples:
    $0                                    # Run health check with defaults
    $0 -f docker-compose.dev.yml         # Check development environment
    $0 -t 60 -r 10                      # Use longer timeout and more retries

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -r|--retries)
            RETRY_COUNT="$2"
            shift 2
            ;;
        -d|--delay)
            RETRY_DELAY="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main "$@"