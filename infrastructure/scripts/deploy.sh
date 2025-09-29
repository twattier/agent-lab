#!/bin/bash

# AgentLab Deployment Script
# Automated deployment with zero-downtime rolling updates

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${ENVIRONMENT:-development}"
COMPOSE_FILE=""
IMAGE_TAG="${IMAGE_TAG:-latest}"
DEPLOYMENT_TIMEOUT="${DEPLOYMENT_TIMEOUT:-300}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-30}"
HEALTH_CHECK_DELAY="${HEALTH_CHECK_DELAY:-10}"

# Pre-deployment checks
PRE_DEPLOY_CHECKS="${PRE_DEPLOY_CHECKS:-true}"
POST_DEPLOY_CHECKS="${POST_DEPLOY_CHECKS:-true}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"

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
        Deployment System
EOF
    echo ""
}

determine_compose_file() {
    case "$ENVIRONMENT" in
        "development"|"dev")
            COMPOSE_FILE="docker-compose.dev.yml"
            ;;
        "testing"|"test")
            COMPOSE_FILE="docker-compose.test.yml"
            ;;
        "production"|"prod")
            COMPOSE_FILE="docker-compose.prod.yml"
            ;;
        "swarm")
            COMPOSE_FILE="docker-compose.swarm.yml"
            ;;
        *)
            COMPOSE_FILE="docker-compose.yml"
            ;;
    esac

    log_info "Using compose file: $COMPOSE_FILE for environment: $ENVIRONMENT"

    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
}

check_dependencies() {
    log_info "Checking deployment dependencies..."

    local missing_deps=()

    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi

    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi

    log_success "All dependencies are available"
}

run_pre_deployment_checks() {
    if [[ "$PRE_DEPLOY_CHECKS" != "true" ]]; then
        log_info "Pre-deployment checks disabled"
        return 0
    fi

    log_info "Running pre-deployment checks..."

    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    # Check available disk space
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1048576 ]]; then  # Less than 1GB
        log_warning "Low disk space available: $(numfmt --to=iec $((available_space * 1024)))"
    fi

    # Check if required images exist for production
    if [[ "$ENVIRONMENT" == "production" || "$ENVIRONMENT" == "prod" ]]; then
        required_images=("agentlab/api:${IMAGE_TAG}" "agentlab/web:${IMAGE_TAG}")
        for image in "${required_images[@]}"; do
            if ! docker image inspect "$image" >/dev/null 2>&1; then
                log_error "Required image not found: $image"
                log_info "Please build the images first: docker build -t $image ."
                exit 1
            fi
        done
    fi

    # Check for existing deployment
    if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
        log_info "Existing deployment detected"
    else
        log_info "No existing deployment found"
    fi

    log_success "Pre-deployment checks passed"
}

backup_current_deployment() {
    if [[ "$BACKUP_BEFORE_DEPLOY" != "true" ]]; then
        log_info "Pre-deployment backup disabled"
        return 0
    fi

    log_info "Creating pre-deployment backup..."

    if [[ -f "./infrastructure/backups/backup.sh" ]]; then
        if ./infrastructure/backups/backup.sh; then
            log_success "Pre-deployment backup completed"
        else
            log_warning "Pre-deployment backup failed (continuing with deployment)"
        fi
    else
        log_warning "Backup script not found, skipping backup"
    fi
}

pull_latest_images() {
    log_info "Pulling latest images..."

    if docker-compose -f "$COMPOSE_FILE" pull; then
        log_success "Images pulled successfully"
    else
        log_error "Failed to pull images"
        exit 1
    fi
}

perform_deployment() {
    log_info "Starting deployment..."

    case "$ENVIRONMENT" in
        "swarm")
            deploy_swarm
            ;;
        *)
            deploy_compose
            ;;
    esac
}

deploy_compose() {
    log_info "Deploying with Docker Compose..."

    # Stop existing services gracefully
    if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
        log_info "Stopping existing services..."
        docker-compose -f "$COMPOSE_FILE" down --timeout 30
    fi

    # Start services
    log_info "Starting services..."
    if docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        return 1
    fi

    # Wait for services to be ready
    wait_for_services
}

deploy_swarm() {
    log_info "Deploying with Docker Swarm..."

    # Check if swarm is initialized
    if ! docker info | grep -q "Swarm: active"; then
        log_info "Initializing Docker Swarm..."
        docker swarm init
    fi

    # Deploy stack
    log_info "Deploying stack..."
    if docker stack deploy -c "$COMPOSE_FILE" agentlab; then
        log_success "Stack deployed successfully"
    else
        log_error "Failed to deploy stack"
        return 1
    fi

    # Wait for services to be ready
    wait_for_swarm_services
}

wait_for_services() {
    log_info "Waiting for services to be ready..."

    local services=("postgres" "redis" "api" "web")
    local ready_services=()

    for ((i=1; i<=HEALTH_CHECK_RETRIES; i++)); do
        log_info "Health check attempt $i/$HEALTH_CHECK_RETRIES"

        for service in "${services[@]}"; do
            if [[ " ${ready_services[*]} " =~ " ${service} " ]]; then
                continue  # Service already ready
            fi

            case "$service" in
                "postgres")
                    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U agentlab_user >/dev/null 2>&1; then
                        log_success "PostgreSQL is ready"
                        ready_services+=("postgres")
                    fi
                    ;;
                "redis")
                    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
                        log_success "Redis is ready"
                        ready_services+=("redis")
                    fi
                    ;;
                "api")
                    if curl -f -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1; then
                        log_success "API is ready"
                        ready_services+=("api")
                    fi
                    ;;
                "web")
                    if curl -f -s --max-time 5 http://localhost:3000/api/health >/dev/null 2>&1; then
                        log_success "Web app is ready"
                        ready_services+=("web")
                    fi
                    ;;
            esac
        done

        # Check if all services are ready
        if [[ ${#ready_services[@]} -eq ${#services[@]} ]]; then
            log_success "All services are ready"
            return 0
        fi

        if [[ $i -lt $HEALTH_CHECK_RETRIES ]]; then
            log_info "Waiting ${HEALTH_CHECK_DELAY}s before next check..."
            sleep "$HEALTH_CHECK_DELAY"
        fi
    done

    log_error "Services did not become ready within timeout"
    return 1
}

wait_for_swarm_services() {
    log_info "Waiting for swarm services to be ready..."

    for ((i=1; i<=HEALTH_CHECK_RETRIES; i++)); do
        log_info "Swarm health check attempt $i/$HEALTH_CHECK_RETRIES"

        # Check service replicas
        local all_ready=true
        while read -r service replicas; do
            if [[ "$replicas" == "0/0" ]]; then
                continue  # Skip services with 0 replicas
            fi

            current=$(echo "$replicas" | cut -d'/' -f1)
            desired=$(echo "$replicas" | cut -d'/' -f2)

            if [[ "$current" != "$desired" ]]; then
                log_info "Service $service: $current/$desired replicas ready"
                all_ready=false
            else
                log_success "Service $service: $replicas replicas ready"
            fi
        done < <(docker service ls --format "{{.Name}} {{.Replicas}}" --filter "label=com.docker.stack.namespace=agentlab")

        if [[ "$all_ready" == true ]]; then
            log_success "All swarm services are ready"
            return 0
        fi

        if [[ $i -lt $HEALTH_CHECK_RETRIES ]]; then
            log_info "Waiting ${HEALTH_CHECK_DELAY}s before next check..."
            sleep "$HEALTH_CHECK_DELAY"
        fi
    done

    log_error "Swarm services did not become ready within timeout"
    return 1
}

run_post_deployment_checks() {
    if [[ "$POST_DEPLOY_CHECKS" != "true" ]]; then
        log_info "Post-deployment checks disabled"
        return 0
    fi

    log_info "Running post-deployment checks..."

    # Run health check script if available
    if [[ -f "./infrastructure/scripts/health-check.sh" ]]; then
        if ./infrastructure/scripts/health-check.sh -f "$COMPOSE_FILE"; then
            log_success "Health check passed"
        else
            log_error "Health check failed"
            return 1
        fi
    else
        log_warning "Health check script not found"
    fi

    # Basic connectivity tests
    local endpoints=(
        "http://localhost:8000/health:API"
        "http://localhost:3000/api/health:Web"
    )

    for endpoint_info in "${endpoints[@]}"; do
        endpoint=${endpoint_info%:*}
        name=${endpoint_info#*:}

        if curl -f -s --max-time 10 "$endpoint" >/dev/null; then
            log_success "$name endpoint is responding"
        else
            log_error "$name endpoint is not responding"
            return 1
        fi
    done

    log_success "Post-deployment checks passed"
}

show_deployment_status() {
    log_info "Deployment Status:"

    if [[ "$ENVIRONMENT" == "swarm" ]]; then
        echo ""
        docker service ls --filter "label=com.docker.stack.namespace=agentlab"
        echo ""
        docker stack ps agentlab
    else
        echo ""
        docker-compose -f "$COMPOSE_FILE" ps
        echo ""
        log_info "Service URLs:"
        echo "  API: http://localhost:8000"
        echo "  Web: http://localhost:3000"
        echo "  API Health: http://localhost:8000/health"
        echo "  Web Health: http://localhost:3000/api/health"

        if [[ "$ENVIRONMENT" == "development" ]]; then
            echo "  PgAdmin: http://localhost:8080"
            echo "  Redis Commander: http://localhost:8081"
        fi
    fi
}

rollback_deployment() {
    log_error "Deployment failed, initiating rollback..."

    if [[ "$ENVIRONMENT" == "swarm" ]]; then
        log_info "Rolling back swarm stack..."
        docker stack rm agentlab
        log_info "Wait for stack removal to complete, then redeploy previous version"
    else
        log_info "Rolling back compose deployment..."
        docker-compose -f "$COMPOSE_FILE" down
        log_info "Previous deployment stopped. Manual intervention required."
    fi
}

# Main deployment function
main() {
    show_banner

    log_info "Starting AgentLab deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Image Tag: $IMAGE_TAG"
    log_info "Timeout: ${DEPLOYMENT_TIMEOUT}s"
    echo ""

    determine_compose_file
    check_dependencies
    run_pre_deployment_checks
    backup_current_deployment

    # Don't pull images for development (they're built locally)
    if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "dev" ]]; then
        pull_latest_images
    fi

    if perform_deployment && run_post_deployment_checks; then
        log_success "Deployment completed successfully!"
        show_deployment_status
        exit 0
    else
        rollback_deployment
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
AgentLab Deployment Script

Usage: $0 [OPTIONS]

Options:
    -h, --help                      Show this help message
    -e, --environment ENV           Deployment environment (dev, test, prod, swarm)
    -t, --tag TAG                   Docker image tag (default: latest)
    -f, --file FILE                 Override compose file detection
    --timeout SECONDS               Deployment timeout (default: 300)
    --skip-pre-checks              Skip pre-deployment checks
    --skip-post-checks             Skip post-deployment checks
    --skip-backup                  Skip pre-deployment backup
    --health-retries COUNT         Health check retry count (default: 30)
    --health-delay SECONDS         Health check delay (default: 10)

Environments:
    dev, development               Use docker-compose.dev.yml
    test, testing                  Use docker-compose.test.yml
    prod, production               Use docker-compose.prod.yml
    swarm                          Use docker-compose.swarm.yml (Docker Swarm)

Examples:
    $0 -e dev                      # Deploy development environment
    $0 -e prod -t v1.2.3           # Deploy production with specific tag
    $0 -e swarm --skip-backup      # Deploy to swarm without backup

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        --timeout)
            DEPLOYMENT_TIMEOUT="$2"
            shift 2
            ;;
        --skip-pre-checks)
            PRE_DEPLOY_CHECKS=false
            shift
            ;;
        --skip-post-checks)
            POST_DEPLOY_CHECKS=false
            shift
            ;;
        --skip-backup)
            BACKUP_BEFORE_DEPLOY=false
            shift
            ;;
        --health-retries)
            HEALTH_CHECK_RETRIES="$2"
            shift 2
            ;;
        --health-delay)
            HEALTH_CHECK_DELAY="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set environment variables for docker-compose
export IMAGE_TAG
export ENVIRONMENT

# Run main function
main "$@"