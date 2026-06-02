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
    # ─── AI providers ────────────────────────────────────────────────────
    # AI calls iterate through this chain in order, using the first provider
    # whose API key is set and whose call succeeds. Cheaper/faster providers
    # come first; OpenAI is the high-quality fallback.
    # Comma-separated; valid values: "groq", "gemini", "openai".
    AI_PROVIDER_CHAIN: str = "groq,gemini,openai"

    # OpenAI. OPENAI_BASE_URL lets you point at a relay (e.g. a Cloudflare
    # Worker) to bypass the geo-blocks OpenAI applies to api.openai.com
    # directly. If empty, falls back to OPENAI_API_URL.
    OPENAI_BASE_URL: str = ""
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # Google Gemini (v1beta generateContent endpoint). Auth is via ?key=...
    # query param, not a Bearer header. Free tier supports gemini-2.5-flash.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def openai_chat_url(self) -> str:
        if self.OPENAI_BASE_URL:
            return f"{self.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
        return self.OPENAI_API_URL

    @property
    def ai_provider_chain_list(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for raw in self.AI_PROVIDER_CHAIN.split(","):
            name = raw.strip().lower()
            if name and name not in seen:
                seen.add(name)
                out.append(name)
        return out

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

    # Groq Cloud (OpenAI-compatible endpoint). First in the default provider
    # chain — free tier is generous (~30 req/min) and llama-3.3-70b returns
    # solid JSON-mode output for the grading task. Env var names are kept
    # as GROK_* (not GROQ_*) so existing .env files don't break.
    GROK_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROK_API_KEY: str = ""
    GROK_MODEL: str = "llama-3.3-70b-versatile"
    # Outbound proxy for AI calls — used to bypass geo-blocks (e.g. OpenAI
    # from Russia). Set in .env as: HTTP_PROXY=http://user:pass@host:port
    # Leave empty in environments where direct egress works.
    HTTP_PROXY: str = ""

    # GitHub Personal Access Token (read-only public scope is enough).
    # Optional but strongly recommended: unauthenticated GitHub API calls are
    # capped at 60/hr/IP and will fail under any real load.
    GITHUB_TOKEN: str = ""
    # Hard cap on AI project reviews per student per UTC day. Prevents
    # points-farming and OpenAI budget drain even if the AI passes back
    # malformed/empty grades. Counts both manual triggers AND auto-triggers
    # fired on lesson submission, so set this high enough to cover the
    # whole course (11 lessons in basics + some retries). Set to 0 to
    # disable AI review entirely.
    MAX_AI_REVIEWS_PER_DAY: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Tolerate unknown vars in .env so the backend doesn't crash when
        # someone adds a new entry (e.g. legacy GROQ_API_KEY) without
        # updating this class.
        extra = "ignore"


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
