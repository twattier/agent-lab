# Deployment Architecture

## Deployment Strategy

AgentLab follows a **local-first deployment** approach with Docker containerization, enabling consistent environments from development to production while maintaining simplicity and portability.

### Deployment Targets
1. **Local Development:** Docker Compose on developer desktop
2. **Staging Environment:** Docker Compose on staging server
3. **Production:** Docker Compose with production configurations
4. **Cloud Deployment:** Optional deployment to AWS, DigitalOcean, or other cloud providers

### Container Strategy
- **Frontend Container:** Next.js application with nginx for static serving
- **Backend Container:** FastAPI application with uvicorn server
- **Database Container:** PostgreSQL with pgvector extension
- **Cache Container:** Redis for session storage and caching
- **Reverse Proxy:** nginx for load balancing and SSL termination

## Docker Configuration

### Development docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: apps/web/Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - api

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./apps/api:/app
    environment:
      - DATABASE_URL=postgresql://agentlab:password@postgres:5432/agentlab
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=dev-secret-key
    depends_on:
      - postgres
      - redis

  postgres:
    image: pgvector/pgvector:pg17
    environment:
      - POSTGRES_DB=agentlab
      - POSTGRES_USER=agentlab
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Production docker-compose.yml
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/ssl:/etc/nginx/ssl
    depends_on:
      - web
      - api

  web:
    build:
      context: .
      dockerfile: apps/web/Dockerfile.prod
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.agentlab.example.com/api/v1
    depends_on:
      - api

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

  postgres:
    image: pgvector/pgvector:pg17
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          npm install
          cd apps/api && pip install -r requirements.txt

      - name: Run frontend tests
        run: npm run test:web

      - name: Run backend tests
        run: npm run test:api

      - name: Run E2E tests
        run: npm run test:e2e

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker images
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/web:${{ github.sha }} -f apps/web/Dockerfile.prod .
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ github.sha }} -f apps/api/Dockerfile.prod .
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/web:${{ github.sha }}
          docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/api:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          # SSH to staging server and update containers
          ssh ${{ secrets.STAGING_HOST }} "
            cd /opt/agentlab &&
            docker-compose pull &&
            docker-compose up -d
          "

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # SSH to production server and update containers
          ssh ${{ secrets.PRODUCTION_HOST }} "
            cd /opt/agentlab &&
            docker-compose pull &&
            docker-compose up -d --no-deps web api
          "
```

## Environment Management

### Environment Variables
```bash
# Production .env
DATABASE_URL=postgresql://user:password@postgres:5432/agentlab_prod
REDIS_URL=redis://redis:6379
JWT_SECRET=production-secret-key-change-this
OPENAI_API_KEY=sk-...
CLAUDE_CODE_MCP_URL=ws://claude-code:3001/mcp
LOG_LEVEL=info
ENVIRONMENT=production
```

### SSL/TLS Configuration
```nginx
# infrastructure/nginx/nginx.conf
server {
    listen 443 ssl;
    server_name agentlab.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://web:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### Database Backup Strategy
```bash
#!/bin/bash
# scripts/backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# Create database backup
docker exec postgres pg_dump -U agentlab agentlab > "$BACKUP_DIR/db_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/db_backup_$DATE.sql"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery Plan
1. **Data Recovery:** Restore from latest backup
2. **Service Recovery:** Redeploy containers from registry
3. **Configuration Recovery:** Restore from version control
4. **Communication:** Automated status page updates

---
[← Back to Development Workflow](development-workflow.md) | [Architecture Index](index.md) | [Next: Error Handling Strategy →](error-handling-strategy.md)