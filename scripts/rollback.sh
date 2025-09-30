#!/bin/bash
# Rollback Automation Script
# This script rolls back to the previous Docker image version

set -euo pipefail  # Stricter error handling: exit on error, undefined variables, pipe failures

# Configuration
REGISTRY="ghcr.io"
REPO_NAME="${GITHUB_REPOSITORY:-agentlab/agent-lab}"
ENVIRONMENT="${1:-production}"
COMPOSE_FILE="docker-compose.yml"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-60}"  # seconds
ROLLBACK_TIMEOUT="${ROLLBACK_TIMEOUT:-180}"  # 3 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get current running image
get_current_image() {
    local service=$1
    local container_id
    container_id=$(docker-compose ps -q "$service" 2>/dev/null)
    if [ -z "$container_id" ]; then
        echo "none"
        return
    fi
    docker inspect "$container_id" --format='{{.Config.Image}}' 2>/dev/null || echo "none"
}

# Function to get previous image tag
get_previous_tag() {
    local service=$1
    local tags
    tags=$(docker images --format "{{.Tag}}" "${REGISTRY}/${REPO_NAME}/${service}" 2>/dev/null | grep -v '^<none>$' | head -2)
    local tag_count
    tag_count=$(echo "$tags" | wc -l)

    if [ "$tag_count" -lt 2 ]; then
        log_error "Not enough image versions available for $service (need at least 2)"
        return 1
    fi

    echo "$tags" | tail -1
}

# Function to perform health check with timeout
health_check() {
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 2))
    local attempt=0
    local health_url="${HEALTH_URL:-http://localhost:8000/api/v1/health}"

    log_info "Performing health check on $health_url..."

    while [ "$attempt" -lt "$max_attempts" ]; do
        if curl -f --max-time 5 --retry 0 "$health_url" > /dev/null 2>&1; then
            log_info "Health check passed!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    log_error "Health check failed after $max_attempts attempts (${HEALTH_CHECK_TIMEOUT}s timeout)"
    return 1
}

# Function to create rollback snapshot for potential revert
create_rollback_snapshot() {
    log_info "Creating rollback snapshot..."
    echo "$(date -Iseconds)" > /tmp/rollback-timestamp-"$ENVIRONMENT".txt
    docker-compose ps -q web api > /tmp/rollback-containers-"$ENVIRONMENT".txt 2>/dev/null || true
}

# Main rollback logic
rollback() {
    log_info "Starting rollback for environment: $ENVIRONMENT"

    # Get current images
    current_web=$(get_current_image web)
    current_api=$(get_current_image api)

    log_info "Current web image: $current_web"
    log_info "Current API image: $current_api"

    # Create snapshot of current state (in case rollback fails)
    create_rollback_snapshot

    # Get previous tags
    previous_web_tag=$(get_previous_tag web) || exit 1
    previous_api_tag=$(get_previous_tag api) || exit 1

    if [ -z "$previous_web_tag" ] || [ -z "$previous_api_tag" ]; then
        log_error "Could not determine previous image tags"
        exit 1
    fi

    log_info "Rolling back web to: ${REGISTRY}/${REPO_NAME}/web:${previous_web_tag}"
    log_info "Rolling back API to: ${REGISTRY}/${REPO_NAME}/api:${previous_api_tag}"

    # Update docker-compose to use previous tags
    export WEB_IMAGE="${REGISTRY}/${REPO_NAME}/web:${previous_web_tag}"
    export API_IMAGE="${REGISTRY}/${REPO_NAME}/api:${previous_api_tag}"

    # Verify previous images exist in registry
    log_info "Verifying previous images exist..."
    if ! docker manifest inspect "$WEB_IMAGE" > /dev/null 2>&1; then
        log_error "Previous web image not found: $WEB_IMAGE"
        exit 1
    fi
    if ! docker manifest inspect "$API_IMAGE" > /dev/null 2>&1; then
        log_error "Previous API image not found: $API_IMAGE"
        exit 1
    fi

    # Pull previous images
    log_info "Pulling previous images..."
    docker pull "$WEB_IMAGE" || { log_error "Failed to pull web image"; exit 1; }
    docker pull "$API_IMAGE" || { log_error "Failed to pull API image"; exit 1; }

    # Stop current containers with timeout
    log_info "Stopping current containers..."
    timeout "$ROLLBACK_TIMEOUT" docker-compose stop web api || {
        log_error "Failed to stop containers within timeout"
        exit 1
    }

    # Start containers with previous images
    log_info "Starting containers with previous images..."
    timeout "$ROLLBACK_TIMEOUT" docker-compose up -d web api || {
        log_error "Failed to start containers within timeout"
        exit 1
    }

    # Wait for services to start
    log_info "Waiting for services to initialize..."
    sleep 10

    # Perform health check
    if health_check; then
        log_info "Rollback completed successfully!"

        # Cleanup old images
        log_info "Cleaning up old images..."
        docker image prune -f

        exit 0
    else
        log_error "Rollback failed health check!"
        log_error "Manual intervention required"
        exit 1
    fi
}

# Script entry point
if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    log_error "Invalid environment: $ENVIRONMENT"
    log_error "Usage: $0 [production|staging]"
    exit 1
fi

log_warn "This will rollback $ENVIRONMENT to the previous deployment"
log_warn "Press Ctrl+C within 5 seconds to cancel..."
sleep 5

rollback
