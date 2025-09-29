# Monitoring and Observability

## Monitoring Stack

AgentLab implements comprehensive monitoring and observability to ensure system health, performance tracking, and rapid issue resolution.

### Core Monitoring Components
- **Application Metrics:** Custom business metrics and system performance indicators
- **Error Tracking:** Comprehensive error capture with context and stack traces
- **Performance Monitoring:** API response times, database query performance, and user experience metrics
- **Health Checks:** System component health monitoring with automated alerts
- **Log Aggregation:** Structured logging with search and analysis capabilities

## Key Metrics

### Business Metrics
- **Project Creation Rate:** New projects created per day/week
- **Workflow Progression:** Average time in each BMAD stage
- **Gate Approval Rate:** Percentage of gates approved vs rejected
- **User Engagement:** Active users, session duration, feature usage
- **Claude Code Sync Success:** File synchronization success rate and timing

### Technical Metrics
- **API Performance:** Response times, throughput, error rates
- **Database Performance:** Query execution times, connection pool usage
- **Memory Usage:** Application memory consumption and garbage collection
- **CPU Utilization:** System load and processing efficiency
- **Network I/O:** Request/response sizes and bandwidth usage

### User Experience Metrics
- **Page Load Times:** Initial load and navigation performance
- **Error Rates:** Client-side errors and their impact on users
- **Feature Adoption:** Usage patterns for new and existing features
- **Conversion Funnels:** Project creation to completion rates
- **User Satisfaction:** Performance impact on user workflows

## Monitoring Implementation

### Application Health Checks
```python
# health_checks.py
from fastapi import APIRouter
from sqlalchemy import text
from core.database import get_db_session
from core.redis import get_redis_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive system health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Database connectivity
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Redis connectivity
    try:
        redis = get_redis_client()
        await redis.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Claude Code MCP connection
    try:
        mcp_status = await check_mcp_connection()
        health_status["checks"]["claude_code"] = "healthy" if mcp_status else "disconnected"
    except Exception as e:
        health_status["checks"]["claude_code"] = f"error: {str(e)}"

    return health_status

@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus-compatible metrics endpoint."""
    metrics = [
        "# HELP agentlab_projects_total Total number of projects",
        "# TYPE agentlab_projects_total counter",
        f"agentlab_projects_total {await get_project_count()}",
        "",
        "# HELP agentlab_api_requests_total Total number of API requests",
        "# TYPE agentlab_api_requests_total counter",
        f"agentlab_api_requests_total {await get_request_count()}",
        "",
        "# HELP agentlab_workflow_stage_duration_seconds Time spent in workflow stages",
        "# TYPE agentlab_workflow_stage_duration_seconds histogram",
        # Add histogram data
    ]

    return "\n".join(metrics)
```

### Structured Logging
```python
# logging_config.py
import structlog
import logging
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME,
                       structlog.processors.CallsiteParameter.FUNC_NAME,
                       structlog.processors.CallsiteParameter.LINENO]
        ),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

# Usage in services
logger = structlog.get_logger()

async def create_project(request: CreateProjectRequest) -> Project:
    logger.info(
        "Creating new project",
        project_name=request.name,
        service_id=request.service_id,
        user_id=request.user_id
    )

    try:
        project = await project_repository.create(request)

        logger.info(
            "Project created successfully",
            project_id=project.id,
            project_name=project.name,
            duration_ms=execution_time
        )

        return project
    except Exception as e:
        logger.error(
            "Project creation failed",
            project_name=request.name,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

### Performance Monitoring
```typescript
// Frontend performance monitoring
export function usePerformanceMonitoring() {
  useEffect(() => {
    // Track page load performance
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
          trackMetric('page_load_time', entry.loadEventEnd - entry.loadEventStart);
        }

        if (entry.entryType === 'largest-contentful-paint') {
          trackMetric('largest_contentful_paint', entry.startTime);
        }
      }
    });

    observer.observe({ entryTypes: ['navigation', 'largest-contentful-paint'] });

    return () => observer.disconnect();
  }, []);
}

// Track user interactions
export function trackUserAction(action: string, properties?: Record<string, any>) {
  const event = {
    action,
    timestamp: new Date().toISOString(),
    page: window.location.pathname,
    userAgent: navigator.userAgent,
    ...properties
  };

  // Send to analytics service
  analytics.track(event);
}
```

### Alert Configuration
```yaml
# alerts.yml - Monitoring alerts configuration
alerts:
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    duration: "5m"
    severity: "critical"
    channels: ["slack", "email"]

  - name: "Slow API Response"
    condition: "api_response_time_p95 > 1000ms"
    duration: "10m"
    severity: "warning"
    channels: ["slack"]

  - name: "Database Connection Issues"
    condition: "database_connections_available < 5"
    duration: "2m"
    severity: "critical"
    channels: ["slack", "email", "pagerduty"]

  - name: "Claude Code Sync Failures"
    condition: "mcp_sync_failure_rate > 10%"
    duration: "15m"
    severity: "warning"
    channels: ["slack"]
```

## Operational Dashboards

### System Health Dashboard
- **Service Status:** Real-time health of all system components
- **Performance Trends:** API response times and throughput over time
- **Error Rates:** Application and infrastructure error tracking
- **Resource Usage:** CPU, memory, and storage utilization

### Business Intelligence Dashboard
- **Project Analytics:** Creation rates, workflow progression, and completion times
- **User Engagement:** Active users, feature usage, and session analytics
- **Workflow Efficiency:** BMAD stage bottlenecks and optimization opportunities
- **Claude Code Integration:** Sync success rates and performance metrics

### Development Metrics Dashboard
- **Code Quality:** Test coverage, lint warnings, and technical debt
- **Deployment Frequency:** Release cadence and deployment success rates
- **Lead Time:** Time from commit to production deployment
- **Mean Time to Recovery:** Incident response and resolution times

---
[← Back to Security and Performance](security-and-performance.md) | [Architecture Index](index.md)