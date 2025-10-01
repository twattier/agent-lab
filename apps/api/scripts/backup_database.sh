#!/bin/bash
#
# Database backup script for AgentLab
#
# Usage: ./scripts/backup_database.sh [output_dir]
#

set -e

# Configuration
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5434}"
DB_NAME="${POSTGRES_DB:-agentlab}"
DB_USER="${POSTGRES_USER:-agentlab}"
DB_PASSWORD="${POSTGRES_PASSWORD:-agentlab}"
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/agentlab_backup_${TIMESTAMP}.dump"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "🗄️  AgentLab Database Backup"
echo "================================"
echo "Database: ${DB_NAME}"
echo "Host: ${DB_HOST}:${DB_PORT}"
echo "Output: ${BACKUP_FILE}"
echo ""

# Export password for pg_dump
export PGPASSWORD="${DB_PASSWORD}"

# Create backup using pg_dump (custom format)
echo "Creating backup..."
docker exec agentlab-postgres pg_dump \
    -h localhost \
    -p 5432 \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -Fc \
    -f "/tmp/backup.dump"

# Copy from container to host
docker cp agentlab-postgres:/tmp/backup.dump "${BACKUP_FILE}"

# Clean up temp file in container
docker exec agentlab-postgres rm /tmp/backup.dump

# Get file size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)

echo "✅ Backup complete!"
echo "   File: ${BACKUP_FILE}"
echo "   Size: ${BACKUP_SIZE}"
echo ""

# Optional: Compress the backup
if command -v gzip &> /dev/null; then
    echo "Compressing backup..."
    gzip "${BACKUP_FILE}"
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    COMPRESSED_SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
    echo "✅ Compressed: ${COMPRESSED_FILE}"
    echo "   Size: ${COMPRESSED_SIZE}"
    echo ""
fi

# Optional: Delete backups older than 30 days
if [ "${BACKUP_RETENTION_DAYS:-0}" -gt 0 ]; then
    echo "Cleaning up old backups (older than ${BACKUP_RETENTION_DAYS} days)..."
    find "${BACKUP_DIR}" -name "agentlab_backup_*.dump*" -mtime +${BACKUP_RETENTION_DAYS} -delete
    echo "✅ Cleanup complete"
    echo ""
fi

echo "Backup process finished successfully!"
