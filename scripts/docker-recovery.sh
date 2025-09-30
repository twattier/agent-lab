#!/bin/bash
# Docker Environment Recovery Script
#
# This script resets the Docker environment when services are not
# functioning correctly.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Docker Environment Recovery${NC}"
echo "This will stop and remove all containers, volumes, and networks."
read -p "Are you sure you want to continue? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Recovery cancelled."
    exit 0
fi

echo -e "${YELLOW}Stopping all containers...${NC}"
docker-compose down || true

echo -e "${YELLOW}Removing volumes...${NC}"
docker volume rm agentlab_postgres_data agentlab_redis_data 2>/dev/null || true

echo -e "${YELLOW}Pruning Docker system...${NC}"
docker system prune -f

echo -e "${YELLOW}Starting fresh containers...${NC}"
docker-compose up -d

echo -e "${GREEN}✓ Docker environment recovered${NC}"
echo "Run 'docker-compose ps' to check service status."
