"""
AGNAYA V3.1 - Centralized Configuration & Environment Settings
Loaded via pydantic-settings v2 (BaseSettings with SettingsConfigDict).
SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Bindings
    API_HOST: str = Field(default="127.0.0.1", description="Default host IP for FastAPI service")
    API_PORT: int = Field(default=8000, description="Port for FastAPI REST service")
    STREAMLIT_PORT: int = Field(default=8501, description="Port for Streamlit operations dashboard")

    # Optional Security Key for REST endpoints (None = open for local evaluation)
    API_KEY: Optional[str] = Field(default=None, description="Optional security token required via X-API-Key header")

    # CARTO Basemap Key (Optional: system automatically falls back to keyless Positron / OSM tiles if empty)
    CARTO_API_KEY: str = Field(default="", description="Optional CARTO basemap access token")

    # Allowed CORS Origins (Never wildcard with credentials)
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        description="Explicit allowed CORS origins"
    )

    # Rate Limiting (Requests per minute per client IP, 0 to disable)
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, description="Maximum requests per minute per IP")


settings = Settings()
