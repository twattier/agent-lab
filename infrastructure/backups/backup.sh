#!/bin/bash

# AgentLab Automated Backup Script
# Performs automated backups of PostgreSQL and Redis data

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/opt/agentlab/backups}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
COMPRESSION="${COMPRESSION:-true}"
ENCRYPTION="${ENCRYPTION:-false}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"

# Database configuration
POSTGRES_CONTAINER="agentlab-postgres"
REDIS_CONTAINER="agentlab-redis"
POSTGRES_USER="agentlab_user"
POSTGRES_DB="agentlab"

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

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if [[ "$COMPRESSION" == "true" ]] && ! command -v gzip &> /dev/null; then
        log_error "gzip is required for compression but not found"
        exit 1
    fi

    if [[ "$ENCRYPTION" == "true" ]] && ! command -v gpg &> /dev/null; then
        log_error "gpg is required for encryption but not found"
        exit 1
    fi

    log_success "All dependencies are available"
}

create_backup_directory() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/$timestamp"

    log_info "Creating backup directory: $BACKUP_PATH"
    mkdir -p "$BACKUP_PATH"

    # Create subdirectories
    mkdir -p "$BACKUP_PATH/postgres"
    mkdir -p "$BACKUP_PATH/redis"
    mkdir -p "$BACKUP_PATH/logs"
}

backup_postgres() {
    log_info "Starting PostgreSQL backup..."

    local backup_file="$BACKUP_PATH/postgres/agentlab_$(date +%Y%m%d_%H%M%S).sql"

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^$POSTGRES_CONTAINER$"; then
        log_error "PostgreSQL container $POSTGRES_CONTAINER is not running"
        return 1
    fi

    # Create database dump
    log_info "Creating PostgreSQL dump..."
    if docker exec "$POSTGRES_CONTAINER" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --verbose --no-owner --no-acl > "$backup_file"; then
        log_success "PostgreSQL dump created: $backup_file"

        # Get backup size
        backup_size=$(stat --format="%s" "$backup_file" 2>/dev/null || echo "unknown")
        log_info "Backup size: $(numfmt --to=iec "$backup_size" 2>/dev/null || echo "$backup_size bytes")"

        # Compress if enabled
        if [[ "$COMPRESSION" == "true" ]]; then
            log_info "Compressing PostgreSQL backup..."
            gzip "$backup_file"
            backup_file="${backup_file}.gz"
            compressed_size=$(stat --format="%s" "$backup_file" 2>/dev/null || echo "unknown")
            log_success "Backup compressed: $backup_file"
            log_info "Compressed size: $(numfmt --to=iec "$compressed_size" 2>/dev/null || echo "$compressed_size bytes")"
        fi

        # Encrypt if enabled
        if [[ "$ENCRYPTION" == "true" && -n "$ENCRYPTION_KEY" ]]; then
            log_info "Encrypting PostgreSQL backup..."
            gpg --symmetric --cipher-algo AES256 --passphrase "$ENCRYPTION_KEY" --output "${backup_file}.gpg" "$backup_file"
            rm "$backup_file"
            backup_file="${backup_file}.gpg"
            log_success "Backup encrypted: $backup_file"
        fi

        return 0
    else
        log_error "Failed to create PostgreSQL backup"
        return 1
    fi
}

backup_redis() {
    log_info "Starting Redis backup..."

    local backup_file="$BACKUP_PATH/redis/redis_$(date +%Y%m%d_%H%M%S).rdb"

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^$REDIS_CONTAINER$"; then
        log_error "Redis container $REDIS_CONTAINER is not running"
        return 1
    fi

    # Create Redis backup
    log_info "Creating Redis backup..."
    if docker exec "$REDIS_CONTAINER" redis-cli --rdb /tmp/dump.rdb >/dev/null 2>&1 &&
       docker cp "$REDIS_CONTAINER:/tmp/dump.rdb" "$backup_file"; then
        log_success "Redis backup created: $backup_file"

        # Get backup size
        backup_size=$(stat --format="%s" "$backup_file" 2>/dev/null || echo "unknown")
        log_info "Backup size: $(numfmt --to=iec "$backup_size" 2>/dev/null || echo "$backup_size bytes")"

        # Compress if enabled
        if [[ "$COMPRESSION" == "true" ]]; then
            log_info "Compressing Redis backup..."
            gzip "$backup_file"
            backup_file="${backup_file}.gz"
            compressed_size=$(stat --format="%s" "$backup_file" 2>/dev/null || echo "unknown")
            log_success "Backup compressed: $backup_file"
            log_info "Compressed size: $(numfmt --to=iec "$compressed_size" 2>/dev/null || echo "$compressed_size bytes")"
        fi

        # Encrypt if enabled
        if [[ "$ENCRYPTION" == "true" && -n "$ENCRYPTION_KEY" ]]; then
            log_info "Encrypting Redis backup..."
            gpg --symmetric --cipher-algo AES256 --passphrase "$ENCRYPTION_KEY" --output "${backup_file}.gpg" "$backup_file"
            rm "$backup_file"
            backup_file="${backup_file}.gpg"
            log_success "Backup encrypted: $backup_file"
        fi

        return 0
    else
        log_error "Failed to create Redis backup"
        return 1
    fi
}

backup_logs() {
    log_info "Starting log backup..."

    local logs_backup="$BACKUP_PATH/logs/application_logs_$(date +%Y%m%d_%H%M%S).tar"

    # Find log directories
    log_dirs=()
    if [[ -d "./infrastructure/logs" ]]; then
        log_dirs+=("./infrastructure/logs")
    fi
    if [[ -d "./logs" ]]; then
        log_dirs+=("./logs")
    fi

    if [[ ${#log_dirs[@]} -eq 0 ]]; then
        log_warning "No log directories found, skipping log backup"
        return 0
    fi

    # Create log archive
    log_info "Creating log archive..."
    if tar -cf "$logs_backup" "${log_dirs[@]}" 2>/dev/null; then
        log_success "Log backup created: $logs_backup"

        # Compress if enabled
        if [[ "$COMPRESSION" == "true" ]]; then
            log_info "Compressing log backup..."
            gzip "$logs_backup"
            logs_backup="${logs_backup}.gz"
            log_success "Log backup compressed: $logs_backup"
        fi

        return 0
    else
        log_warning "Failed to create log backup (logs may be empty)"
        return 0
    fi
}

create_backup_manifest() {
    log_info "Creating backup manifest..."

    local manifest_file="$BACKUP_PATH/backup_manifest.txt"

    cat > "$manifest_file" << EOF
AgentLab Backup Manifest
Generated: $(date)
Backup Path: $BACKUP_PATH

Configuration:
  Compression: $COMPRESSION
  Encryption: $ENCRYPTION
  Retention Days: $RETENTION_DAYS

Backup Contents:
EOF

    # List backup files with sizes
    find "$BACKUP_PATH" -type f -name "*.sql*" -o -name "*.rdb*" -o -name "*.tar*" | while read -r file; do
        if [[ -f "$file" ]]; then
            size=$(stat --format="%s" "$file" 2>/dev/null || echo "unknown")
            readable_size=$(numfmt --to=iec "$size" 2>/dev/null || echo "$size bytes")
            echo "  $(basename "$file"): $readable_size" >> "$manifest_file"
        fi
    done

    cat >> "$manifest_file" << EOF

System Information:
  Hostname: $(hostname)
  Docker Version: $(docker --version 2>/dev/null || echo "unknown")
  Backup User: $(whoami)
  Backup Script: $0

Verification:
  MD5 Checksums:
EOF

    # Generate checksums for verification
    find "$BACKUP_PATH" -type f \( -name "*.sql*" -o -name "*.rdb*" -o -name "*.tar*" \) -exec md5sum {} \; >> "$manifest_file" 2>/dev/null || echo "  Unable to generate checksums" >> "$manifest_file"

    log_success "Backup manifest created: $manifest_file"
}

cleanup_old_backups() {
    log_info "Cleaning up old backups (retention: $RETENTION_DAYS days)..."

    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_warning "Backup directory does not exist: $BACKUP_DIR"
        return 0
    fi

    # Find and remove old backup directories
    old_backups=$(find "$BACKUP_DIR" -maxdepth 1 -type d -name "????????_??????" -mtime +$RETENTION_DAYS 2>/dev/null || true)

    if [[ -n "$old_backups" ]]; then
        echo "$old_backups" | while read -r old_backup; do
            if [[ -d "$old_backup" ]]; then
                log_info "Removing old backup: $old_backup"
                rm -rf "$old_backup"
            fi
        done
        log_success "Old backups cleaned up"
    else
        log_info "No old backups to clean up"
    fi
}

verify_backup() {
    log_info "Verifying backup integrity..."

    local verification_passed=true

    # Check if backup files exist and are not empty
    if [[ -d "$BACKUP_PATH/postgres" ]]; then
        postgres_files=$(find "$BACKUP_PATH/postgres" -name "*.sql*" -o -name "*.gpg" | head -1)
        if [[ -n "$postgres_files" && -s "$postgres_files" ]]; then
            log_success "PostgreSQL backup file exists and is not empty"
        else
            log_error "PostgreSQL backup file is missing or empty"
            verification_passed=false
        fi
    fi

    if [[ -d "$BACKUP_PATH/redis" ]]; then
        redis_files=$(find "$BACKUP_PATH/redis" -name "*.rdb*" -o -name "*.gpg" | head -1)
        if [[ -n "$redis_files" && -s "$redis_files" ]]; then
            log_success "Redis backup file exists and is not empty"
        else
            log_error "Redis backup file is missing or empty"
            verification_passed=false
        fi
    fi

    if [[ "$verification_passed" == true ]]; then
        log_success "Backup verification passed"
        return 0
    else
        log_error "Backup verification failed"
        return 1
    fi
}

# Main backup function
main() {
    log_info "Starting AgentLab backup process..."
    echo "Backup directory: $BACKUP_DIR"
    echo "Retention: $RETENTION_DAYS days"
    echo "Compression: $COMPRESSION"
    echo "Encryption: $ENCRYPTION"
    echo ""

    check_dependencies
    create_backup_directory

    local backup_success=true

    # Perform backups
    backup_postgres || backup_success=false
    backup_redis || backup_success=false
    backup_logs || true  # Don't fail overall backup for log issues

    create_backup_manifest
    verify_backup || backup_success=false
    cleanup_old_backups

    if [[ "$backup_success" == true ]]; then
        log_success "Backup process completed successfully"
        log_info "Backup location: $BACKUP_PATH"
        exit 0
    else
        log_error "Backup process completed with errors"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
AgentLab Backup Script

Usage: $0 [OPTIONS]

Options:
    -h, --help                    Show this help message
    -d, --dir DIRECTORY          Backup directory (default: $BACKUP_DIR)
    -f, --file FILE              Docker Compose file (default: $COMPOSE_FILE)
    -r, --retention DAYS         Backup retention in days (default: $RETENTION_DAYS)
    -c, --compress               Enable compression (default: $COMPRESSION)
    -e, --encrypt KEY            Enable encryption with key
    --no-compress                Disable compression
    --postgres-only              Backup only PostgreSQL
    --redis-only                 Backup only Redis

Examples:
    $0                           # Full backup with defaults
    $0 -d /backups -r 7          # Custom directory and 7-day retention
    $0 --postgres-only           # PostgreSQL backup only
    $0 -e "my-secret-key"        # Encrypted backup

EOF
}

# Parse command line arguments
POSTGRES_ONLY=false
REDIS_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESSION=true
            shift
            ;;
        --no-compress)
            COMPRESSION=false
            shift
            ;;
        -e|--encrypt)
            ENCRYPTION=true
            ENCRYPTION_KEY="$2"
            shift 2
            ;;
        --postgres-only)
            POSTGRES_ONLY=true
            shift
            ;;
        --redis-only)
            REDIS_ONLY=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Adjust backup functions based on options
if [[ "$POSTGRES_ONLY" == true ]]; then
    backup_redis() { return 0; }
elif [[ "$REDIS_ONLY" == true ]]; then
    backup_postgres() { return 0; }
fi

# Run main function
main "$@"