# Multi-stage Dockerfile for AgentLab FastAPI backend
# Based on Python 3.11.5-slim with security and performance optimizations

# Build stage
FROM python:3.11.5-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy dependency files
COPY apps/api/requirements.txt .
COPY apps/api/requirements-dev.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM python:3.11.5-slim as development

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r agentlab && useradd -r -g agentlab -u 1000 agentlab

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy application code
COPY apps/api/ ./api/
COPY packages/ ./packages/

# Create logs directory
RUN mkdir -p logs && chown -R agentlab:agentlab logs

# Development dependencies
COPY apps/api/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set permissions
RUN chown -R agentlab:agentlab /app

# Switch to non-root user
USER agentlab

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command with hot reload
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]

# Production stage
FROM python:3.11.5-slim as production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r agentlab && useradd -r -g agentlab -u 1000 agentlab

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy application code
COPY apps/api/ ./api/
COPY packages/ ./packages/

# Create logs directory
RUN mkdir -p logs && chown -R agentlab:agentlab logs

# Set permissions
RUN chown -R agentlab:agentlab /app

# Switch to non-root user
USER agentlab

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["gunicorn", "api.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--keepalive", "2", "--max-requests", "1000", "--max-requests-jitter", "100"]