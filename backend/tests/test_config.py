"""Covers Settings.cors_origins_list, which main.py's CORSMiddleware now
actually reads (previously wired to a hardcoded allow_origins=["*"] instead
— see docs/PROJECT_KNOWLEDGE.md §12 and BACKEND_BUGS.md's CORS entry). Must
tolerate both the documented comma-separated format and the legacy
JSON-list format some deployed .env files still use.
"""
from app.config import Settings


def _settings(cors_value: str) -> Settings:
    # Pass kwargs directly rather than mutating env vars — pydantic-settings
    # accepts constructor overrides ahead of .env/environment, and this
    # keeps each test's value isolated from the others.
    return Settings(SECRET_KEY="test-secret-key-minimum-32-characters-xxx", BACKEND_CORS_ORIGINS=cors_value)


class TestCorsOriginsList:
    def test_comma_separated_format(self):
        s = _settings("https://tech.gennis.uz,https://admin.gennis.uz")
        assert s.cors_origins_list == ["https://tech.gennis.uz", "https://admin.gennis.uz"]

    def test_comma_separated_format_tolerates_whitespace(self):
        s = _settings(" https://tech.gennis.uz , https://admin.gennis.uz ")
        assert s.cors_origins_list == ["https://tech.gennis.uz", "https://admin.gennis.uz"]

    def test_legacy_json_list_format(self):
        s = _settings('["https://tech.gennis.uz", "https://admin.gennis.uz"]')
        assert s.cors_origins_list == ["https://tech.gennis.uz", "https://admin.gennis.uz"]

    def test_single_origin_comma_separated(self):
        s = _settings("http://localhost:3000")
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_single_origin_json_list(self):
        s = _settings('["http://localhost:3000"]')
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_malformed_json_falls_back_to_comma_split(self):
        # Starts with "[" but isn't valid JSON — must not crash; falls back
        # to treating the whole thing as a (degenerate) comma-separated list
        # rather than raising, since a live CORS config is not the place to
        # 500 the entire app over a typo.
        s = _settings("[not valid json")
        assert s.cors_origins_list == ["[not valid json"]

    def test_empty_string_yields_empty_list(self):
        s = _settings("")
        assert s.cors_origins_list == []
