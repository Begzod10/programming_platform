from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:123@localhost:5432/Student_Platform"
    APP_NAME: str = "Student Programming Platform"
    DEBUG: bool = False
    # SECRET_KEY is REQUIRED in .env. No default — startup fails loudly if missing,
    # which is intentional: a hardcoded default would let attackers forge JWTs
    # against any deploy that forgot to set it.
    SECRET_KEY: str = Field(..., min_length=16)
    JWT_ALGORITHM: str = "HS256"
    # 30 minutes — short-lived access tokens. Refresh flow handles long sessions.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = ".py,.js,.html,.css,.json,.md,.txt,.zip"
    API_V1_PREFIX: str = "/api/v1"
    # Comma-separated list of allowed origins. Default to local dev only —
    # production MUST override via .env. Wildcard with credentials is unsafe
    # and the CORS spec forbids it.
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    APP_VERSION: str = "1.0.0"
    GENNIS_API_URL: str = "https://admin.gennis.uz/api"
    # OpenAI (active provider). Set OPENAI_API_KEY in .env.
    # OPENAI_BASE_URL lets you point at a relay (e.g. a Cloudflare Worker)
    # without the geo-blocks OpenAI applies to api.openai.com directly.
    # If empty, falls back to OPENAI_API_URL.
    OPENAI_BASE_URL: str = ""
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    @property
    def openai_chat_url(self) -> str:
        if self.OPENAI_BASE_URL:
            return f"{self.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
        return self.OPENAI_API_URL

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.BACKEND_CORS_ORIGINS.strip()
        # Tolerate both formats so existing .env files using JSON-list syntax
        # (legacy pydantic v1 style) keep working:  ["http://a", "http://b"]
        if raw.startswith("["):
            import json
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(o).strip() for o in parsed if str(o).strip()]
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in raw.split(",") if o.strip()]

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
