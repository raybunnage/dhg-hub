from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Supabase settings (for backend)
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
