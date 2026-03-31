from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReplyMind Context API"
    VERSION: str = "1.2.0"
    
    # Supabase Secrets
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # LLM Auth (OPENAI_API_KEY supported as a common alias on hosts like Render)
    OPENAI_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Redis for Celery Worker
    REDIS_URL: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=True)

settings = Settings()
