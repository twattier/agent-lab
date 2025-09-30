"""
Configuration settings for AgentLab API.
"""
import secrets
from functools import lru_cache
from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://agentlab:agentlab@localhost:5432/agentlab"
    DATABASE_ECHO: bool = False

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # MCP settings
    MCP_ENABLED: bool = True
    MCP_HOST: str = "localhost"
    MCP_PORT: int = 3001

    # Security settings
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()