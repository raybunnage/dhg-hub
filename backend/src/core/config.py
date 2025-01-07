from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    SUPABASE_URL: str
    SUPABASE_KEY: str
    DATABASE_URL: str
    API_VERSION: str = "v1"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
