#!/bin/bash
#
# Database restore script for AgentLab
#
# Usage: ./scripts/restore_database.sh <backup_file>
#

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "❌ Error: Backup file not specified"
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Example: $0 ./backups/agentlab_backup_20251001_120000.dump"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    # Check if it's a gzipped file
    if [ -f "${BACKUP_FILE}.gz" ]; then
        echo "Found compressed backup, decompressing..."
        gunzip -k "${BACKUP_FILE}.gz"
    else
        echo "❌ Error: Backup file not found: ${BACKUP_FILE}"
        exit 1
    fi
fi

# Configuration
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5434}"
DB_NAME="${POSTGRES_DB:-agentlab}"
DB_USER="${POSTGRES_USER:-agentlab}"
DB_PASSWORD="${POSTGRES_PASSWORD:-agentlab}"

echo "⚠️  AgentLab Database Restore"
echo "================================"
echo "Database: ${DB_NAME}"
echo "Host: ${DB_HOST}:${DB_PORT}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
echo "⚠️  WARNING: This will DROP the existing database!"
echo "Press Ctrl+C within 5 seconds to cancel..."
sleep 5

# Export password for psql/pg_restore
export PGPASSWORD="${DB_PASSWORD}"

# Copy backup file to container
echo "Copying backup to container..."
docker cp "${BACKUP_FILE}" agentlab-postgres:/tmp/restore.dump

# Drop existing database
echo "Dropping existing database..."
docker exec agentlab-postgres psql -U postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"

# Create fresh database
echo "Creating fresh database..."
docker exec agentlab-postgres psql -U postgres -c "CREATE DATABASE ${DB_NAME};"
docker exec agentlab-postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

# Restore from backup
echo "Restoring from backup..."
docker exec agentlab-postgres pg_restore \
    -h localhost \
    -p 5432 \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -v \
    /tmp/restore.dump

# Clean up temp file in container
docker exec agentlab-postgres rm /tmp/restore.dump

echo ""
echo "✅ Database restore complete!"
echo ""
echo "Verifying restore..."

# Verify by checking table count
TABLE_COUNT=$(docker exec agentlab-postgres psql -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "Tables restored: ${TABLE_COUNT}"

# Check alembic version
ALEMBIC_VERSION=$(docker exec agentlab-postgres psql -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT version_num FROM alembic_version;" 2>/dev/null || echo "N/A")
echo "Alembic version: ${ALEMBIC_VERSION}"

echo ""
echo "Restore process finished successfully!"
