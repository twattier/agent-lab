# Epic 2: Canonical Version Reference Sheet

**Purpose:** Quick reference for authoritative version specifications for Epic 2 development.

**Status:** ✅ ACTIVE - Quick reference (architecture docs now aligned)
**Created:** 2025-09-30
**Story 1.7 Status:** ✅ COMPLETE (2025-09-30 - Quality Score: 100/100)
**Architecture Docs:** All aligned and validated

---

## ✅ Architecture Documentation Status

**Update (2025-09-30):** Story 1.7 (Architecture Documentation Alignment) has been completed with QA approval. All architecture documents now reference correct canonical versions.

**Current Status:**

- ✅ All PostgreSQL references updated to 15.4/pg15
- ✅ All pgvector references updated to 0.5.0
- ✅ All Python references standardized to 3.11.5
- ✅ FastAPI version verified as 0.115+ (actual deployed version)
- ✅ TypeScript version aligned to 5.1.6

**Developer Instruction:** Architecture documents are now reliable. This reference sheet remains available as a quick lookup guide for canonical versions.

---

## 🎯 Canonical Versions for Epic 2

### Database & Infrastructure

| Component        | Canonical Version        | Architecture Doc Reference | Status  |
| ---------------- | ------------------------ | -------------------------- | ------- |
| **PostgreSQL**   | `15.4`                   | ✅ Aligned (Story 1.7)     | Correct |
| **pgvector**     | `0.5.0`                  | ✅ Aligned (Story 1.7)     | Correct |
| **Docker Image** | `pgvector/pgvector:pg15` | ✅ Aligned (Story 1.7)     | Correct |
| **Redis**        | `7.0-alpine`             | ✅ Aligned                 | Correct |

### Backend Stack

| Component      | Canonical Version | Architecture Doc Reference | Status  |
| -------------- | ----------------- | -------------------------- | ------- |
| **Python**     | `3.11.5`          | ✅ Aligned (Story 1.7)     | Correct |
| **FastAPI**    | `0.115+`          | ✅ Aligned (Story 1.7)     | Correct |
| **Pydantic**   | `2.0+`            | ✅ Aligned                 | Correct |
| **SQLAlchemy** | `2.0+` (async)    | ✅ Aligned                 | Correct |
| **Alembic**    | `1.11+`           | ✅ Aligned                 | Correct |
| **asyncpg**    | `0.28+`           | ✅ Aligned                 | Correct |

### Frontend Stack (if UI added)

| Component        | Canonical Version | Architecture Doc Reference | Status  |
| ---------------- | ----------------- | -------------------------- | ------- |
| **Node.js**      | `18.17.0`         | ✅ Aligned                 | Correct |
| **Next.js**      | `13.4.19+`        | ✅ Aligned                 | Correct |
| **TypeScript**   | `5.1.6`           | ✅ Aligned (Story 1.7)     | Correct |
| **React**        | `18.2.0+`         | ✅ Aligned                 | Correct |
| **Tailwind CSS** | `3.3.0+`          | ✅ Aligned                 | Correct |

---

## 📋 Epic 2 Story-Specific Guidance

### Story 2.1: Client & Service Hierarchy Management

**Database Connection:**

```python
# Use these exact versions in requirements.txt
asyncpg==0.28.0
SQLAlchemy==2.0.23
alembic==1.12.1
```

**Alembic Migration:**

```python
# Alembic env.py - Use asyncpg driver
from sqlalchemy.ext.asyncio import create_async_engine

# Connection string format
DATABASE_URL = "postgresql+asyncpg://agentlab:agentlab@localhost:5434/agentlab"
```

**Docker Reference:**

```yaml
# docker-compose.yml - PostgreSQL service
services:
  postgres:
    image: pgvector/pgvector:pg15 # ← USE pg15, NOT pg17
    environment:
      POSTGRES_VERSION: '15.4'
      PGVECTOR_VERSION: '0.5.0'
```

### Story 2.2: Project Data Models & Lifecycle

**SQLAlchemy Models:**

```python
from sqlalchemy import String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Use Python 3.11.5 type hints
class Base(AsyncAttrs, DeclarativeBase):
    pass
```

### Story 2.3: BMAD Workflow State Management

**JSONB Workflow State:**

```python
# PostgreSQL 15.4 JSONB support
workflow_state: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
```

### Story 2.4: Document Metadata Management

**pgvector Integration:**

```python
from pgvector.sqlalchemy import Vector

# pgvector 0.5.0 syntax
content_vector: Mapped[list] = mapped_column(Vector(1536), nullable=True)

# Index creation (pgvector 0.5.0)
# CREATE INDEX idx_document_vector ON document
# USING ivfflat (content_vector vector_cosine_ops);
```

**Note:** pgvector 0.5.0 uses `ivfflat` index. Version 0.8+ introduced `hnsw` - DO NOT use hnsw syntax.

### Story 2.5: Data Validation & Seed Data

**Pydantic Models:**

```python
from pydantic import BaseModel, Field, EmailStr
from pydantic import ConfigDict  # Pydantic 2.0+ syntax

class ClientCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic 2.0+

    name: str = Field(..., min_length=1, max_length=255)
    business_domain: str
```

---

## 🔧 Development Environment Validation

**Before starting Epic 2 development, verify your environment:**

```bash
# Check Python version
python --version
# Expected: Python 3.11.5

# Check PostgreSQL version
docker exec -it agentlab-postgres-1 psql -U agentlab -c "SELECT version();"
# Expected: PostgreSQL 15.4

# Check pgvector extension
docker exec -it agentlab-postgres-1 psql -U agentlab -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
# Expected: vector | 0.5.0

# Check Node.js version (if frontend work)
node --version
# Expected: v18.17.0
```

---

## 📚 Architecture Document Status

**All Architecture Documents Updated (Story 1.7 Complete - 2025-09-30):**

✅ **[docs/architecture/deployment-architecture.md](./architecture/deployment-architecture.md)**

- PostgreSQL references corrected to pg15 ✅
- Python version standardized to 3.11.5 ✅
- IaC implementation documented ✅

✅ **[docs/architecture/tech-stack.md](./architecture/tech-stack.md)**

- pgvector version corrected to 0.5.0 ✅
- FastAPI version verified as 0.115+ ✅
- TypeScript version aligned to 5.1.6 ✅

✅ **[docs/architecture/testing-strategy.md](./architecture/testing-strategy.md)**

- Mock services documented with file locations ✅
- Test metrics updated (49 tests, <2 seconds) ✅

✅ **[docs/architecture/development-workflow.md](./architecture/development-workflow.md)**

- Python version standardized to 3.11.5 ✅

**All Documents Validated:**

✅ [docs/epics/epic-1-foundation-infrastructure.md](./epics/epic-1-foundation-infrastructure.md) - Authoritative source
✅ [docs/architecture/database-schema.md](./architecture/database-schema.md) - Accurate and complete
✅ [docs/architecture/data-models.md](./architecture/data-models.md) - Models correct

---

## 🎯 Quick Reference Card

**Copy this to your development notes:**

```
EPIC 2 CANONICAL VERSIONS (Architecture docs now aligned ✅)
==================================================================
PostgreSQL:      15.4
pgvector:        0.5.0
Docker Image:    pgvector/pgvector:pg15
Python:          3.11.5
FastAPI:         0.115+
SQLAlchemy:      2.0+ (async)
Alembic:         1.11+
asyncpg:         0.28+

Node.js:         18.17.0
Next.js:         13.4.19+
TypeScript:      5.1.6
React:           18.2.0+
```

---

## 🔄 Document Status

**Story 1.7 Completion:** ✅ COMPLETE (2025-09-30)

- All architecture documents updated with canonical versions
- Version consistency validated across all docs (grep validation passed)
- Quality Score: 100/100

**Document Purpose:** This remains as a quick reference guide for Epic 2 developers. All architecture documents are now aligned and reliable.

---

**Questions or Conflicts?**

- Architecture docs are now reliable - refer to [architecture documentation](./architecture/index.md)
- Review Story 1.7 completion: [story-1.7-architecture-documentation-alignment.md](./stories/story-1.7-architecture-documentation-alignment.md)
- Consult [Epic 1](./epics/epic-1-foundation-infrastructure.md) for canonical version sources
- Escalate to Product Owner (Sarah) or Tech Lead if needed

**Last Updated:** 2025-09-30 (Story 1.7 completion)
**Created By:** Sarah (Product Owner)
**Review Status:** ✅ PO Approved for Epic 2 Development
