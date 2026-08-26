from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices
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
    # The old system (admin.gennis.uz) was switched off at the cutover, so its
    # /base/login no longer answers. management-v2 exposes a compatibility
    # endpoint (POST /login, GET /group/{id}/students, GET /flow/{id}/students)
    # returning the same shape the sync code below expects, which is why
    # GennisService keeps its original parsing. Points at management-v2 (the
    # DB owner) directly — no fallback to gennis-v2's own copy of this shim;
    # if this URL is ever unreachable, login falls through to local auth the
    # same way it always has, it does NOT retry against gennis-v2.
    MGMT_INTEGRATION_URL: str = "https://office.gennis.uz/api/v1/integrations/student-platform"
    # ─── AI providers ────────────────────────────────────────────────────
    # AI calls iterate through this chain in order, using the first provider
    # whose API key is set and whose call succeeds. OpenAI-only per explicit
    # request — Gemini/Groq fallback removed after Groq's free-tier rate
    # limit ("limit tugadi") started surfacing as user-facing failures under
    # real classroom load (e.g. projects 2492/2504 auto-rejected on a 429).
    # Comma-separated; valid values: "groq", "gemini", "openai".
    AI_PROVIDER_CHAIN: str = "openai"

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

    # Groq Cloud (OpenAI-compatible endpoint) — free tier is generous
    # (~30 req/min) and llama-3.3-70b returns solid JSON-mode output for the
    # grading task. Accepts .env as either GROK_API_KEY or GROQ_API_KEY (the
    # product's actual name) — deployed .env files use both spellings and
    # pydantic's extra="ignore" would otherwise silently drop the unmatched
    # one, leaving this provider disabled with no error.
    GROK_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROK_API_KEY: str = Field(
        default="", validation_alias=AliasChoices("GROK_API_KEY", "GROQ_API_KEY"),
    )
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

    # ─── Parent Telegram bot integration ────────────────────────────────
    # Fire-and-forget notification to gennis_parent_bot when a game session
    # is completed. The bot fetches the full summary back via the
    # secret-authenticated /summary-public endpoint (auth is a plain shared
    # secret, not JWT, because the bot doesn't have a user token). Leaving
    # PARENT_BOT_URL empty disables the integration cleanly — no config
    # error, just no outbound push.
    PARENT_BOT_URL: str = ""  # e.g. http://127.0.0.1:8064
    PARENT_BOT_SECRET: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Tolerate unknown vars in .env so the backend doesn't crash when
        # someone adds a new entry (e.g. legacy GROQ_API_KEY) without
        # updating this class.
        extra = "ignore"


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
