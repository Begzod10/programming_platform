"""Add a class-name glossary to each Bootstrap lesson's demo code.

Every lesson's showcase HTML uses far more Bootstrap classes than the
lesson's own text/exercises ever explain (confirmed by scanning code
sections against prose+exercise content per lesson). A student who has
only seen the classes taught so far in the course has no way to look up
what e.g. `list-group-flush` or `offset-md-1` does. This appends a short
glossary covering exactly the classes that appear in each lesson's code
demo and aren't already explained earlier in the course.

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

GLOSSARY = {
    514: [
        ("align-items-center", "Flex konteyner ichidagi elementlarni vertikal markazga tekislaydi."),
        ("bg-light", "Och kulrang fon rangi beradi."),
        ("bg-white", "Oq fon rangi beradi."),
        ("col-lg-9", "lg ekranda (≥992px) 12 ustundan 9 tasini egallaydi."),
        ("col-md-10", "md ekranda (≥768px) 12 ustundan 10 tasini egallaydi."),
        ("col-md-3", "md ekranda 12 ustundan 3 tasini egallaydi."),
        ("col-md-9", "md ekranda 12 ustundan 9 tasini egallaydi."),
        ("col-sm-6", "sm ekranda (≥576px) 12 ustundan 6 tasini egallaydi."),
        ("fs-5", "Matn o'lchamini (font-size) 5-darajaga o'rnatadi (1 dan 6 gacha, raqam oshgani sayin kichrayadi)."),
        ("fw-bold", "Matnni qalin (bold) qiladi."),
        ("list-unstyled", "<ul>/<ol> dagi standart belgilar va chekinishni olib tashlaydi."),
        ("mb-4", "Pastdan tashqi bo'shliq (margin-bottom), 4-daraja (Bootstrap spacing shkalasi 0-5)."),
        ("mt-3", "Yuqoridan tashqi bo'shliq, 3-daraja."),
        ("offset-md-1", "md ekranda ustunni chapdan 1 ustunlik bo'sh joyga suradi."),
        ("py-3", "Yuqori-past ichki bo'shliq (padding), 3-daraja."),
        ("shadow-sm", "Yengil (kichik) soya effekti qo'shadi."),
        ("text-end", "Matnni o'ngga tekislaydi."),
    ],
    515: [
        ("active", "Elementni \"faol/tanlangan\" holatda ko'rsatuvchi klass (masalan navigatsiyada joriy sahifa)."),
        ("alert-success", "Yashil rangli \"muvaffaqiyat\" xabar qutisi."),
        ("bg-danger", "Qizil fon rangi (xato/xavf uchun)."),
        ("bg-success", "Yashil fon rangi (muvaffaqiyat uchun)."),
        ("bg-warning", "Sariq fon rangi (ogohlantirish uchun)."),
        ("btn-outline-secondary", "Fonsiz, kulrang chegarali tugma."),
        ("d-flex", "Elementni flex konteyner qiladi (display: flex)."),
        ("fade", "CSS o'tish (transition) effektini yoqadi, odatda .show bilan birga ishlaydi."),
        ("justify-content-between", "Flex elementlar orasiga teng bo'shliq qo'yib, chekkalarga tekislaydi."),
        ("list-group-flush", "Ro'yxat elementlaridan chekka chiziq va burchaklarni olib tashlaydi (kartaga yopishgan ko'rinish uchun)."),
        ("ms-auto", "Chapdan avtomatik bo'shliq — flex ichida elementni o'ngga suradi."),
        ("mt-2", "Yuqoridan tashqi bo'shliq, 2-daraja."),
        ("my-4", "Yuqori-past tashqi bo'shliq, 4-daraja."),
        ("nav-item", "Navigatsiya ro'yxatidagi bitta element konteyneri."),
        ("nav-link", "Navigatsiya ichidagi bosiladigan havola."),
        ("navbar-brand", "Navbardagi logotip/sayt nomi uchun klass."),
        ("navbar-nav", "Navbar ichidagi navigatsiya ro'yxati konteyneri."),
        ("navbar-toggler-icon", "Mobil \"gamburger\" tugmasi ichidagi ikonka."),
        ("show", "Elementni ko'rinadigan holatga o'tkazadi (collapse/modal/fade bilan birga)."),
        ("text-center", "Matnni markazga tekislaydi."),
        ("text-dark", "Matn rangini to'q (deyarli qora) qiladi."),
        ("text-primary", "Matn rangini asosiy brend rangiga (ko'k) bo'yaydi."),
    ],
    516: [
        ("btn-secondary", "Kulrang, ikkinchi darajali tugma."),
        ("form-check-label", "Checkbox/radio yonidagi matn yorlig'i."),
        ("form-label", "Input maydoni ustidagi yorliq matni."),
        ("has-validation", "Input-group ichida validatsiya xabari to'g'ri joylashishi uchun kerakli yordamchi klass."),
        ("mb-3", "Pastdan tashqi bo'shliq, 3-daraja."),
        ("modal-title", "Modal oynaning sarlavha matni uchun klass."),
    ],
    517: [
        ("align-items-start", "Flex elementlarni yuqori chetga tekislaydi."),
        ("border-bottom", "Pastki chegara chizig'ini qo'shadi."),
        ("btn-dark", "Qora rangli tugma."),
        ("btn-lg", "Tugmani kattaroq qiladi."),
        ("btn-outline-primary", "Fonsiz, asosiy rang chegarali tugma."),
        ("flex-grow-1", "Flex elementga bo'sh joyni to'liq egallab o'sish imkonini beradi."),
        ("flex-md-row", "md ekrandan boshlab flex elementlarni gorizontal qatorga joylaydi."),
        ("fs-2 / fs-3 / fs-4", "Turli matn o'lchami darajalari (raqam kichraysa, matn kattalashadi)."),
        ("fs-md-1", "md ekrandan boshlab eng katta matn o'lchami darajasi qo'llanadi."),
        ("m-0", "Barcha tomondan tashqi bo'shliqni olib tashlaydi."),
        ("mb-2", "Pastdan tashqi bo'shliq, 2-daraja."),
        ("mt-5", "Yuqoridan tashqi bo'shliq, eng katta (5) daraja."),
        ("px-5", "Chap-o'ng ichki bo'shliq, 5-daraja."),
        ("py-5", "Yuqori-past ichki bo'shliq, 5-daraja."),
        ("py-md-6", "md ekrandan boshlab yuqori-past ichki bo'shliq, 6-daraja (kengaytirilgan shkala)."),
        ("small", "Matnni kichikroq qiladi (<small> tegiga mos uslub)."),
        ("text-white", "Matn rangini oq qiladi."),
    ],
    518: [
        ("align-middle", "Jadval katagi ichidagi kontentni vertikal markazga tekislaydi."),
        ("bi-speedometer2", "Bootstrap Icons kutubxonasidagi \"spidometr\" ikonkasi klassi."),
        ("border-0", "Barcha chegara chiziqlarini olib tashlaydi."),
        ("btn-close-white", "Yopish (×) tugmasini to'q fonlar uchun oq rangga o'zgartiradi."),
        ("col-lg-10 / col-lg-2", "lg ekranda mos ravishda 10 va 2 ustunni egallaydi."),
        ("h5", "<h5> sarlavha uslubini istalgan tegga qo'llaydi."),
        ("m-auto", "Barcha tomondan avtomatik bo'shliq — elementni markazlashtiradi."),
        ("mb-0", "Pastki tashqi bo'shliqni 0 ga o'rnatadi."),
        ("me-2", "O'ngdan tashqi bo'shliq, 2-daraja."),
        ("min-vh-100", "Minimal balandlikni butun ekran balandligiga (100vh) o'rnatadi."),
        ("navbar-light", "Och rangli fonlar uchun to'q matnli navbar rang sxemasi."),
        ("p-0", "Barcha tomondan ichki bo'shliqni olib tashlaydi."),
        ("toast", "Qisqa vaqtli bildirishnoma (\"toast\") konteyneri."),
        ("toast-body", "Toast bildirishnoma ichidagi asosiy matn qismi."),
    ],
}


def build_html(entries: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f"  <li><code>{cls}</code> — {desc}</li>" for cls, desc in entries
    )
    return (
        f"<h3>{MARKER}</h3>\n"
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
            await append_bug_marker(db, lesson_id, build_html(entries))
            print(f"lesson {lesson_id}: appended glossary ({len(entries)} classes)")
        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
