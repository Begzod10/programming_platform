"""Enhance course 30 (Python Asoslari, beginner) from ~2 to 4-5 star ambition.

Adds a real "🐛 Ataylab xato" gotcha to 8 of 14 lessons plus one reasoning
exercise (output-prediction style, matching course 37's pattern) per lesson.
Idempotent — checks for the marker/title before writing.
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
from app.models.exercise import Exercise  # noqa: E402
from enhance_lesson_helpers import append_bug_marker, add_exercise, sync_exercise_section  # noqa: E402

MARKER = "🐛 Ataylab xato"

BUGS = {
    219: {  # O'zgaruvchilar va turlar — float equality
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi shunday tekshiruv yozadi:</p>
<pre><code class="lang-python">narx1 = 0.1
narx2 = 0.2
jami = narx1 + narx2
print(jami == 0.3)</code></pre>
<p><strong>Natija:</strong> <code>False</code>! Garchi <code>0.1 + 0.2</code> "matematik jihatdan" <code>0.3</code>ga teng ko'ringan bo'lsa ham. Sabab: kompyuter <code>float</code> sonlarni ikkilik (binary) sanoq tizimida saqlaydi, va <code>0.1</code> kabi sonlarni <strong>aniq</strong> ifodalab bo'lmaydi (xuddi <code>1/3</code>ni o'nlik kasrda aniq yozib bo'lmagani kabi). Haqiqatda <code>0.1 + 0.2 = 0.30000000000000004</code>.</p>
<p><strong>To'g'ri yechim:</strong> Float sonlarni to'g'ridan-to'g'ri <code>==</code> bilan solishtirmang. Buning o'rniga farqning juda kichikligini tekshiring: <code>abs(jami - 0.3) &lt; 1e-9</code>.</p>""",
        "exercise": {
            "title": "print(0.1 + 0.2 == 0.3) nima chiqaradi?",
            "description": "Quyidagi kod nima natija beradi deb o'ylaysiz?\n`print(0.1 + 0.2 == 0.3)`",
            "exercise_type": "multiple_choice",
            "options": '["True", "False", "SyntaxError", "0.3"]',
            "correct_answers": "B",
            "hint": "Kompyuter float sonlarni qanday sanoq tizimida saqlaydi — o'nlikmi, ikkilikmi?",
            "explanation": "Float sonlar IEEE 754 ikkilik formatda saqlanadi, va 0.1 kabi o'nlik kasrlarni bu formatda aniq ifodalab bo'lmaydi. 0.1 + 0.2 aslida 0.30000000000000004 ga teng, shuning uchun == 0.3 False qaytaradi.",
        },
    },
    220: {  # Stringlar bilan ishlash — immutability
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi stringning bitta harfini "tuzatmoqchi" bo'ladi:</p>
<pre><code class="lang-python">ism = "Alimjon"
ism[0] = "S"
print(ism)</code></pre>
<p><strong>Natija:</strong> <code>TypeError: 'str' object does not support item assignment</code>. Python'da stringlar <strong>o'zgarmas (immutable)</strong> — ular yaratilgandan keyin hech qanday indeks orqali o'zgartirib bo'lmaydi (ro'yxatlardan farqli o'laroq).</p>
<p><strong>To'g'ri yechim:</strong> Yangi string yaratish kerak: <code>ism = "S" + ism[1:]</code> yoki <code>ism = ism.replace("A", "S", 1)</code>.</p>""",
        "exercise": {
            "title": "ism = \"Alimjon\"; ism[0] = \"S\" kodini ishga tushirsak nima bo'ladi?",
            "description": "Quyidagi kod ishga tushirilsa nima natija beradi?\n`ism = \"Alimjon\"`\n`ism[0] = \"S\"`",
            "exercise_type": "multiple_choice",
            "options": '["ism o\'zgarib \"Slimjon\" bo\'ladi", "TypeError: \'str\' object does not support item assignment", "Hech narsa o\'zgarmaydi, sokin ishlayveradi", "IndexError chiqadi"]',
            "correct_answers": "B",
            "hint": "Python'da stringlar ro'yxat (list) kabi o'zgaruvchanmi?",
            "explanation": "Stringlar Python'da immutable (o'zgarmas) tur hisoblanadi. Indeks orqali element o'zgartirishga urinish TypeError beradi. Yangi qiymat kerak bo'lsa, butunlay yangi string yaratiladi.",
        },
    },
    222: {  # Shartli ifodalar — 0 is falsy trap
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi ball kiritilgan-kiritilmaganini shunday tekshiradi:</p>
<pre><code class="lang-python">def natija_korsat(ball):
    if ball:
        print(f"Sizning balingiz: {{ball}}")
    else:
        print("Ball kiritilmagan!")

natija_korsat(0)</code></pre>
<p><strong>Natija:</strong> <code>"Ball kiritilmagan!"</code> chiqadi — garchi <code>0</code> aslida <strong>haqiqiy, to'g'ri qiymat</strong> bo'lsa ham (masalan, talaba haqiqatan ham 0 ball olgan bo'lishi mumkin)! Sabab: Python'da <code>if qiymat:</code> yozilganda, <code>0</code>, <code>0.0</code>, <code>""</code>, <code>[]</code>, <code>None</code>, <code>False</code> — barchasi "falsy" (yolg'on) deb hisoblanadi. Dastur "ball kiritilmagan" (<code>None</code>) bilan "ball nolga teng" (<code>0</code>) holatlarini <strong>farqlay olmaydi</strong>.</p>
<p><strong>To'g'ri yechim:</strong> Aniq <code>None</code> tekshiruvi kerak: <code>if ball is not None:</code>.</p>""",
        "exercise": {
            "title": "natija_korsat(0) chaqirilsa, funksiya nima chop etadi?",
            "description": "def natija_korsat(ball):\n    if ball:\n        print(f\"Sizning balingiz: {ball}\")\n    else:\n        print(\"Ball kiritilmagan!\")\n\nnatija_korsat(0) chaqirilsa, ekranda nima chiqadi va nega bu xato hisoblanadi?",
            "exercise_type": "text_input",
            "expected_answer": "\"Ball kiritilmagan!\" chiqadi, garchi 0 haqiqiy qiymat bo'lsa ham. Sabab: Python'da if ball: yozilganda 0 'falsy' hisoblanadi, xuddi None kabi. Dastur 0 va None ni farqlay olmaydi. To'g'ri yechim: if ball is not None: ishlatish.",
            "hint": "Python'da qanday qiymatlar 'falsy' (yolg'ondek) hisoblanadi?",
            "explanation": "0, 0.0, \"\", [], {}, None, False — barchasi if shartida False sifatida baholanadi. Agar 0 haqiqiy qiymat bo'lishi mumkin bo'lsa, uni None bilan aralashtirmaslik uchun aniq 'is not None' tekshiruvi kerak.",
        },
    },
    224: {  # Ro'yxatlar va kortejlar — mutable default arg
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi ro'yxatga element qo'shadigan funksiya yozadi:</p>
<pre><code class="lang-python">def royxatga_qosh(element, royxat=[]):
    royxat.append(element)
    return royxat

print(royxatga_qosh("olma"))
print(royxatga_qosh("nok"))</code></pre>
<p><strong>Natija:</strong> Kutilgan <code>['nok']</code> o'rniga <strong><code>['olma', 'nok']</code></strong> chiqadi! Sabab: Python'da funksiya <strong>default argumentlari faqat BIR MARTA</strong>, funksiya ta'riflanganda yaratiladi — har bir chaqiruvda emas. Shuning uchun <code>royxat=[]</code> aslida <strong>barcha chaqiruvlar orasida bitta umumiy ro'yxatga</strong> ishora qiladi.</p>
<p><strong>To'g'ri yechim:</strong> Standart qiymat sifatida hech qachon mutable (o'zgaruvchan) obyekt (list, dict) ishlatmang: <code>def royxatga_qosh(element, royxat=None): royxat = royxat or []</code>.</p>""",
        "exercise": {
            "title": "royxatga_qosh(\"olma\") va royxatga_qosh(\"nok\") ketma-ket chaqirilsa, ikkinchisi nima qaytaradi?",
            "description": "def royxatga_qosh(element, royxat=[]):\n    royxat.append(element)\n    return royxat\n\nroyxatga_qosh(\"olma\") va keyin royxatga_qosh(\"nok\") chaqirilsa, ikkinchi chaqiruv nima qaytaradi?",
            "exercise_type": "multiple_choice",
            "options": '["[\'nok\']", "[\'olma\', \'nok\']", "[\'olma\']", "TypeError chiqadi"]',
            "correct_answers": "B",
            "hint": "Python funksiya default argumentlarini qachon yaratadi — har chaqiruvdami, yoki funksiya ta'riflanganda bir martami?",
            "explanation": "Mutable default argument (masalan bo'sh list) funksiya ta'riflanganda FAQAT BIR MARTA yaratiladi va barcha keyingi chaqiruvlar xuddi shu obyektga ishora qiladi. Shuning uchun avvalgi chaqiruvdagi o'zgarishlar saqlanib qoladi.",
        },
    },
    226: {  # Funksiyalar — closures late binding
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi sikl ichida bir nechta funksiya (lambda) yaratadi:</p>
<pre><code class="lang-python">funksiyalar = []
for i in range(3):
    funksiyalar.append(lambda: i)

print([f() for f in funksiyalar])</code></pre>
<p><strong>Natija:</strong> Kutilgan <code>[0, 1, 2]</code> o'rniga <strong><code>[2, 2, 2]</code></strong> chiqadi! Sabab: lambda funksiyasi <code>i</code>ning yaratilgan paytdagi <strong>qiymatini emas</strong>, balki <code>i</code> nomli <strong>o'zgaruvchiga ishorani</strong> "eslab qoladi" (bu "late binding" — kech bog'lanish deyiladi). Sikl tugagach <code>i</code>ning oxirgi qiymati — <code>2</code> — barcha lambda'lar tomonidan qaytariladi.</p>
<p><strong>To'g'ri yechim:</strong> <code>i</code>ning joriy qiymatini default argument sifatida "qulflab qo'yish": <code>lambda i=i: i</code>.</p>""",
        "exercise": {
            "title": "for i in range(3): funksiyalar.append(lambda: i) — [f() for f in funksiyalar] nima qaytaradi?",
            "description": "funksiyalar = []\nfor i in range(3):\n    funksiyalar.append(lambda: i)\n\n[f() for f in funksiyalar] ishga tushirilsa, natija qanday bo'ladi?",
            "exercise_type": "multiple_choice",
            "options": '["[0, 1, 2]", "[2, 2, 2]", "[0, 0, 0]", "TypeError"]',
            "correct_answers": "B",
            "hint": "Lambda o'zgaruvchining qiymatinimi yoki o'ziga ishorani eslab qoladimi?",
            "explanation": "Lambda closure orqali o'zgaruvchi i ga ISHORANI saqlaydi, uning sikl paytidagi qiymatini emas. Sikl tugagach i=2 bo'lib qoladi, va barcha lambda'lar chaqirilganda aynan shu oxirgi qiymatni qaytaradi — bu 'late binding closure' muammosi.",
        },
    },
    227: {  # Lug'atlar va to'plamlar — mutate during iteration
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi lug'atdan ma'lum shartga mos kalitlarni o'chirmoqchi bo'ladi:</p>
<pre><code class="lang-python">narxlar = {{"olma": 5000, "nok": 0, "uzum": 12000, "shaftoli": 0}}

for mahsulot in narxlar:
    if narxlar[mahsulot] == 0:
        del narxlar[mahsulot]</code></pre>
<p><strong>Natija:</strong> <code>RuntimeError: dictionary changed size during iteration</code>. Python sikl davomida <code>for</code> iteratori lug'atning <strong>ichki tuzilishiga</strong> tayanadi — siklning o'zi ishlab turgan paytda lug'at o'lchamini o'zgartirish (element qo'shish/o'chirish) taqiqlanadi.</p>
<p><strong>To'g'ri yechim:</strong> Avval o'chiriladigan kalitlar ro'yxatini yig'ib oling, keyin alohida siklda o'chiring: <code>uchun_ochirish = [k for k, v in narxlar.items() if v == 0]</code>, so'ng ularni alohida o'chiring. Yoki <code>narxlar.copy()</code> ustida iteratsiya qiling.</p>""",
        "exercise": {
            "title": "Lug'at ustida for bilan iteratsiya qilib, shu ichida del bilan kalit o'chirilsa nima bo'ladi?",
            "description": "for mahsulot in narxlar:\n    if narxlar[mahsulot] == 0:\n        del narxlar[mahsulot]\n\nBu kod ishga tushirilsa nima natija beradi, va nega?",
            "exercise_type": "text_input",
            "expected_answer": "RuntimeError: dictionary changed size during iteration xatosi chiqadi. Python for sikli lug'at ustida ishlayotganda uning ichki tuzilishiga tayanadi, shu sikl davomida lug'atga element qo'shish yoki o'chirish taqiqlangan. Yechim: avval o'chiriladigan kalitlarni alohida ro'yxatga yig'ib, keyin ularni alohida siklda o'chirish, yoki narxlar.copy() ustida iteratsiya qilish.",
            "hint": "Sikl ishlab turgan paytda ustida yurayotgan kolleksiyaning o'lchamini o'zgartirish mumkinmi?",
            "explanation": "Python ichki iteratorlar kolleksiya o'lchami sikl davomida o'zgarmasligiga tayanadi. O'zgarsa, RuntimeError chiqaradi — bu xato ma'lumot yo'qolishining oldini olish uchun qasddan qilingan.",
        },
    },
    230: {  # Klasslar va obyektlar (OOP) — shared class attribute
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi har bir talabaning baholari ro'yxatini shunday yaratadi:</p>
<pre><code class="lang-python">class Talaba:
    baholar = []   # klass darajasidagi atribut!

    def __init__(self, ism):
        self.ism = ism

ali = Talaba("Ali")
vali = Talaba("Vali")

ali.baholar.append(5)
print(vali.baholar)</code></pre>
<p><strong>Natija:</strong> <code>[5]</code> — Valining baholar ro'yxatida ham Alining bahosi bor! Sabab: <code>baholar = []</code> <strong>klass darajasida</strong> yozilgan, ya'ni u <code>__init__</code> ichida emas — bu barcha <code>Talaba</code> obyektlari o'rtasida <strong>bitta umumiy</strong> ro'yxatni bildiradi, har bir obyektga alohida emas.</p>
<p><strong>To'g'ri yechim:</strong> Har bir obyektga xos (instance) atributlar <code>__init__</code> ichida <code>self.baholar = []</code> ko'rinishida yaratilishi kerak.</p>""",
        "exercise": {
            "title": "ali.baholar.append(5) qilingandan keyin, nega vali.baholar ham [5] bo'lib qoladi?",
            "description": "class Talaba:\n    baholar = []\n    def __init__(self, ism):\n        self.ism = ism\n\nali = Talaba(\"Ali\"); vali = Talaba(\"Vali\")\nali.baholar.append(5)\nprint(vali.baholar)\n\nNatija nima, va nega?",
            "exercise_type": "multiple_choice",
            "options": '["[] — vali baholari bo\'sh qoladi", "[5] — baholar klass darajasida e\'lon qilingani uchun barcha obyektlar orasida umumiy", "AttributeError chiqadi", "[5, 5] chiqadi"]',
            "correct_answers": "B",
            "hint": "baholar = [] qayerda yozilgan — __init__ ichidami, klass darajasidami? Bu farq nimani anglatadi?",
            "explanation": "Klass darajasidagi atribut (__init__ tashqarisida yozilgan) barcha instance'lar orasida umumiy bo'ladi — u faqat bitta marta, klass yaratilganda hosil bo'ladi. Har bir obyektga alohida ro'yxat kerak bo'lsa, uni __init__ ichida self.baholar = [] deb yaratish shart.",
        },
    },
    231: {  # Fayllar va xatolar — bare except
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi xatolarni "chiroyli" ushlash uchun shunday yozadi:</p>
<pre><code class="lang-python">try:
    fayl = open("malumot.txt")
    son = int(fayl.read())
    natija = 100 / son
except:
    print("Xatolik yuz berdi")</code></pre>
<p><strong>Natija:</strong> Dastur ishlaydi, lekin <strong>qaysi xato</strong> yuz berganini hech qachon bilib bo'lmaydi — fayl topilmadimi (<code>FileNotFoundError</code>), son formatida xato bormi (<code>ValueError</code>), nolga bo'lish bormi (<code>ZeroDivisionError</code>)? Yalang'och <code>except:</code> <strong>barcha</strong> istisnolarni, hatto <code>KeyboardInterrupt</code> (Ctrl+C) va dasturchining o'zi qilgan mantiqiy xatolarini ham "yutib yuboradi" — bu debugging'ni deyarli imkonsiz qiladi.</p>
<p><strong>To'g'ri yechim:</strong> Har doim <strong>aniq</strong> istisno turlarini ko'rsating: <code>except FileNotFoundError:</code>, <code>except ValueError:</code>, <code>except ZeroDivisionError:</code> — har biriga mos xabar bilan.</p>""",
        "exercise": {
            "title": "Yalang'och except: nima uchun xavfli hisoblanadi?",
            "description": "try:\n    ...\nexcept:\n    print(\"Xatolik yuz berdi\")\n\nBu kod ishlaydi, lekin nega professional kodda tavsiya etilmaydi?",
            "exercise_type": "text_input",
            "expected_answer": "Yalang'och except: barcha turdagi istisnolarni (hatto KeyboardInterrupt, SystemExit va dasturchining o'z xatolarini ham) ushlab qoladi, qaysi xato yuz berganini bilib bo'lmaydi va debugging qiyinlashadi. To'g'ri yondashuv: har bir aniq istisno turini alohida except bloki bilan ushlash (masalan except ValueError:, except FileNotFoundError:).",
            "hint": "except: (turini ko'rsatmasdan) qancha turdagi xatoni ushlaydi — faqat kutilganlariniмі, hammasinimi?",
            "explanation": "Yalang'och except barcha Exception (va hatto BaseException) turlarini ushlaydi, shu jumladan dasturchi bilishi kerak bo'lgan haqiqiy xatolarni ham yashiradi. Bu xatoni 'yashirish' orqali muammoni kelajakda topishni qiyinlashtiradi.",
        },
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, spec in BUGS.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()
            if MARKER in (lesson.text_content or ""):
                print(f"lesson {lesson_id}: bug marker already present, skipping content append")
            else:
                await append_bug_marker(db, lesson_id, spec["html"])
                print(f"lesson {lesson_id}: appended bug marker")

            ex_spec = spec["exercise"]
            already = (await db.execute(
                select(Exercise).where(Exercise.lesson_id == lesson_id,
                                        Exercise.title == ex_spec["title"])
            )).scalar_one_or_none()
            if already is None:
                await add_exercise(
                    db, lesson_id,
                    title=ex_spec["title"], description=ex_spec["description"],
                    exercise_type=ex_spec["exercise_type"], options=ex_spec.get("options"),
                    correct_answers=ex_spec.get("correct_answers"),
                    expected_answer=ex_spec.get("expected_answer"),
                    hint=ex_spec["hint"], explanation=ex_spec["explanation"],
                    difficulty_level="Medium", points=4,
                )
                print(f"lesson {lesson_id}: added exercise")
            else:
                print(f"lesson {lesson_id}: exercise already present, skipping insert")
            await sync_exercise_section(db, lesson_id)
            print(f"lesson {lesson_id}: synced exercise section")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
