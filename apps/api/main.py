"""
FastAPI application entry point for AgentLab API.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown - cleanup if needed


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="AgentLab API",
        description="Backend API for BMAD workflow automation and Claude Code integration",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    from api.v1 import health, clients, services, projects, contacts, service_categories, implementation_types, workflows

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(clients.router, prefix="/api/v1", tags=["clients"])
    app.include_router(services.router, prefix="/api/v1", tags=["services"])
    app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
    app.include_router(contacts.router, prefix="/api/v1", tags=["contacts"])
    app.include_router(service_categories.router, prefix="/api/v1", tags=["service-categories"])
    app.include_router(implementation_types.router, prefix="/api/v1", tags=["implementation-types"])
    app.include_router(workflows.router, prefix="/api/v1", tags=["workflows"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )