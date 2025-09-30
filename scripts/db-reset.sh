#!/bin/bash
# Database Reset Script
#
# This script resets the database and runs migrations.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DB_URL=${DATABASE_URL:-"postgresql+asyncpg://agentlab:agentlab@localhost:5434/agentlab"}

echo -e "${YELLOW}Database Reset${NC}"
echo "This will drop all tables and re-run migrations."
read -p "Are you sure? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Reset cancelled."
    exit 0
fi

cd apps/api

echo -e "${YELLOW}Downgrading database...${NC}"
alembic downgrade base || echo "No migrations to downgrade"

echo -e "${YELLOW}Upgrading database...${NC}"
alembic upgrade head

echo -e "${GREEN}✓ Database reset complete${NC}"

cd ../..
