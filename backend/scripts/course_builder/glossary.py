"""RU terminology for course content — one preferred Russian term per concept.

Machine and human translators drift: "endpoint" became "конечная точка" in one lesson and "эндпоинт" in
the next. `lint_spec` rejects the forbidden variants (outside code blocks) and names the preferred term.
Extend this table when a new concept appears; keep the preferred term what Russian developers actually say.
"""
from __future__ import annotations

import re

RU_GLOSSARY: dict[str, dict] = {
    "endpoint": {"ru": "эндпоинт", "forbidden": ["конечная точка", "конечной точки", "конечную точку", "энд-поинт", "эндпойнт"]},
    "token": {"ru": "токен", "forbidden": ["жетон", "маркер доступа"]},
    "middleware": {"ru": "мидлвар", "forbidden": ["промежуточное по", "промежуточный обработчик", "мидлвэр"]},
    "deploy": {"ru": "деплой", "forbidden": ["развёртывание приложения", "разворачивание"]},
    "frontend": {"ru": "фронтенд", "forbidden": ["фронт-энд", "фронтэнд", "фронт энд"]},
    "backend": {"ru": "бэкенд", "forbidden": ["бекенд", "бэкэнд", "бек-энд", "бэк-энд"]},
    "request": {"ru": "запрос", "forbidden": ["реквест"]},
    "response": {"ru": "ответ", "forbidden": ["респонс", "респонз"]},
    "route": {"ru": "маршрут", "forbidden": ["роут ", "роуты", "роутинг"]},
    "database": {"ru": "база данных", "forbidden": ["датабаза", "бд-шка"]},
    "framework": {"ru": "фреймворк", "forbidden": ["фрэймворк", "фреймворк-а"]},
    "library": {"ru": "библиотека", "forbidden": ["либа", "лайбрери"]},
    "commit": {"ru": "коммит", "forbidden": ["комит", "фиксация изменений"]},
    "branch": {"ru": "ветка", "forbidden": ["бранч", "бранчи"]},
    "repository": {"ru": "репозиторий", "forbidden": ["репо ", "хранилище кода"]},
    "bug": {"ru": "баг", "forbidden": ["жучок", "ошибка-баг"]},
    "API": {"ru": "API", "forbidden": ["апи ", "эйпиай"]},
}

_PRE = re.compile(r"<pre[^>]*>.*?</pre>|<code[^>]*>.*?</code>", re.S | re.I)
_FORBIDDEN = [(variant, entry["ru"]) for entry in RU_GLOSSARY.values() for variant in entry["forbidden"]]


def forbidden_ru_terms(text: str) -> list[tuple[str, str]]:
    """[(forbidden variant found, preferred term)] — code blocks are ignored."""
    prose = _PRE.sub(" ", text or "").lower() + " "
    return [(variant.strip(), good) for variant, good in _FORBIDDEN if variant.lower() in prose]
