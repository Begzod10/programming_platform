import httpx
from app.config import settings


async def analyze_project_with_grok(
        title: str,
        description: str,
        github_url: str,
        technologies: list[str],
        difficulty_level: str
) -> dict:
    """
    Grok AI yordamida proektni tahlil qiladi va baho beradi.
    """

    technologies_str = ", ".join(technologies) if technologies else "ko'rsatilmagan"

    prompt = f"""
Sen tajribali dasturlash o'qituvchisisiz. Quyidagi o'quvchi proektini baholab ber.

Proekt ma'lumotlari:
- Nomi: {title}
- Tavsifi: {description}
- GitHub: {github_url}
- Texnologiyalar: {technologies_str}
- Qiyinlik darajasi: {difficulty_level}

Quyidagi formatda JSON javob ber (boshqa hech narsa yozma, faqat JSON):
{{
    "grade": "A yoki B yoki C yoki D yoki F",
    "points": 0-100 orasida son,
    "feedback": "O'quvchiga batafsil fikr-mulohaza (o'zbek tilida)",
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

    headers = {
        "Authorization": f"Bearer {settings.GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GROK_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            settings.GROK_API_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]

    # JSON ni tozalab parse qilish
    import json
    import re
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group())
    else:
        result = {
            "grade": "C",
            "points": 60,
            "feedback": content,
            "strengths": [],
            "improvements": [],
            "summary": "AI tahlil qildi"
        }

    return result
