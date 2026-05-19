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
    GENNIS_API_URL: str = "https://admin.gennis.uz/api"
    # OpenAI (active provider). Set OPENAI_API_KEY in .env.
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    # Legacy Groq Cloud settings kept so existing .env entries don't trip
    # validation. Services now call OpenAI; remove later once .env is cleaned.
    GROK_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROK_API_KEY: str = ""
    GROK_MODEL: str = "llama-3.3-70b-versatile"
    # Outbound proxy for AI calls — used to bypass geo-blocks (e.g. OpenAI
    # from Russia). Set in .env as: HTTP_PROXY=http://user:pass@host:port
    # Leave empty in environments where direct egress works.
    HTTP_PROXY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Tolerate unknown vars in .env so the backend doesn't crash when
        # someone adds a new entry (e.g. legacy GROQ_API_KEY) without
        # updating this class.
        extra = "ignore"


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
