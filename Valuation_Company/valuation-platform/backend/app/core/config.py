from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Application
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here-change-in-production"

    # AI Strategy - 50:25:25 (Investment Tracker)
    CLAUDE_USAGE_RATIO: float = 0.50
    OPENAI_USAGE_RATIO: float = 0.25
    GEMINI_USAGE_RATIO: float = 0.25

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
