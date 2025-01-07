from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase settings
    supabase_url: str
    supabase_key: str
    supabase_db_password: str
    supabase_domain_id: str
    vite_supabase_url: str
    vite_supabase_anon_key: str

    # API Keys
    anthropic_api_key: str
    openai_api_key: str

    # Google settings
    google_credentials_file: str
    client_id: str
    client_email: str
    private_key_id: str
    private_key: str

    # Test credentials
    test_email: str
    test_password: str

    # Optional settings
    debug: bool = False
    api_version: str = "v1"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
