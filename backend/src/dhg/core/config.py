from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    API_VERSION: str = "v1"  # Added API version setting

    # Supabase settings
    SUPABASE_URL: str = "http://localhost:8000"  # default for testing
    SUPABASE_KEY: str = "dummy-key"  # default for testing

    # Flask settings
    FLASK_ENV: str = "development"
    DEBUG: bool = True
    TESTING: bool = False
    SECRET_KEY: Optional[str] = None

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="allow")


# Create a global settings instance
settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return settings
