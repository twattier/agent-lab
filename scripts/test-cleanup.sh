#!/bin/bash
# Test Environment Cleanup Script
#
# This script cleans up test artifacts and resets the test environment.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Test Environment Cleanup${NC}"

# Clean Python test artifacts
echo "Cleaning Python test artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clean Node test artifacts
echo "Cleaning Node test artifacts..."
find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
find apps/web -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true

# Clean coverage reports
echo "Cleaning coverage reports..."
rm -rf apps/api/htmlcov apps/api/.coverage apps/api/coverage.xml 2>/dev/null || true
rm -rf apps/web/coverage 2>/dev/null || true

# Clean Playwright artifacts
echo "Cleaning Playwright artifacts..."
rm -rf test-results playwright-report 2>/dev/null || true

# Clean test databases
echo "Stopping test containers..."
docker-compose -f docker-compose.test.yml down 2>/dev/null || true

echo -e "${GREEN}✓ Test environment cleaned${NC}"
