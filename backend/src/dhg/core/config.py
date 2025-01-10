import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    TESTING = False
    DEBUG = False
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    ENV = "development"


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    ENV = "testing"
    # Use test-specific Supabase credentials
    SUPABASE_URL = "https://example.supabase.co"
    SUPABASE_KEY = "test-key"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    ENV = "production"


@lru_cache()
def get_settings():
    """Get cached settings based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    configs = {
        "development": DevelopmentConfig,
        "testing": TestConfig,
        "production": ProductionConfig,
        "default": DevelopmentConfig,
    }
    return configs[env]()


# For Flask app configuration
config = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
