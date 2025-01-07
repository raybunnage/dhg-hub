from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the application."""

    PROJECT_NAME: str = 'Your Project Name'
    API_V1_STR: str = '/api/v1'
    SUPABASE_KEY: str = ''

    class Config:
        """Pydantic configuration class."""

        env_file = '.env'


settings = Settings()
