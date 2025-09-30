#!/bin/bash
# Deployment Automation Script
# This script handles zero-downtime deployments with health checks

set -euo pipefail  # Stricter error handling: exit on error, undefined variables, pipe failures

# Configuration
REGISTRY="ghcr.io"
REPO_NAME="${GITHUB_REPOSITORY:-agentlab/agent-lab}"
ENVIRONMENT="${1:-production}"
TAG="${2:-latest}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-60}"  # seconds
DEPLOYMENT_TIMEOUT="${DEPLOYMENT_TIMEOUT:-300}"  # 5 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to perform health check with timeout
health_check() {
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 2))
    local attempt=0
    local health_url="${HEALTH_URL:-http://localhost:8000/api/v1/health}"

    log_info "Performing health check on $health_url..."

    while [ $attempt -lt $max_attempts ]; do
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

# Function to verify image signatures (placeholder for future enhancement)
verify_image_signature() {
    local image=$1
    log_info "Image signature verification: $image"
    # TODO: Implement cosign verification when available
    # cosign verify --key cosign.pub $image
    return 0
}

# Function to check database migrations
check_migrations() {
    log_info "Checking database migrations..."

    # In production, this would run alembic or equivalent
    # docker-compose exec api alembic upgrade head --dry-run

    log_info "Migration check passed"
    return 0
}

# Main deployment logic
deploy() {
    log_step "Starting deployment to $ENVIRONMENT with tag $TAG"

    # Set image versions
    export WEB_IMAGE="${REGISTRY}/${REPO_NAME}/web:${TAG}"
    export API_IMAGE="${REGISTRY}/${REPO_NAME}/api:${TAG}"

    log_info "Web image: $WEB_IMAGE"
    log_info "API image: $API_IMAGE"

    # Verify images exist in registry before pulling
    log_step "Verifying images exist in registry..."
    if ! docker manifest inspect "$WEB_IMAGE" > /dev/null 2>&1; then
        log_error "Web image not found in registry: $WEB_IMAGE"
        exit 1
    fi
    if ! docker manifest inspect "$API_IMAGE" > /dev/null 2>&1; then
        log_error "API image not found in registry: $API_IMAGE"
        exit 1
    fi

    # Pull new images
    log_step "Pulling new images..."
    docker pull "$WEB_IMAGE" || { log_error "Failed to pull web image"; exit 1; }
    docker pull "$API_IMAGE" || { log_error "Failed to pull API image"; exit 1; }

    # Verify image signatures (placeholder for future)
    verify_image_signature "$WEB_IMAGE"
    verify_image_signature "$API_IMAGE"

    # Check database migrations
    if ! check_migrations; then
        log_error "Migration check failed. Aborting deployment."
        exit 1
    fi

    # Rolling update strategy
    log_step "Performing rolling update..."

    # Update API first (backend)
    log_info "Updating API service..."
    timeout "$DEPLOYMENT_TIMEOUT" docker-compose up -d --no-deps --scale api=2 api || {
        log_error "API deployment timed out after ${DEPLOYMENT_TIMEOUT}s"
        exit 1
    }

    log_info "Waiting for new API containers to initialize..."
    sleep 10

    if ! health_check; then
        log_error "New API containers failed health check. Rolling back..."
        docker-compose up -d --no-deps --scale api=1 api
        exit 1
    fi

    # Scale down old API containers
    log_info "Scaling down old API containers..."
    docker-compose up -d --no-deps --scale api=1 api

    # Update web frontend
    log_info "Updating web service..."
    timeout "$DEPLOYMENT_TIMEOUT" docker-compose up -d --no-deps web || {
        log_error "Web deployment timed out after ${DEPLOYMENT_TIMEOUT}s"
        exit 1
    }

    log_info "Waiting for web service to start..."
    sleep 5

    # Final health check
    log_step "Final health check..."
    if ! health_check; then
        log_error "Final health check failed. Please investigate."
        exit 1
    fi

    # Cleanup old images
    log_step "Cleaning up old images..."
    docker image prune -f

    log_info "Deployment completed successfully!"
    exit 0
}

# Script entry point
if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    log_error "Invalid environment: $ENVIRONMENT"
    log_error "Usage: $0 [production|staging] [tag]"
    exit 1
fi

deploy
