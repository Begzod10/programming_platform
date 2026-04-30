from pydantic_settings import BaseSettings
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:123@localhost:5432/Student_Platform"
    APP_NAME: str = "Student Programming Platform"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = ".py,.js,.html,.css,.json,.md,.txt,.zip"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    APP_VERSION: str = "1.0.0"
    GROQ_API_KEY: str = ""
    GENNIS_API_URL: str = "https://tech.gennis.uz/api"
    GROK_API_URL: str = "https://api.x.ai/v1/chat/completions" # Based on grok_service.py
    GROK_API_KEY: str = ""
    GROK_MODEL: str = "grok-beta"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
