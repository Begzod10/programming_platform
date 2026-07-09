"""
Generate and insert namuna (sample) codes for lessons missing them.
Run from backend/ directory: python scripts/generate_namuna.py
"""
import asyncio
import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.lesson_sample import LessonSample
from app.services.grok_service import call_chain

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SYSTEM_PROMPT = """Sen o'zbek tilida dars beradigan dasturlash o'qituvchisisiz.
Berilgan dars mavzusi uchun qisqa, aniq va o'quvchi uchun foydali namuna kod yozasiz.
Faqat JSON formatida javob ber, boshqa hech narsa yozma."""

def make_user_prompt(title, course, code_language, sections_preview):
    lang_hint = code_language or "html/css/js"
    return f"""Dars: "{title}"
Kurs: "{course}"
Dasturlash tili: {lang_hint}
Dars mazmuni (qisqa): {sections_preview[:500] if sections_preview else 'mavjud emas'}

Ushbu dars uchun namuna kod yarat. Qoidalar:
- Namuna kod dars mavzusini aniq ko'rsatishi kerak
- Kod qisqa va tushunarli bo'lsin (20-50 qator)
- Faqat quyidagi JSON formatida javob ber:

Agar web (HTML/CSS/JS) namuna bo'lsa:
{{
  "sample_type": "web",
  "title": "Namuna: [mavzu nomi]",
  "description": "Qisqa tavsif (1 jumla)",
  "html_code": "...",
  "css_code": "...",
  "js_code": ""
}}

Agar Python namuna bo'lsa:
{{
  "sample_type": "python",
  "title": "Namuna: [mavzu nomi]",
  "description": "Qisqa tavsif",
  "html_code": "# Python kodi bu yerda",
  "css_code": "",
  "js_code": ""
}}

Agar SQL namuna bo'lsa:
{{
  "sample_type": "sql",
  "title": "Namuna: [mavzu nomi]",
  "description": "Qisqa tavsif",
  "html_code": "-- SQL kodi bu yerda",
  "css_code": "",
  "js_code": ""
}}

Git/bash darslar uchun web tipida chiroyli HTML ko'rsatma sahifa yarat (terminalda qanday buyruq ishlatilishini vizual ko'rsatuvchi).

FAQAT JSON qaytargin, izoh yoki boshqa matn yozma."""


async def fetch_missing_lessons(session):
    result = await session.execute(text("""
        SELECT l.id, l.title, l.code_language, c.title as course, l.sections_json
        FROM lessons l
        JOIN courses c ON c.id = l.course_id
        LEFT JOIN lesson_samples ls ON ls.lesson_id = l.id
        WHERE l.is_published = true AND ls.id IS NULL
        ORDER BY c.title, l."order"
    """))
    return result.fetchall()


async def generate_sample(title, course, code_language, sections_json):
    sections_preview = ""
    if sections_json:
        try:
            sections = json.loads(sections_json)
            for s in sections[:2]:
                if s.get("type") == "text" and s.get("html"):
                    import re
                    text_clean = re.sub(r'<[^>]+>', ' ', s["html"])[:300]
                    sections_preview += text_clean + " "
        except Exception:
            pass

    prompt = make_user_prompt(title, course, code_language, sections_preview)

    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt
    try:
        raw, _, _, _ = await call_chain(full_prompt, max_tokens=1200)
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  ERROR generating: {e}")
        return None


async def main():
    async with AsyncSessionLocal() as session:
        lessons = await fetch_missing_lessons(session)
        print(f"Found {len(lessons)} lessons without namuna codes")

        success = 0
        failed = 0

        for row in lessons:
            lesson_id, title, code_language, course, sections_json = row
            print(f"[{lesson_id}] {course} / {title[:50]}...", end=" ", flush=True)

            data = await generate_sample(title, course, code_language, sections_json)
            if not data:
                print("FAILED")
                failed += 1
                continue

            sample = LessonSample(
                lesson_id=lesson_id,
                title=data.get("title", f"Namuna: {title}"),
                description=data.get("description", ""),
                sample_type=data.get("sample_type", "web"),
                html_code=data.get("html_code") or None,
                css_code=data.get("css_code") or None,
                js_code=data.get("js_code") or None,
            )
            session.add(sample)
            try:
                await session.commit()
                print("OK")
                success += 1
            except Exception as e:
                await session.rollback()
                print(f"DB ERROR: {e}")
                failed += 1

            # Small delay to avoid rate limits
            await asyncio.sleep(1)

        print(f"\nDone: {success} inserted, {failed} failed")


if __name__ == "__main__":
    asyncio.run(main())
