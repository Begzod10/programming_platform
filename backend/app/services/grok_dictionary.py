"""AI-powered word explanation and answer checking for the dictionary feature.

Public API:
  explain_word_with_ai(word, ...)  — dictionary lookup (400 tok cap)
  check_word_meaning_with_ai(...)  — review answer checker
"""
from __future__ import annotations

from typing import Optional
import re
import json
import logging

from app.services.grok_ai_client import _ask_ai

logger = logging.getLogger(__name__)


def _parse_json(text: str) -> Optional[dict]:
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return None


def _looks_like_keyword_stew(text: str, lang: str = "uz") -> bool:
    """Reject AI outputs that are a list of bare terms rather than a sentence.

    Symptom we hit in prod: model echoes lesson keywords ("content appearance
    behavior HTML structure tags Browser CSS …") instead of defining the word,
    or returns short comma-lists like "Frontend, Backend, JavaScript, HTML".
    Heuristic: no connective tissue (verb/copula/etc.) AND most tokens are
    bare alpha terms → almost certainly stew.

    `lang` selects which connective-word list to check against. This used to
    be Uzbek-only, which meant a perfectly normal RUSSIAN sentence (e.g. "Это
    CSS-свойство, которое задерживает начало анимации.") has none of the
    Uzbek tokens, falls through to the bare-token-ratio check, and gets
    misclassified as stew — ordinary prose easily clears the >70%-alpha-
    tokens bar with only a trailing period. Confirmed in prod: RU dictionary
    entries ended up with a blank definition ~5x more often than UZ ones,
    on the exact same terms (e.g. "animation-delay") repeatedly. See
    RU_SIGNAL below.
    """
    s = (text or "").strip()
    if not s:
        return True
    # Strip leading/trailing quote chars the model sometimes wraps things in
    s = s.strip("\"'«»""").strip()
    # A real sentence has spaces AND at least one of these connective tokens
    # (verb, copula) — keyword soups have none of these. Do NOT add weak
    # conjunctions like "va"/"yoki"/"и"/"или": they appear in pure lists too
    # ("HTML va CSS" / "HTML и CSS") and would let stew slip through.
    # Stems, not full conjugated forms — both languages are heavily
    # inflected/agglutinative, so a fixed-form list misses participles like
    # "qo'shadigan" (adds/adding) or "задающее" (setting/that sets). A stem
    # substring naturally covers every suffixed variant. Bounded with a
    # leading space to avoid matching mid-word inside an unrelated term.
    UZ_SIGNAL = (" — ", " bu ", " bo'l", " hisoblan", " ishlat",
                 " yarat", " yordam", " uchun ", " sifatida", " ya'ni ",
                 " bilan ", " orqali ", " ko'rsat", " saqla", " tasvirl",
                 " qil", " ber", " maydon", " ramka", " degan ",
                 " qo'sh", " belgila", " aniqla", " bajar", " boshqar",
                 " o'zgartir", " ta'minla", " kechiktir", " kirit", " chiqar")
    RU_SIGNAL = (" — ", " это ", " являет", " использ", " позволя",
                 " нужен", " нужна", " нужно", " с помощью", " котор",
                 " задаёт", " задает", " задающ", " задерж", " определя",
                 " устанавлив", " создава", " создаёт", " создает",
                 " указыва", " обознач", " хранит", " хранящ", " означа",
                 " служит", " чтобы ")
    signals = RU_SIGNAL if lang == "ru" else UZ_SIGNAL
    # Pad with a leading space so a signal word starting the sentence still
    # matches — Russian and Uzbek both commonly drop the subject and open
    # straight on the verb (e.g. "Определяет, как..." = "[It] defines...",
    # no space precedes "определя" since it's the very first token). Without
    # this padding every signal-opening sentence fell through to the
    # bare-token-ratio check and got misclassified as stew.
    has_signal = any(sig in (" " + s.lower()) for sig in signals)
    if has_signal:
        return False
    # Structural fallback: a comma joining two multi-word clauses is real
    # prose (a subordinate/participial clause), whatever verb it happens to
    # use — enumerating every possible verb stem is a losing game (e.g.
    # "...yopishib, qolgan bo'shliqlar teng taqsimlanadi" hits none of the
    # signal lists above but is a perfectly normal sentence). A bare noun
    # list ("Frontend, Backend, JavaScript, HTML") only ever has single-word
    # segments, so this doesn't let those back in.
    if "," in s:
        segments = [seg.strip() for seg in s.split(",") if seg.strip()]
        if segments and max(len(seg.split()) for seg in segments) >= 3:
            return False
    # No signal — strip per-token punctuation (commas, periods) so
    # "Frontend, Backend" counts as bare alpha tokens. Threshold lowered to
    # 4 tokens so short comma-lists are caught too.
    PUNCT = ",.;:!?·•«»\"'()[]{}—–-"
    tokens = [t.strip(PUNCT) for t in s.split()]
    tokens = [t for t in tokens if t]
    if len(tokens) >= 4:
        alpha_only = [t for t in tokens if t.replace("-", "").isalpha()]
        if alpha_only and len(alpha_only) / len(tokens) > 0.7:
            return True
    return False


_MERMAID_SIGNALS = ("flowchart ", "graph ", "sequencediagram", "classDiagram",
                    "stateDiagram", "gantt\n", "erdiagram", "→", "-->", "->>",
                    "subgraph ", "|content")


def _looks_like_diagram(text: str) -> bool:
    """Reject responses that are mermaid/diagram syntax instead of a definition."""
    s = (text or "").strip()
    return any(sig in s for sig in _MERMAID_SIGNALS)


def _restates_target_word(text: str, word: str) -> bool:
    """True if the definition opens by naming the very word it defines.

    Symptom we hit in prod: the model answers "JavaScript — bu ... dasturlash
    tili." — grammatically fine, but this gets stored as `context` and shown
    verbatim on recall-style practice surfaces (Quiz+ round 2, Spelling,
    Listening, MCQ meaning options) where the student's job is to produce
    the word from its meaning. Opening with the word hands back the answer.
    `_mask_word_in_text` in practice_words.py is the display-time safety
    net; this check keeps newly generated contexts clean at the source.
    """
    s = (text or "").strip().lower()
    w = (word or "").strip().lower()
    if not s or not w:
        return False
    return s[: len(w) + 5].startswith(w) or f'"{w}"' in s[: len(w) + 10]


def _sanity_check_explanation(parsed: dict, word: str, excerpt: str, lang: str = "uz") -> bool:
    """True if the parsed explanation looks usable; False to retry/fallback."""
    if not isinstance(parsed, dict):
        return False
    sd = (parsed.get("short_definition") or "").strip()
    if not sd:
        return False
    if len(sd) < 8:
        return False
    # Don't accept the lesson excerpt being echoed back verbatim.
    ex_norm = (excerpt or "").strip().lower()[:80]
    if ex_norm and ex_norm in sd.lower():
        return False
    if _looks_like_keyword_stew(sd, lang=lang):
        return False
    if _looks_like_diagram(sd):
        return False
    if _restates_target_word(sd, word):
        return False
    return True


async def explain_word_with_ai(
    word: str,
    *,
    course_title: str = "",
    lesson_title: str = "",
    lesson_excerpt: str = "",
    lang: str = "uz",
) -> dict:
    """AI yordamida so'zni O'ZBEK TILIDA tushuntiradi.

    The optional course/lesson hints scope the meaning. The same word means
    different things in different courses — "Panel" in a JS course is the
    DevTools panel, in a UI course it's a sidebar panel. Passing the lesson
    context lets the model pick the right sense.

    Reliability layers:
      1. Strict prompt — the word is centred; excerpt is supporting hint only.
      2. JSON-only output enforced + parsed defensively.
      3. Sanity check rejects keyword stews / excerpt echoes.
      4. One retry with a "you produced X — try again, focus on the word"
         feedback prompt if the first response fails sanity.
    """
    safe_word = (word or "").strip()
    if not safe_word:
        return {"word": "", "translation": "", "definition": "", "examples": [], "error": "Empty word"}
    if len(safe_word) > 80:
        safe_word = safe_word[:80]

    # Detect script: if >30 % of alphabetic chars are Cyrillic → Russian word.
    alpha = [c for c in safe_word if c.isalpha()]
    cyrillic_ratio = sum(1 for c in alpha if "Ѐ" <= c <= "ӿ") / max(len(alpha), 1)
    is_russian = cyrillic_ratio > 0.3

    # Trim the excerpt hard — 150 chars is enough to disambiguate sense; more
    # and the model starts repeating lesson keywords instead of defining the
    # word. (Symptom in prod: "JavaScript" and "HTML" got identical contexts
    # because the same 400-char lesson body dominated both prompts.)
    excerpt_clean = (lesson_excerpt or "").strip().replace("\n", " ")[:150]

    scope_lines = []
    if course_title:
        scope_lines.append(f"Kurs nomi: {course_title}")
    if lesson_title:
        scope_lines.append(f"Dars nomi: {lesson_title}")
    if excerpt_clean:
        scope_lines.append(f"Dars kontekstidan parcha (faqat ma'no aniqlash uchun): \"{excerpt_clean}\"")
    scope_block = ("\n".join(scope_lines) + "\n") if scope_lines else ""

    def _build_prompt(retry_feedback: str = "") -> str:
        feedback_uz = (
            f"\nOldingi javobing yaroqsiz edi: {retry_feedback}\n"
            f"Endi qaytadan, FAQAT \"{safe_word}\" so'zi haqida yoz.\n"
            if retry_feedback else ""
        )
        feedback_ru = (
            f"\nТвой предыдущий ответ не прошёл проверку: {retry_feedback}\n"
            f"Повтори, сосредоточившись только на слове \"{safe_word}\".\n"
            if retry_feedback else ""
        )

        if lang == "ru":
            return f"""\
Ты — преподаватель программирования, объясняющий термины на русском языке.

ЗАДАЧА: Объясни следующий термин или слово НА РУССКОМ ЯЗЫКЕ.

СЛОВО: "{safe_word}"

{scope_block}ПРАВИЛА:
- Пиши только о "{safe_word}", не пересказывай текст урока.
- Ответ должен быть полностью НА РУССКОМ ЯЗЫКЕ (технические названия могут остаться на английском).
- "short_definition" — 1 законченное предложение с глаголом.
  Пример: "Это CSS-правило, которое задаёт шаги анимации элемента."
  ПЛОХО: "keyframes animation steps css" (просто список слов).
- НЕ начинай "short_definition" с повторения самого термина "{safe_word}"
  (например, не пиши "{safe_word} — это..."). Слово используется как ответ
  в упражнениях на запоминание, повтор в начале определения выдаёт ответ.
- Не перечисляй другие ключевые слова.
{feedback_ru}
ОТВЕТЬ СТРОГО В СЛЕДУЮЩЕМ JSON-ФОРМАТЕ (никаких пояснений, никаких ```json):
{{
    "word": "{safe_word}",
    "short_definition": "1 законченное предложение о '{safe_word}'",
    "full_explanation": "3-5 предложений — подробное объяснение",
    "example": "1 практический пример использования",
    "category": "например: Язык программирования, Фреймворк, CSS-правило, Термин",
    "part_of_speech": "существительное | глагол | прилагательное | термин | выражение | код"
}}
"""
        if is_russian:
            return f"""\
Sen rus tilidan o'zbek tiliga professional tarjimon va izohlovchisisiz.

VAZIFA: Quyidagi rus tilidagi so'z yoki iborani O'ZBEK TILIGA tarjima qil va tushuntir.

SO'Z: "{safe_word}"

{scope_block}MUHIM QOIDALAR:
- "short_definition" — O'zbek tiliga tarjimasi va 1 ta to'liq tushuntirish jumla.
  Misol: "O'zgaruvchi; dasturda ma'lumotlarni saqlash uchun ishlatiladigan nom."
- "short_definition" ichida asl rus so'zi "{safe_word}"ni qayta yozmang —
  bu so'z takrorlash mashqlarida javob sifatida ishlatiladi, uni ta'rif
  ichida ko'rsatish javobni oldindan aytib qo'yadi.
- Javob O'ZBEK TILIDA bo'lsin.
{feedback_uz}
FAQAT QUYIDAGI JSON FORMATIDA JAVOB BER (boshqa hech narsa yozma, hatto ```json belgisini ham):
{{
    "word": "{safe_word}",
    "short_definition": "O'zbekcha tarjima va 1 ta tushuntirish jumla",
    "full_explanation": "2-3 jumla — batafsil tushuntirish o'zbek tilida",
    "example": "1 ta misol",
    "category": "masalan: Ot, Fe'l, Sifat, Atama",
    "part_of_speech": "ot | fe'l | sifat | ibora | atama"
}}
"""
        return f"""\
Sen dasturlash va texnologiyalar bo'yicha o'zbek tilida izohlovchi o'qituvchisisiz.

VAZIFA: Quyidagi bitta so'z yoki atamani O'ZBEK TILIDA tushuntir.

SO'Z: "{safe_word}"

{scope_block}MUHIM QOIDALAR:
- Faqat "{safe_word}" so'zi/atamasi haqida yoz, dars matnini takrorlama.
- Javob to'liq O'ZBEK TILIDA bo'lsin (atamalar nomi ingliz qolishi mumkin).
- "short_definition" — 1 ta to'liq jumla, fe'l bilan, gap tuzilishi bilan.
  Misol: "Veb-sahifalarga dinamiklik qo'shadigan dasturlash tili."
  YOMON misol: "content appearance behavior HTML tags" (faqat so'zlar ro'yxati).
- "short_definition"ni so'zning o'zini takrorlab boshlamang (masalan,
  "{safe_word} — bu ..." deb yozmang). Bu so'z takrorlash mashqlarida
  o'quvchi topishi kerak bo'lgan javob — uni ta'rif ichida ko'rsatish
  javobni oldindan aytib qo'yadi.
- Boshqa kalit so'zlarni ro'yxatlab tashlamang.
{feedback_uz}
FAQAT QUYIDAGI JSON FORMATIDA JAVOB BER (boshqa hech narsa yozma, hatto ```json belgisini ham):
{{
    "word": "{safe_word}",
    "short_definition": "1 ta to'liq jumla — '{safe_word}' nimaligini aytib bersin",
    "full_explanation": "3-5 jumla — batafsil tushuntirish",
    "example": "1 ta amaliy misol yoki qo'llanilish",
    "category": "masalan: Dasturlash tili, Belgilash tili, Freymvork, Kutubxona, Atama",
    "part_of_speech": "ot | fe'l | sifat | ibora | atama | kod"
}}
"""

    fallback = {
        "word": safe_word,
        "short_definition": "",
        "full_explanation": "",
        "example": "",
        "category": "",
        "part_of_speech": "",
    }

    # First attempt
    text = await _ask_ai(_build_prompt())
    parsed = _parse_json(text) if text else None
    if parsed and _sanity_check_explanation(parsed, safe_word, excerpt_clean, lang=lang):
        return parsed

    # One retry with explicit feedback about what was wrong
    feedback_reason = ""
    if parsed is None:
        feedback_reason = "JSON formatda emas edi"
    elif not (parsed.get("short_definition") or "").strip():
        feedback_reason = "short_definition bo'sh edi"
    elif _looks_like_keyword_stew(parsed.get("short_definition", ""), lang=lang):
        feedback_reason = "to'liq jumla emas — faqat so'zlar ro'yxati edi"
    elif _restates_target_word(parsed.get("short_definition", ""), safe_word):
        feedback_reason = f"ta'rif \"{safe_word}\" so'zining o'zini takrorlab boshlandi — faqat ma'nosini yoz, so'zni qaytarma"
    else:
        feedback_reason = "dars matnini takrorlading"

    logger.warning(
        "explain_word_with_ai: retrying for word=%r reason=%s",
        safe_word, feedback_reason,
    )
    text2 = await _ask_ai(_build_prompt(retry_feedback=feedback_reason))
    parsed2 = _parse_json(text2) if text2 else None
    if parsed2 and _sanity_check_explanation(parsed2, safe_word, excerpt_clean, lang=lang):
        return parsed2

    # Both attempts failed sanity. Prefer a clean empty over a junk string —
    # the frontend renders "" as no-context, which is better than gibberish.
    logger.warning(
        "explain_word_with_ai: both attempts failed sanity for word=%r",
        safe_word,
    )
    if not text and not text2:
        return {**fallback, "short_definition": "AI xizmati hozirda mavjud emas."}
    return fallback


async def check_word_meaning_with_ai(word: str, correct_meaning: str, user_meaning: str) -> dict:
    """O'quvchi yozgan ma'noni AI orqali O'ZBEK TILIDA tekshiradi."""

    prompt = f"""
O'quvchi so'zning ma'nosini yozdi. Uni tekshir va fikr bil.
Barcha javoblar faqat O'ZBEK TILIDA bo'lsin.

So'z: {word}
To'g'ri ma'no: {correct_meaning}
O'quvchi yozgan: {user_meaning}

Faqat JSON formatda javob ber (boshqa hech narsa yozma):
{{
    "is_correct": true yoki false,
    "feedback": "O'quvchiga o'zbek tilida qisqa izoh (to'g'ri bo'lsa rag'batlantir, noto'g'ri bo'lsa to'g'ri ma'noni tushuntir)"
}}
"""

    text = await _ask_ai(prompt)
    if text:
        parsed = _parse_json(text)
        if parsed:
            return parsed
    return {"is_correct": False, "feedback": "AI tekshira olmadi."}
