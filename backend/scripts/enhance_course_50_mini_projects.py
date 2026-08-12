"""Enhance course 50 (HTML/CSS Mini-Projects) from ~2 to 4-5 star ambition.

Correction to the original plan: this course's lessons are NOT near-empty —
the flat text_content column is thin, but the real content (explanation +
full working code demo + project task) lives in sections_json and is
already solid. The actual gap is the same one fixed in courses 9/21/30/56:
no "🐛 Ataylab xato" gotcha and pure-recall exercises. This script applies
the same lightweight enhancement to all 13 lessons instead of a ground-up
rewrite.
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
    480: {  # HTML Jadvallar
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi jadval yasaydi, lekin <code>border-collapse</code>ni unutadi:</p>
<pre><code class="lang-css">table, th, td {{ border: 1px solid black; }}</code></pre>
<p><strong>Natija:</strong> Jadvalda chegaralar <strong>ikki qatlam bo'lib</strong> ko'rinadi (har bir katakcha o'z chegarasini alohida chizadi, ular orasida bo'shliq qoladi) — kutilgan yagona chiziqlar o'rniga g'alati "qo'sh chiziq" effekti hosil bo'ladi.</p>
<p><strong>To'g'ri yechim:</strong> <code>table {{ border-collapse: collapse; }}</code> qo'shish — bu qo'shni katakchalarning chegaralarini <strong>bitta chiziqqa</strong> birlashtiradi.</p>""",
        "exercise": {
            "title": "border-collapse: collapse yozilmasa, jadval chegaralari nega qo'sh chiziq bo'lib ko'rinadi?",
            "description": "table, th, td { border: 1px solid black; } yozilgan, lekin border-collapse ishlatilmagan. Jadvalda nega chiziqlar ikki qatlam bo'lib chiqadi?",
            "exercise_type": "text_input",
            "expected_answer": "Standart holatda har bir katakcha (th/td) o'z chegarasini alohida chizadi, qo'shni katakchalar orasida ular ikkilanib, bo'shliq bilan ko'rinadi. border-collapse: collapse qo'shni chegaralarni bitta umumiy chiziqqa birlashtiradi.",
            "hint": "Standart holatda har bir katakcha o'z chegarasini alohida chizadimi, yoki qo'shnisi bilan bo'lishadimi?",
            "explanation": "border-collapse: separate (standart qiymat) har bir katakchaga alohida chegara beradi. collapse qiymati qo'shni chegaralarni birlashtirib, professional ko'rinishdagi yagona chiziqlarni hosil qiladi.",
        },
    },
    481: {  # Ro'yxat Dizayni
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi <code>backdrop-filter: blur()</code> qo'shadi, lekin effekt ko'rinmaydi:</p>
<pre><code class="lang-css">.karta {{
  backdrop-filter: blur(10px);
  background-color: white;
}}</code></pre>
<p><strong>Natija:</strong> Hech qanday "muzli oyna" (glassmorphism) effekti ko'rinmaydi — orqa fon oddiy oq rangligicha qoladi! Sabab: <code>backdrop-filter</code> orqadagi kontentni xiralashtiradi, lekin agar elementning o'z foni <strong>butunlay shaffof emas</strong> bo'lsa (bu yerda <code>white</code> — 100% qattiq rang), xiralashgan orqa fon <strong>ko'rinmaydi</strong>, chunki uni ustidan qattiq oq rang bosib turadi.</p>
<p><strong>To'g'ri yechim:</strong> Foni <strong>yarim shaffof</strong> qilish kerak: <code>background-color: rgba(255, 255, 255, 0.3);</code>.</p>""",
        "exercise": {
            "title": "backdrop-filter: blur(10px) qo'yilgan, lekin background-color: white bo'lsa, nega effekt ko'rinmaydi?",
            "description": ".karta { backdrop-filter: blur(10px); background-color: white; } — glassmorphism effekti kutilgan, lekin ekranda oddiy oq karta ko'rinadi. Nega?",
            "exercise_type": "multiple_choice",
            "options": '["backdrop-filter Safari brauzerida ishlamaydi", "background-color butunlay shaffof emasligi uchun xiralashgan orqa fon ustidan qattiq rang bosib turadi", "blur(10px) qiymati juda kichik", "backdrop-filter faqat rasmlar uchun ishlaydi"]',
            "correct_answers": "B",
            "hint": "backdrop-filter NIMANI xiralashtiradi — elementning o'zinimi, ORQASIDAGI narsanimi? Bu ko'rinishi uchun element foni qanday bo'lishi kerak?",
            "explanation": "backdrop-filter faqat elementning ORQASIDAGI kontentni xiralashtiradi. Agar elementning o'z foni to'liq shaffof bo'lmasa (masalan white), xiralashgan fon ko'rinmay, uning ustidan oddiy rang chiqadi. rgba() bilan shaffoflik berish shart.",
        },
    },
    482: {  # Navigatsiya Paneli
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi navigatsiya panelini <code>position: sticky</code> bilan yopishtiradi:</p>
<pre><code class="lang-css">.nav {{ position: sticky; top: 0; }}</code></pre>
<p>Lekin nav ota elementi shunday yozilgan: <code>.header-wrapper {{ overflow: hidden; }}</code></p>
<p><strong>Natija:</strong> Sahifani scroll qilganda nav <strong>yopishmaydi</strong>, oddiy elementdek yuqoriga qarab yo'qolib ketadi! Sabab: <code>position: sticky</code> faqat ota elementlarning hech birida <code>overflow: hidden</code>, <code>auto</code> yoki <code>scroll</code> bo'lmasa ishlaydi — bu xususiyatlar sticky elementning "yopishish doirasi"ni cheklab, uni oddiy elementga aylantiradi.</p>
<p><strong>To'g'ri yechim:</strong> Ota elementlarda <code>overflow</code> xususiyatini olib tashlang, yoki agar u kerak bo'lsa, sticky elementni boshqa (overflow bo'lmagan) konteynerga joylashtiring.</p>""",
        "exercise": {
            "title": ".header-wrapper{overflow:hidden;} bo'lsa, nega ichidagi position:sticky nav ishlamaydi?",
            "description": ".nav{position:sticky; top:0;} yozilgan, lekin uning ota elementida overflow:hidden bor. Scroll qilganda nav yopishmaydi. Nega?",
            "exercise_type": "text_input",
            "expected_answer": "position: sticky faqat ota elementlarning hech birida overflow:hidden/auto/scroll bo'lmasa to'g'ri ishlaydi. Ota elementda overflow:hidden bo'lsa, sticky elementning yopishish doirasi shu ota bilan cheklanib, u sticky bo'lishni to'xtatadi. Yechim: ota elementdan overflow'ni olib tashlash.",
            "hint": "sticky ishlashi uchun ota elementlarning HECH BIRIDA bo'lmasligi kerak bo'lgan bitta CSS xususiyati bor.",
            "explanation": "overflow: hidden/auto/scroll ota elementda bo'lsa, brauzer sticky elementni shu ota ichida 'joylashtirilgan' deb hisoblaydi va uning yopishish doirasini cheklaydi — natijada sticky effekt yo'qoladi.",
        },
    },
    483: {  # Kartochkalar (Cards)
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi kartochkaga soya (shadow) qo'shadi:</p>
<pre><code class="lang-css">.karta {{ box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
.karta-konteyner {{ overflow: hidden; }}</code></pre>
<p><strong>Natija:</strong> Kartochkaning soyasi <strong>qirqilib qoladi</strong> — faqat yuqori va chap tomonlarida ko'rinadi, pastki va o'ng qismlari yo'qoladi! Sabab: <code>box-shadow</code> elementning <strong>chegarasidan tashqariga</strong> chiqadi, lekin ota konteynerda <code>overflow: hidden</code> bo'lsa, undan tashqariga chiqqan har qanday narsa (soya ham) <strong>kesib tashlanadi</strong>.</p>
<p><strong>To'g'ri yechim:</strong> Agar overflow kerak bo'lmasa, uni olib tashlang. Agar boshqa maqsad uchun kerak bo'lsa (masalan rasm qirralarini yumaloqlash uchun), soyani <strong>alohida, tashqi</strong> elementga bering.</p>""",
        "exercise": {
            "title": "karta-konteyner{overflow:hidden} bo'lsa, nega box-shadow to'liq ko'rinmaydi?",
            "description": ".karta{box-shadow: 0 4px 12px rgba(0,0,0,0.2);} ichida joylashgan, ota .karta-konteyner{overflow:hidden;} ga ega. Soya nima uchun to'liq ko'rinmaydi?",
            "exercise_type": "multiple_choice",
            "options": '["box-shadow qiymati noto\'g\'ri yozilgan", "box-shadow element chegarasidan tashqariga chiqadi, overflow:hidden esa undan tashqarisini kesib tashlaydi", "rgba rangi noto\'g\'ri", "box-shadow faqat button elementida ishlaydi"]',
            "correct_answers": "B",
            "hint": "box-shadow elementning ICHIDA chiziladimi, TASHQARISIDAmi? overflow:hidden nimani kesib tashlaydi?",
            "explanation": "box-shadow vizual ravishda elementning chegarasidan tashqariga cho'ziladi. overflow:hidden ota konteynerning chegarasidan tashqariga chiqqan HAR QANDAY narsani (bolalarning o'zi ham, ularning soyasi ham) kesib tashlaydi.",
        },
    },
    484: {  # Flexbox Layout
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi 3 ta turli balandlikdagi kartani flex qatorga joylaydi:</p>
<pre><code class="lang-css">.konteyner {{ display: flex; }}</code></pre>
<p><strong>Natija:</strong> Barcha kartalar — matn miqdoridan qat'iy nazar — <strong>bir xil, eng balandining balandligiga</strong> cho'zilib qoladi, garchi buni hech kim so'ramagan bo'lsa ham! Sabab: flex konteynerning <code>align-items</code> xususiyati standart qiymati <code>stretch</code> — bu barcha flex-elementlarni bir-biriga <strong>tenglashtirib cho'zadi</strong>, agar boshqacha ko'rsatilmasa.</p>
<p><strong>To'g'ri yechim:</strong> Agar kartalar o'z tabiiy balandligida qolishi kerak bo'lsa: <code>align-items: flex-start;</code> berish kerak.</p>""",
        "exercise": {
            "title": "display:flex berilgan konteynerda, nega turli miqdordagi matnli kartalar bir xil balandlikka cho'ziladi?",
            "description": ".konteyner{display:flex;} ichida 3 ta har xil matn uzunlikdagi karta bor. Ular bir xil (eng balandining) balandlikda ko'rinadi. Nega, hech qanday height berilmagan bo'lsa ham?",
            "exercise_type": "text_input",
            "expected_answer": "Flex konteynerning align-items xususiyati standart qiymati stretch — bu barcha flex-elementlarni bir-biriga tenglashtirib, konteynerning balandligiga cho'zadi. Agar bunday xohlanmasa, align-items: flex-start berish kerak.",
            "hint": "align-items xususiyatining standart (default) qiymati nima?",
            "explanation": "align-items: stretch — Flexbox'ning standart holati. U barcha flex-elementlarni cross-axis bo'yicha bir xil o'lchamga cho'zadi, agar ularning o'zida aniq height berilmagan bo'lsa.",
        },
    },
    485: {  # Div Layout (Bugatti)
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi rasm ustiga narx yorlig'ini <code>position: absolute</code> bilan joylashtiradi:</p>
<pre><code class="lang-css">.narx-yorlik {{ position: absolute; top: 10px; right: 10px; }}</code></pre>
<p><strong>Natija:</strong> Yorliq kutilganidek rasm burchagida emas, balki <strong>butun sahifaning yuqori o'ng burchagida</strong> chiqib ketadi! Sabab: <code>position: absolute</code> elementni eng yaqin <strong>positioned</strong> (ya'ni <code>position: relative/absolute/fixed</code> berilgan) ota elementiga nisbatan joylashtiradi. Agar hech qanday ota elementda bunday xususiyat bo'lmasa, u <code>&lt;body&gt;</code>ga nisbatan joylashadi.</p>
<p><strong>To'g'ri yechim:</strong> Rasm konteyneriga <code>position: relative;</code> berish — shunda <code>absolute</code> yorliq aynan shu konteynerga nisbatan joylashadi.</p>""",
        "exercise": {
            "title": ".narx-yorlik{position:absolute} rasm konteyneriga nisbatan emas, butun sahifaga nisbatan joylashib qoladi — nega?",
            "description": "Rasm ustiga narx yorlig'i position:absolute; top:10px; right:10px; bilan qo'yilgan, lekin u rasm burchagida emas, butun sahifa burchagida chiqadi. Sababi nima?",
            "exercise_type": "multiple_choice",
            "options": '["top va right qiymatlari noto\'g\'ri", "absolute element eng yaqin POSITIONED ota elementga nisbatan joylashadi, bunday ota topilmasa body\'ga nisbatan joylashadi", "position:absolute faqat rasm ichida ishlaydi", "z-index yetishmaydi"]',
            "correct_answers": "B",
            "hint": "absolute joylashuv uchun 'nisbat olinadigan' ota element qanday xususiyatga ega bo'lishi kerak?",
            "explanation": "position: absolute elementni eng yaqin 'positioned' (position:relative/absolute/fixed/sticky berilgan) ota elementiga nisbatan joylashtiradi. Bunday ota bo'lmasa, u butun hujjat (body/html)ga nisbatan joylashadi.",
        },
    },
    486: {  # CSS Position — Shaxsiy Kartochka
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi badge (nishonча)ni kartochka ustiga chiqarish uchun <code>z-index</code> beradi:</p>
<pre><code class="lang-css">.badge {{ z-index: 999; top: -10px; right: -10px; }}</code></pre>
<p><strong>Natija:</strong> Badge hamon kartochka ostida "yashiringan" holda qoladi, garchi <code>z-index: 999</code> — juda katta qiymat bo'lsa ham! Sabab: <code>z-index</code> xususiyati <strong>faqat</strong> elementga <code>position</code> qiymati (<code>relative</code>, <code>absolute</code>, <code>fixed</code> yoki <code>sticky</code>) berilgan bo'lsa ishlaydi. <code>position: static</code> (standart qiymat) elementlar uchun <code>z-index</code> hech qanday ta'sir qilmaydi.</p>
<p><strong>To'g'ri yechim:</strong> <code>.badge {{ position: absolute; z-index: 999; ... }}</code> — <code>position</code>ni albatta belgilash kerak.</p>""",
        "exercise": {
            "title": "z-index: 999 berilgan, lekin badge hamon orqada qolib ketadi — nima yetishmayapti?",
            "description": ".badge { z-index: 999; top: -10px; right: -10px; } yozilgan, lekin position xususiyati berilmagan. Badge nega hamon kartochka ostida qoladi?",
            "exercise_type": "fill_in_blank",
            "correct_answers": "position",
            "hint": "z-index qaysi xususiyat berilmagan elementlarga umuman ta'sir qilmaydi?",
            "explanation": "z-index faqat position: static bo'lmagan (ya'ni relative, absolute, fixed yoki sticky berilgan) elementlarga ta'sir qiladi. position berilmasa (standart static holatda), z-index butunlay e'tiborga olinmaydi.",
        },
    },
    487: {  # CSS Position — Ilg'or
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi sahifa yuqorisida doim ko'rinib turadigan tugma yaratadi:</p>
<pre><code class="lang-css">.card-wrapper {{ transform: translateY(0); }}  /* animatsiya uchun */
.tugma {{ position: fixed; top: 20px; right: 20px; }}</code></pre>
<p><strong>Natija:</strong> <code>.tugma</code> sahifa scroll qilinganda ekranga "yopishib qolish" o'rniga, <code>.card-wrapper</code> ichida <strong>oddiy elementdek</strong> harakatlanadi! Sabab: agar ota elementda <code>transform</code> (hattoki <code>translateY(0)</code> kabi "hech narsa qilmaydigan" qiymat bo'lsa ham!) qo'llanilgan bo'lsa, u <strong>yangi containing block</strong> yaratadi — va <code>position: fixed</code> endi viewport'ga emas, aynan shu ota elementga nisbatan hisoblanadi.</p>
<p><strong>To'g'ri yechim:</strong> <code>transform</code>ni fixed elementning ota-bobolaridan olib tashlang, yoki fixed elementni butunlay boshqa (transform'siz) konteynerga chiqaring.</p>""",
        "exercise": {
            "title": "Ota elementda transform: translateY(0) bo'lsa, nega ichidagi position:fixed element ekranga yopishmaydi?",
            "description": ".card-wrapper{transform: translateY(0);} ichida .tugma{position:fixed;} bor. Scroll qilganda tugma ekranga yopishishi kerak edi, lekin u wrapper ichida oddiy elementdek harakatlanadi. Nega?",
            "exercise_type": "text_input",
            "expected_answer": "Ota elementga transform qo'llanilishi (hatto translateY(0) kabi vizual jihatdan hech narsani o'zgartirmaydigan qiymat bo'lsa ham) yangi 'containing block' yaratadi. Shu sababli ichidagi position:fixed element endi butun viewport'ga emas, balki shu transform qilingan ota elementga nisbatan joylashadi. Yechim: transform'ni fixed elementning ota-bobolaridan olib tashlash.",
            "hint": "position:fixed odatda nimaga nisbatan hisoblanadi, va transform bu qoidani qanday o'zgartiradi?",
            "explanation": "CSS spetsifikatsiyasiga ko'ra, transform (yoki filter, perspective) qiymati static bo'lmagan har qanday element yangi containing block yaratadi. Bu ichidagi fixed/absolute elementlarning 'nisbat nuqtasi'ni butunlay o'zgartiradi — bu keng tarqalgan, kutilmagan CSS tuzoqlaridan biri.",
        },
    },
    488: {  # Login Formasi
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi login formasida <code>&lt;label&gt;</code> va <code>&lt;input&gt;</code>ni shunday yozadi:</p>
<pre><code class="lang-html">&lt;label&gt;Foydalanuvchi nomi&lt;/label&gt;
&lt;input type="text" id="username"&gt;</code></pre>
<p><strong>Natija:</strong> Label matniga bosganda input maydoniga fokus <strong>tushmaydi</strong> — foydalanuvchi aynan input ustiga bosishi shart. Bu kichik, lekin real UX/accessibility muammosi: skrin-rider foydalanuvchilar uchun ham bu ikkisi bog'liq emas deb hisoblanadi.</p>
<p><strong>To'g'ri yechim:</strong> <code>&lt;label for="username"&gt;</code> — <code>input</code>ning <code>id</code>siga mos <code>for</code> atributi berish. Shunda label bosilganda ham input avtomatik fokus oladi.</p>""",
        "exercise": {
            "title": "<label>Foydalanuvchi nomi</label> ustiga bosilganda nega input maydoni fokus olmaydi?",
            "description": "<label>Foydalanuvchi nomi</label> va <input type=\"text\" id=\"username\"> alohida yozilgan, ular orasida hech qanday bog'lovchi atribut yo'q. Label matniga bosilganda nega input fokus olmaydi?",
            "exercise_type": "fill_in_blank",
            "correct_answers": "for",
            "hint": "label va inputni bog'laydigan, input'ning id'siga mos keladigan atribut qaysi?",
            "explanation": "label elementiga for=\"username\" atributi berilib, u input'ning id=\"username\" qiymatiga moslashtirilishi kerak. Shundagina label matniga bosish inputga fokus qo'yadi (bu accessibility uchun ham muhim).",
        },
    },
    489: {  # Register Formasi
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi ro'yxatdan o'tish formasida shunday yozadi:</p>
<pre><code class="lang-html">&lt;input type="email" id="email" placeholder="Email"&gt;
&lt;input type="password" id="password" placeholder="Parol"&gt;
&lt;button type="submit"&gt;Ro'yxatdan o'tish&lt;/button&gt;</code></pre>
<p><strong>Natija:</strong> Forma yuborilganda server hech qanday ma'lumot olmaydi — <code>request.form</code> bo'sh keladi! Sabab: har ikkala <code>&lt;input&gt;</code>da <strong><code>name</code> atributi yo'q</strong>. Forma yuborilganda brauzer faqat <code>name</code> atributi bor maydonlarni serverga jo'natadi — <code>id</code> faqat frontend/CSS/JS uchun, u serverga <strong>umuman yuborilmaydi</strong>.</p>
<p><strong>To'g'ri yechim:</strong> Har bir input'ga <code>name</code> atributi qo'shish: <code>&lt;input type="email" id="email" name="email"&gt;</code>.</p>""",
        "exercise": {
            "title": "input'larda faqat id bor, name yo'q — forma yuborilganda server nega bo'sh ma'lumot oladi?",
            "description": "<input type=\"email\" id=\"email\" placeholder=\"Email\"> — bu input'da id bor, lekin name yo'q. Forma yuborilganda server bu maydonni nega umuman ko'rmaydi?",
            "exercise_type": "multiple_choice",
            "options": '["placeholder qiymati serverga yuborilishi kerak edi", "Forma faqat name atributi bor maydonlarni serverga yuboradi, id faqat frontend uchun ishlatiladi", "type=\\"email\\" xato yozilgan", "Bu faqat POST so\'rovlarda muammo bo\'ladi"]',
            "correct_answers": "B",
            "hint": "Forma yuborilganda brauzer har bir maydonni QANDAY nom bilan serverga jo'natadi — id bilanmi, boshqa atribut bilanmi?",
            "explanation": "HTML formalarida faqat name atributi bor input'lar forma ma'lumotlarining bir qismi sifatida serverga yuboriladi. id — faqat CSS selektor yoki JavaScript uchun ishlatiladigan, sahifa ichidagi noyob identifikator, u forma submit protokoliga umuman aloqasi yo'q.",
        },
    },
    490: {  # CSS Animatsiya — Asoslar
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi menyuni ochish/yopishda balandlikni animatsiyalamoqchi bo'ladi:</p>
<pre><code class="lang-css">.menu {{ height: 0; overflow: hidden; transition: height 0.3s; }}
.menu.ochiq {{ height: auto; }}</code></pre>
<p><strong>Natija:</strong> Menyu <strong>sirpanib emas, sakrab</strong> ochiladi — <code>transition</code> umuman ishlamayotgandek tuyuladi! Sabab: CSS <code>transition</code> faqat ikkita <strong>aniq son</strong> qiymat orasida silliq animatsiya qila oladi. <code>height: auto</code> — aniq son emas, "kontentga qarab hisoblanadigan" qiymat, shuning uchun brauzer undan/unga o'tishni animatsiyalay olmaydi — u darhol sakrab o'zgaradi.</p>
<p><strong>To'g'ri yechim:</strong> Taxminiy aniq balandlik berish (<code>max-height: 500px;</code> kabi katta qiymat bilan) yoki JavaScript orqali haqiqiy <code>scrollHeight</code>ni o'lchab, aniq piksel qiymat sifatida animatsiyalash.</p>""",
        "exercise": {
            "title": "height: 0 dan height: auto ga transition berilsa, nega animatsiya silliq ishlamaydi?",
            "description": ".menu{height:0; transition:height 0.3s;} .menu.ochiq{height:auto;} — menyu sakrab ochiladi, sirpanmaydi. Nega transition ishlamayapti?",
            "exercise_type": "text_input",
            "expected_answer": "CSS transition faqat ikkita aniq sonli qiymat orasida silliq animatsiya bera oladi. auto — kontentga qarab hisoblanadigan noaniq qiymat, brauzer undan/unga silliq o'tishni hisoblay olmaydi, shuning uchun o'zgarish darhol (sakrab) sodir bo'ladi. Yechim: max-height bilan aniq (yetarlicha katta) qiymat berish yoki JS bilan scrollHeight'ni o'lchab aniq piksel animatsiyalash.",
            "hint": "CSS transition qanday qiymatlar orasida ishlay oladi — faqat aniq sonlar orasidami, 'auto' kabi hisoblab chiqiladigan qiymatlar bilan ham ishlaydimi?",
            "explanation": "Brauzer transition uchun boshlang'ich va oxirgi qiymat orasidagi oraliq qadamlarni hisoblashi kerak. 'auto' aniq son emas, shuning uchun bu hisob-kitob imkonsiz — brauzer shunchaki darhol yakuniy holatga o'tadi.",
        },
    },
    491: {  # CSS Animatsiya — Ilg'or
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi kartochkaga ham aylanish animatsiyasi, ham hover'da kattalashish beradi:</p>
<pre><code class="lang-css">@keyframes aylanish {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}
.karta {{ animation: aylanish 3s linear infinite; }}
.karta:hover {{ transform: scale(1.2); }}</code></pre>
<p><strong>Natija:</strong> Hover qilganda kartochka <strong>kattalashadi, lekin aylanish to'xtab qoladi</strong>! Sabab: <code>transform</code> xususiyati bir vaqtning o'zida <strong>faqat bitta qiymatni</strong> qabul qiladi. <code>:hover</code>dagi <code>transform: scale(1.2)</code> — animatsiyaning har bir kadrida hisoblanayotgan <code>rotate()</code> qiymatini butunlay <strong>almashtirib qo'yadi</strong>, ular birga qo'shilmaydi.</p>
<p><strong>To'g'ri yechim:</strong> Ikkala effektni bitta joyda birlashtirib yozish kerak, masalan JavaScript orqali CSS custom property yordamida, yoki animatsiyani alohida wrapper elementga, scale'ni esa ichki elementga berish.</p>""",
        "exercise": {
            "title": "Kartochka doim aylanayotgan bo'lsa, hover'da scale(1.2) berilsa, nega aylanish to'xtab qoladi?",
            "description": ".karta{animation: aylanish 3s linear infinite;} .karta:hover{transform: scale(1.2);} — hover paytida kartochka kattalashadi, lekin aylanish to'xtaydi. Nega ikkalasi birga ishlamaydi?",
            "exercise_type": "multiple_choice",
            "options": '["animation va transition bir vaqtda ishlatib bo\'lmaydi", "transform xususiyati bitta vaqtda faqat bitta qiymatni qabul qiladi, hover\'dagi scale() animatsiyadagi rotate() ni almashtirib yuboradi", "hover holatida @keyframes ishlamay qoladi", "scale(1.2) noto\'g\'ri sintaksis"]',
            "correct_answers": "B",
            "hint": "transform: rotate() va transform: scale() — bular ikki alohida xususiyatmi, yoki bitta xususiyatning ikki turli qiymatimi?",
            "explanation": "transform — bitta CSS xususiyat, va unga berilgan har qanday yangi qiymat avvalgisini TO'LIQ ALMASHTIRADI, ular qo'shilmaydi. :hover qoidasidagi transform: scale(1.2) shu paytda animatsiya hisoblab turgan rotate() qiymatini butunlay bekor qiladi.",
        },
    },
    492: {  # Parallax Effekti
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi parallax sahifasini <code>background-attachment: fixed</code> bilan qiladi va uni telefonda tekshiradi:</p>
<pre><code class="lang-css">.parallax-seksiya {{
  background-attachment: fixed;
  background-size: cover;
}}</code></pre>
<p><strong>Natija:</strong> Desktop brauzerda hammasi ajoyib ishlaydi, lekin <strong>iOS Safari'da (iPhone/iPad) parallax effekti butunlay ishlamaydi</strong> — fon rasm oddiy <code>scroll</code> kabi harakatlanadi! Sabab: mobil Safari brauzerlari <strong>ishlash sababli</strong> (performance) <code>background-attachment: fixed</code>ni qo'llab-quvvatlamaydi — bu ko'plab dasturchilarni "nega mening saytim faqat iPhone'da buzilgan" degan savolga olib keladigan mashhur muammo.</p>
<p><strong>To'g'ri yechim:</strong> Mobil qurilmalar uchun muqobil yondashuv kerak — masalan CSS <code>transform: translateZ()</code> asosidagi parallax kutubxonasi, yoki mobil ekranlarda parallax effektini butunlay o'chirib, oddiy statik fon bilan almashtirish (media query orqali).</p>""",
        "exercise": {
            "title": "background-attachment: fixed desktop'da ishlaydi, lekin iPhone'da nega parallax butunlay yo'qoladi?",
            "description": ".parallax-seksiya{background-attachment:fixed;} desktop brauzerlarda mukammal ishlaydi. iOS Safari'da (iPhone) esa fon oddiy scroll bilan harakatlanadi, parallax effekti yo'q. Nega?",
            "exercise_type": "text_input",
            "expected_answer": "Mobil Safari (iOS) ishlash unumdorligi (performance) sababli background-attachment: fixed'ni qo'llab-quvvatlamaydi — bu qasddan qilingan cheklov. Yechim: mobil ekranlar uchun media query orqali parallax'ni o'chirib statik fonga almashtirish, yoki transform-asosidagi JS parallax kutubxonasidan foydalanish.",
            "hint": "Bu CSS xususiyatning barcha brauzer/qurilmalarda bir xil qo'llab-quvvatlanishiga ishonch bormi, ayniqsa mobil qurilmalarda?",
            "explanation": "Bu — real, keng tarqalgan 'faqat mobil qurilmada buziladi' muammosi. iOS Safari background-attachment:fixed'ni ataylab qo'llab-quvvatlamaydi (batareya/ishlash resursi tejash uchun), shuning uchun cross-device test qilish har doim shart.",
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
