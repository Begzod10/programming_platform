# Kurs kontenti: sifat standarti (UZ + RU)

Yangi kurs yoki dars **spec fayli** (`backend/scripts/course_specs/<nom>.py`) orqali yoziladi va `build_course.py` bilan kiritiladi.
Qo'lda o'qituvchi paneli orqali o'zgartirmang: UZ va RU birga yangilanishi uchun spec fayli yagona manba.

```bash
cd backend
python scripts/build_course.py course_specs/<nom>.py --dry-run   # lint + shakl, bazaga tegmaydi
python scripts/build_course.py course_specs/<nom>.py             # kursni yashirin (is_published=False) yaratadi
# keyin: servisni qayta ishga tushiring YOKI  POST /api/v1/admin/translations/reload  (o'qituvchi tokeni)
```

Kurs avtomatik nashr qilinmaydi: o'qituvchi sifatida UZ va RU ni ko'rib chiqing, keyin `is_published=True` qiling.

## Bir dars nimadan iborat
1. **Nazariya** (`text_content` / `text_content_ru`): kamida 300 belgi, qisqa, misolga tayangan. Kerak bo'lsa Mermaid diagramma.
2. **Kod misoli** (`<pre><code>`): ikki tilda **aynan bir xil** (faqat izohlar farq qilishi mumkin).
3. **5 ta mashq, kamida 3 xil tur** (test, tartiblash, bo'sh joy, erkin javob). Har birida:
   - `hint` (UZ + `hint_ru`): javobni aytmasdan yo'naltiradi;
   - `explanation` (faqat UZ): nima uchun shunday ekanini tushuntiradi. Bu AI baholash konteksti, RU ga tarjima qilinmaydi.
4. **Mini-loyiha** faqat takrorlash/yakuniy darsda (`task`): sarlavha, tavsif, talablar (UZ+RU), `task_technologies`, `task_deadline_days`.
   Talablar **shu kursgacha o'tilgan** mavzularga tayanadi: o'tilmagan texnologiyani talab qilmang (lint ogohlantiradi).

## Mashq turlari
| Tur | Qoidalar |
|---|---|
| `multiple_choice` | 2+ variant, `correct_answers` harf ("A" yoki "A,C"), `options_ru` uzunligi `options` bilan teng |
| `drag_and_drop` | `correct_order` — `drag_items` ning o'rin almashtirishi, `drag_items_ru` uzunligi teng |
| `fill_in_blank` | tavsifda aynan bitta `___`, `correct_answers` bo'sh emas. Javob tire bilan boshlansa (`-a`, `-v`, `--from`), builder uni tabiiy til deb hisoblaydi: `correct_answers_ru` ni xuddi shu qiymat bilan bering (lint buni tekshiradi) |
| `text_input` | `expected_answer` — AI baholash mezoni (qat'iy mos kelish emas) |

## RU yozish qoidalari
- Tabiiy rus tili, so'zma-so'z tarjima emas; kod, buyruq, fayl nomlari, jadval/ustun nomlari **o'zgarmaydi**.
- Atamalar `course_builder/glossary.py` dagi lug'atdan: `эндпоинт`, `токен`, `бэкенд`, `фронтенд`, `деплой`, `коммит`, `ветка`, ...
  Taqiqlangan variantlar (masalan "конечная точка", "бекенд") lint xatosi beradi.
- RU matni UZ bilan bir xil bo'lmasligi va kirill harfi bo'lishi kerak (qisqa kod tokenlari istisno).

## Lint nimalarni to'xtatadi
**Xato (build to'xtaydi):** RU juftlik yo'q/bo'sh/bir xil/kirillsiz; mashqda `hint` yoki `explanation` yo'q; mashq shakli noto'g'ri;
dars 5 mashqdan kam yoki 3 turdan kam; topshiriq maydonlari to'liq emas; lug'atga zid atama.
**Ogohlantirish (build davom etadi):** UZ va RU kod bloklari farq qiladi; talablarda dars matnida yo'q texnologiya bor.

Eski speclarni qayta yurgizish kerak bo'lsa: `--no-lint` (faqat eski speclar uchun).
