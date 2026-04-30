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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                settings.GROK_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROK_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": 1000
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
            except:
                pass
        return {
            "grade": "F",
            "points": 0,
            "feedback": f"AI tahlilida xatolik yuz berdi: {error_msg}",
            "strengths": [],
            "improvements": [],
            "summary": "Xatolik yuz berdi."
        }