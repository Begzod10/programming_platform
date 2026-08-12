"""Add a class-name glossary to each Tailwind lesson's demo code.

Same problem as Bootstrap (see enhance_course_56_bootstrap_glossary.py),
worse in absolute numbers because Tailwind is utility-first: the capstone
lesson's landing page alone uses 70+ distinct classes. Rather than a flat
70-line dump, lesson 525 (the intro lesson) gets a short explanation of
the NAMING SYSTEM itself (spacing/color scale, responsive and state
prefixes) once, and every lesson's own list only needs to cover the
specific classes it uses -- a student who has the system explained can
decompose scale variants (mb-1 / mb-3 / mb-6) themselves.

Idempotent: keyed by MARKER, re-running is a no-op if already applied.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from enhance_lesson_helpers import append_bug_marker  # noqa: E402

MARKER = "📖 Klasslar lug'ati"

SYSTEM_INTRO_UZ = """<p>Tailwind'da klasslar ma'lum qoidalar bilan nomlanadi:</p>
<ul>
  <li>Masofa/o'lcham (padding, margin, height, width): raqam × 0.25rem (masalan 4 = 1rem = 16px).</li>
  <li>Ranglar: <code>rang-nomi-soya</code>, soya 50 (eng och) dan 950 (eng to'q) gacha.</li>
  <li><code>hover:</code>, <code>focus:</code>, <code>active:</code>, <code>disabled:</code> — foydalanuvchi harakatiga qarab yoqiladigan prefikslar.</li>
  <li><code>sm:</code>, <code>md:</code>, <code>lg:</code>, <code>xl:</code> — Bootstrap'dagi kabi mobile-first: "shu va undan katta ekranlarda" degani.</li>
</ul>"""

GLOSSARY = {
    525: [
        ("bg-gray-100", "Juda och kulrang fon (gray oilasi, 100-soya)."),
        ("font-semibold", "O'rtacha qalinlikdagi shrift (bold'dan biroz yengilroq)."),
        ("hover:bg-blue-700", "Sichqoncha ustiga kelganda fon to'q ko'k (blue-700) bo'ladi."),
        ("justify-center", "Flex/grid elementlarni asosiy o'q bo'ylab markazga tekislaydi."),
        ("mb-2 / mb-4", "Pastdan tashqi bo'shliq, mos ravishda 0.5rem va 1rem."),
        ("min-h-screen", "Minimal balandlikni butun ekran balandligiga (100vh) o'rnatadi."),
        ("px-4", "Chap-o'ng ichki bo'shliq, 1rem."),
        ("text-gray-600", "O'rtacha to'qlikdagi kulrang matn rangi."),
        ("transition-colors", "Rang o'zgarishlarini (fon, matn, chegara) silliq animatsiya qiladi."),
    ],
    526: [
        ("bg-gradient-to-br", "Yuqori chapdan pastki o'ngga (bottom-right) yo'nalgan gradient fon boshlaydi."),
        ("from-indigo-500 / to-purple-600", "Gradientning boshlang'ich va tugash ranglari."),
        ("bg-indigo-600, bg-slate-50/100/200", "Rang oilasi (indigo, slate) + soya raqami bo'yicha fon ranglari."),
        ("text-indigo-600, text-slate-500/600/800", "Xuddi shu tamoyil bilan matn ranglari."),
        ("hover:text-indigo-600", "Sichqoncha ustida matn rangi indigo-600 ga o'zgaradi."),
        ("lg:col-span-2", "lg ekrandan boshlab grid ustunlarining 2 tasini egallaydi."),
        ("gap-3", "Grid/flex elementlar orasidagi bo'shliq, 0.75rem."),
        ("h-10 / h-32 / w-10", "Qattiq belgilangan balandlik/kenglik (10 = 2.5rem, 32 = 8rem)."),
        ("mb-8 / mt-4 / mt-auto", "Tashqi bo'shliqlar (mt-auto — flex ichida elementni pastga suradi)."),
        ("opacity-90", "Elementni 90% shaffoflikda (biroz shaffof) ko'rsatadi."),
        ("p-8 / px-3 / px-6 / py-1 / py-4", "Ichki bo'shliqlar, raqam × 0.25rem."),
        ("rounded-lg / rounded-2xl", "Burchaklarni yumaloqlash darajasi (2xl — kattaroq radius)."),
        ("shadow / shadow-sm", "Standart va yengil soya effektlari."),
        ("text-lg / text-xl", "Standart shkaladan kattaroq matn o'lchami darajalari."),
    ],
    527: [
        ("group-hover: / peer-*:", "group-hover — ota elementga hover qilinganda ichidagi bolaga ta'sir qiladi (ota elementda `group` klassi bo'lishi shart); peer-* — 'birodar' elementning holatiga qarab boshqa elementga ta'sir qiladi (undan oldingi elementda `peer` klassi bo'lishi shart)."),
        ("[...] (kvadrat qavs)", "Shkaladan tashqari, ixtiyoriy (arbitrary) qiymat, masalan h-[73px] yoki bg-[#4f46e5]."),
        ("active:bg-indigo-800 / active:scale-95", "Bosilgan (active) paytda fon yoki o'lcham o'zgaradi."),
        ("bg-[#4f46e5]", "Ixtiyoriy fon rangi — aniq HEX qiymat."),
        ("border / border-slate-300", "Standart chegara qalinligi va rangi."),
        ("dark:bg-slate-700/800, dark:border-slate-600, dark:text-slate-100/400", "Qorong'i rejimda qo'llanadigan fon/chegara/matn ranglari."),
        ("dark:group-hover:text-indigo-400", "Qorong'i rejimda, ota elementga hover qilinganda matn rangi o'zgaradi (uchta prefiks birga)."),
        ("dark:hover:bg-slate-600", "Qorong'i rejimda hover holatidagi fon rangi."),
        ("dark:shadow-slate-950", "Qorong'i rejimda soya rangi."),
        ("disabled:cursor-not-allowed", "Element o'chirilgan (disabled) bo'lsa, kursor \"taqiqlangan\" belgisiga aylanadi."),
        ("focus-visible:outline / outline-2 / outline-indigo-500", "Klaviatura bilan fokus qilinganda ko'rinadigan konturning yoqilishi, qalinligi va rangi."),
        ("focus:border-indigo-500", "Input fokusda bo'lganda chegara rangi."),
        ("group-hover:text-indigo-600 / translate-x-1", "Ota elementga hover qilinganda, ichidagi bolaning rangi yoki joyi o'zgaradi."),
        ("h-[73px] / rounded-[14px]", "Ixtiyoriy (arbitrary) piksel qiymatlar."),
        ("hover:bg-slate-300 / hover:shadow-lg", "Hover holatidagi fon va soya."),
        ("inline-block", "Elementni inline-block qiladi."),
        ("invalid:border-rose-500", "Input noto'g'ri (invalid) to'ldirilsa, chegara rangi qizil-pushti bo'ladi."),
        ("mt-1 / mt-2 / mt-8", "Yuqoridan tashqi bo'shliqlar."),
        ("peer-placeholder-shown:hidden", "\"Birodar\" input hali bo'sh (placeholder ko'rinib turibdi) bo'lsa, bu element yashiriladi."),
        ("rounded", "Standart burchak yumaloqligi."),
        ("sm:w-auto", "sm ekrandan boshlab kenglik avtomatik (kontentga mos) bo'ladi."),
        ("space-y-4", "Bolalar elementlar orasiga vertikal bo'shliq qo'yadi."),
        ("text-rose-600 / text-slate-900", "Rang oilasi bo'yicha matn ranglari."),
        ("transition-transform", "Transform (scale, translate) o'zgarishlarini silliq animatsiya qiladi."),
    ],
    529: [
        ("rang/raqam (masalan bg-white/70)", "Rang nomidan keyingi \"/raqam\" shaffoflik foizini bildiradi (bg-white/70 — 70% xiralik oq fon)."),
        ("manfiy qiymat (masalan -top-3, -translate-x-1/2)", "Elementni ko'rsatilgan yo'nalishning teskarisiga suradi — odatda markazlash yoki chetga \"osib qo'yish\" uchun."),
        ("-top-3", "Elementni yuqoriga 0.75rem suradi — badge/etiketkani chetga osib qo'yish uchun."),
        ("-translate-x-1/2 + left-1/2", "Klassik markazlash usuli: elementni chapdan 50% ga suradi, so'ng o'z kengligining yarmicha orqaga qaytaradi."),
        ("backdrop-blur-md", "Element ortasidagi fonni xiralashtiradi (shisha effekti)."),
        ("bg-emerald-100 / bg-indigo-100 / bg-pink-100", "Och rangli fon ranglari (100-soya)."),
        ("border-2", "2px qalinlikdagi chegara."),
        ("border-b / border-t", "Faqat pastki yoki yuqori chegara chizig'i."),
        ("border-indigo-500 / border-slate-200", "Chegara ranglari."),
        ("dark:bg-emerald-900/50 va shunga o'xshashlar", "Qorong'i rejimda, 50% shaffoflikdagi to'q fon ranglari."),
        ("dark:from-indigo-900/40, dark:to-pink-900/30", "Qorong'i rejimdagi gradient ranglari (shaffoflik bilan)."),
        ("font-extrabold / font-medium / font-normal", "Shrift qalinligi darajalari."),
        ("gap-4", "Grid/flex elementlar orasidagi bo'shliq, 1rem."),
        ("h-6 / h-12 / w-6 / w-12", "Qattiq belgilangan o'lchamlar."),
        ("hover:shadow-xl", "Hover holatida kattaroq soya."),
        ("inset-0", "Elementni ota elementning barcha tomoniga (yuqori-past-chap-o'ng — hammasi 0) yopishtiradi."),
        ("max-w-2xl / max-w-5xl / max-w-7xl", "Maksimal kenglik chegaralari (2xl eng kichik, 7xl eng katta)."),
        ("mb-1 / mb-3 / mb-6 / mb-10 / mb-16", "Pastdan tashqi bo'shliqlar, raqam kattalashgan sayin bo'shliq oshadi."),
        ("md:grid-cols-3 / md:grid-cols-4", "md ekrandan boshlab grid 3 yoki 4 ustunli bo'ladi."),
        ("md:py-32 / md:scale-105 / md:text-4xl/6xl/xl", "md ekrandan boshlab qo'llanadigan bo'shliq, kattalashtirish va matn o'lchami."),
        ("mx-auto / my-6", "Gorizontal markazlash (chap-o'ng avtomatik) va vertikal tashqi bo'shliq."),
        ("overflow-hidden", "Konteynerdan tashqariga chiqqan kontentni yashiradi."),
        ("px-8 / py-3 / py-12", "Ichki bo'shliqlar."),
        ("rounded-full", "To'liq yumaloq (doira/oval) burchak."),
        ("scroll-smooth", "Sahifa ichida silliq skroll animatsiyasini yoqadi."),
        ("shadow-2xl", "Eng katta soya darajasi."),
        ("shadow-indigo-500/20", "Indigo rangli, 20% shaffoflikdagi soya."),
        ("sm:flex-row", "sm ekrandan boshlab flex elementlar gorizontal qatorga joylanadi."),
        ("space-y-2 / space-y-3", "Bolalar elementlar orasiga vertikal bo'shliq."),
        ("text-3xl / text-4xl / text-base / text-xs", "Matn o'lchami darajalari."),
        ("text-center", "Matnni markazga tekislaydi."),
        ("text-emerald-600 / text-indigo-700 / text-pink-600", "Rang oilalari bo'yicha matn ranglari."),
        ("to-pink-500/20", "Gradientning tugash rangi, 20% shaffoflikda."),
        ("tracking-tight", "Harflar orasidagi bo'shliqni (letter-spacing) qisqartiradi."),
        ("via-purple-500/10", "Uch rangli gradientning o'rta rangi, 10% shaffoflikda."),
    ],
}


def build_html(lesson_id: int, entries: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"  <li><code>{cls}</code> — {desc}</li>" for cls, desc in entries
    )
    intro = SYSTEM_INTRO_UZ + "\n" if lesson_id == 525 else ""
    return (
        f"<h3>{MARKER}</h3>\n"
        f"{intro}"
        f"<p>Yuqoridagi namunada ishlatilgan, lekin hali alohida tushuntirilmagan klasslar:</p>\n"
        f"<ul>\n{items}\n</ul>"
    )


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, entries in GLOSSARY.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()
            if MARKER in (lesson.text_content or ""):
                print(f"lesson {lesson_id}: glossary already present, skipping")
                continue
            await append_bug_marker(db, lesson_id, build_html(lesson_id, entries))
            print(f"lesson {lesson_id}: appended glossary ({len(entries)} entries)")
        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
