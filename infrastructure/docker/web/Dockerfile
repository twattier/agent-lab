# Multi-stage Dockerfile for AgentLab Next.js frontend
# Based on Node.js 18.17.0-alpine with security and performance optimizations

# Dependencies stage
FROM node:18.17.0-alpine AS deps

# Install system dependencies
RUN apk add --no-cache libc6-compat curl

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY packages/types/package*.json ./packages/types/
COPY packages/ui/package*.json ./packages/ui/
COPY packages/utils/package*.json ./packages/utils/
COPY apps/web/package*.json ./apps/web/

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Build stage
FROM node:18.17.0-alpine AS builder

# Install system dependencies
RUN apk add --no-cache libc6-compat curl

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages/types/node_modules ./packages/types/node_modules
COPY --from=deps /app/packages/ui/node_modules ./packages/ui/node_modules
COPY --from=deps /app/packages/utils/node_modules ./packages/utils/node_modules

# Copy source code
COPY . .

# Install all dependencies including dev dependencies for build
RUN npm ci

# Build packages
RUN npm run build --workspaces

# Build Next.js application
RUN cd apps/web && npm run build

# Development stage
FROM node:18.17.0-alpine AS development

# Install system dependencies
RUN apk add --no-cache libc6-compat curl

# Create non-root user
RUN addgroup -g 1000 -S agentlab && adduser -S agentlab -u 1000 -G agentlab

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY packages/types/package*.json ./packages/types/
COPY packages/ui/package*.json ./packages/ui/
COPY packages/utils/package*.json ./packages/utils/
COPY apps/web/package*.json ./apps/web/

# Install all dependencies for development
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Build packages in development mode
RUN npm run build --workspaces

# Set permissions
RUN chown -R agentlab:agentlab /app

# Switch to non-root user
USER agentlab

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Development command with hot reload
CMD ["npm", "run", "dev", "--workspace=apps/web"]

# Production stage
FROM node:18.17.0-alpine AS production

# Install system dependencies
RUN apk add --no-cache libc6-compat curl

# Create non-root user
RUN addgroup -g 1000 -S agentlab && adduser -S agentlab -u 1000 -G agentlab

WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public

# Set permissions
RUN chown -R agentlab:agentlab /app

# Switch to non-root user
USER agentlab

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Production command
CMD ["node", "apps/web/server.js"]