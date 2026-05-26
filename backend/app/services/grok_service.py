import httpx
import re
import json
from app.config import settings

async def analyze_project_with_grok(
        title: str,
        description: str,
        github_url: str,
        technologies: list[str],
        difficulty_level: str,
        previous_points: int = 0
) -> dict:
    """
    Grok AI yordamida proektni tahlil qiladi va baho beradi.
    """
    technologies_str = ", ".join(technologies) if technologies else "ko'rsatilmagan"

    previous_info = ""
    if previous_points > 0:
        previous_info = f"\nDIQQAT: Bu loyiha avval {previous_points} ball olgan edi. Agar ball oshgan bo'lsa, feedback da nima yaxshilanganini aniq ayt."

    prompt = f"""
Sen tajribali dasturlash o'qituvchisisiz. Quyidagi o'quvchi proektini baholab ber.
Proekt ma'lumotlari:
- Nomi: {title}
- Tavsifi: {description}
- GitHub: {github_url}
- Texnologiyalar: {technologies_str}
- Qiyinlik darajasi: {difficulty_level}
{previous_info}

Quyidagi formatda JSON javob ber (boshqa hech narsa yozma, faqat JSON):
{{
    "grade": "A yoki B yoki C yoki D yoki F",
    "points": 0-100 orasida son,
    "feedback": "O'quvchiga batafsil fikr-mulohaza (o'zbek tilida). Agar avval baholangan bo'lsa, nima yaxshilanganini ayt.",
    "strengths": ["kuchli tomon 1", "kuchli tomon 2"],
    "improvements": ["yaxshilash kerak 1", "yaxshilash kerak 2"],
    "summary": "Qisqa xulosa (1-2 jumla, o'zbek tilida)"
}}
Baholash mezonlari:
- A: 90-100 ball - Ajoyib proekt
- B: 75-89 ball - Yaxshi proekt
- C: 60-74 ball - O'rtacha proekt
- D: 45-59 ball - Qoniqarsiz
- F: 0-44 ball - Juda zaif
"""

    try:
        async with httpx.AsyncClient(timeout=60.0, proxy=settings.HTTP_PROXY or None) as client:
            response = await client.post(
                settings.openai_chat_url,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]

            # JSON ni qidirib topish
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "grade": "C",
                    "points": 60,
                    "feedback": text,
                    "strengths": [],
                    "improvements": [],
                    "summary": "AI javobi JSON formatida emas edi."
                }
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response:
            try:
                error_msg += f" - Response: {e.response.text}"
            except Exception:
                pass
        return {
            "grade": "F",
            "points": 0,
            "feedback": f"AI tahlilida xatolik yuz berdi: {error_msg}",
            "strengths": [],
            "improvements": [],
            "summary": "Xatolik yuz berdi."
        }


async def explain_word_with_ai(word: str) -> dict:
    """
    AI yordamida so'zni tushuntiradi: tarjima, ta'rif va misollar.
    Returns: {word, translation, definition, examples: list[str]}.
    """
    safe_word = (word or "").strip()
    if not safe_word:
        return {
            "word": "",
            "translation": "",
            "definition": "",
            "examples": [],
            "error": "Empty word",
        }
    if len(safe_word) > 80:
        safe_word = safe_word[:80]

    prompt = f"""
Sen ingliz tilini o'rgatuvchi tajribali o'qituvchisiz. Quyidagi so'zni o'quvchiga tushuntirib ber:
SO'Z: {safe_word}

Faqat JSON formatda javob ber (boshqa hech narsa yozma):
{{
    "word": "asl so'z",
    "translation": "o'zbek tilidagi tarjimasi (1-3 ta variant, vergul bilan)",
    "definition": "qisqa ta'rif (o'zbek tilida, 1-2 jumla)",
    "examples": ["ingliz tilida misol jumla 1", "ingliz tilida misol jumla 2"]
}}
"""

    fallback = {
        "word": safe_word,
        "translation": "",
        "definition": "",
        "examples": [],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0, proxy=settings.HTTP_PROXY or None) as client:
            response = await client.post(
                settings.openai_chat_url,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 400,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]

            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if not json_match:
                return {**fallback, "definition": text.strip()[:500]}

            parsed = json.loads(json_match.group())
            return {
                "word": str(parsed.get("word") or safe_word),
                "translation": str(parsed.get("translation") or ""),
                "definition": str(parsed.get("definition") or ""),
                "examples": [str(x) for x in (parsed.get("examples") or []) if x][:5],
            }
    except Exception as e:
        return {**fallback, "error": f"AI xatolik: {str(e)[:200]}"}