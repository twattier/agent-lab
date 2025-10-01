# AgentLab Seed Data Scripts

This directory contains scripts for seeding the AgentLab database with sample data.

## Available Scripts

### `seed_dev_data.py`

Populates the database with realistic development data for testing and development purposes.

**What it seeds:**

- 5 sample clients across different business domains (healthcare, finance, technology, manufacturing, education)
- 10 sample contacts with realistic names and emails
- 15-16 sample services with descriptions
- 24+ sample projects with various statuses and workflow states
- Service-contact and project-contact relationships
- Service categories and project user categories
- Workflow events for project history

**Usage:**

```bash
# Seed data (will fail if data already exists)
cd apps/api
export DATABASE_URL="postgresql://agentlab:agentlab@localhost:5434/agentlab"
python3 scripts/seed_dev_data.py

# Reset and reseed (clears all existing data)
python3 scripts/seed_dev_data.py --reset
```

**Requirements:**

- `faker` library must be installed: `pip install faker`
- Database must be migrated to latest version: `alembic upgrade head`
- Reference data (implementation types and service categories) must exist

## Database Reset Procedure

To completely reset your database and start fresh:

```bash
cd apps/api
export DATABASE_URL="postgresql://agentlab:agentlab@localhost:5434/agentlab"

# 1. Drop and recreate database (using docker)
docker exec agentlab-postgres psql -U agentlab -c "DROP DATABASE agentlab;"
docker exec agentlab-postgres psql -U agentlab -c "CREATE DATABASE agentlab;"

# 2. Run migrations
python3 -m alembic upgrade head

# 3. Seed development data
python3 scripts/seed_dev_data.py
```

## Reference Data

Reference data (implementation types and service categories) is seeded via Alembic migrations:

- Migration: `090f812c94b9_seed_reference_data.py`
- Implementation Types: RAG, AGENTIC, AUTOMATON, CHATBOT, ANALYTICS, RECOMMENDATION
- Service Categories: SALES, HR, FINANCE, OPERATIONS, CUSTOMER_SERVICE, IT, LEGAL, PRODUCT, EXECUTIVE

This data is automatically loaded when you run `alembic upgrade head`.

## Verification

To verify data was seeded correctly:

```bash
# Check client count
docker exec agentlab-postgres psql -U agentlab -d agentlab -c "SELECT COUNT(*) FROM clients;"

# Check service count
docker exec agentlab-postgres psql -U agentlab -d agentlab -c "SELECT COUNT(*) FROM services;"

# Check project count
docker exec agentlab-postgres psql -U agentlab -d agentlab -c "SELECT COUNT(*) FROM projects;"

# View sample data
docker exec agentlab-postgres psql -U agentlab -d agentlab -c "SELECT name, business_domain FROM clients;"
```

## Troubleshooting

### "No module named 'models'" Error

Make sure you're running the script from the `apps/api` directory:

```bash
cd apps/api
python3 scripts/seed_dev_data.py
```

### "faker library not installed" Error

Install the faker library:

```bash
pip install faker
```

### "The asyncio extension requires an async driver" Error

This should be handled automatically by the script. If you see this error, ensure your DATABASE_URL is in the correct format:

```
postgresql://agentlab:agentlab@localhost:5434/agentlab
```

The script will automatically convert it to `postgresql+asyncpg://...`

### "Reference data not found" Error

Run migrations first:

```bash
python3 -m alembic upgrade head
```

This will seed the reference data (implementation types and service categories).
