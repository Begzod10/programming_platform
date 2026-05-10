# Task List: Production Readiness (PostgreSQL & Vercel)

- [x] 1. Muhit parametrlarini sozlash (.env)
    - [x] `python-dotenv` o'rnatish
    - [x] `.env` faylini yaratish va tokenlarni ko'chirish
- [x] 2. Ma'lumotlar bazasini PostgreSQL ga moslashtirish
    - [x] `database/database.py` ni dinamik URL ga o'tkazish
    - [x] `requirements.txt` ga `asyncpg` va `psycopg2-binary` qo'shish
- [x] 3. Vercel Serverless Function (Backend)
    - [x] `api/index.py` yaratish (Vercel uchun entry point)
    - [x] `tma_server.py` ni importga moslashtirish
- [x] 4. Vercel Routing va Frontend
    - [x] Root `vercel.json` yaratish
    - [x] `frontend/src/utils/api.js` ni dinamik URL ga o'tkazish
- [x] 5. Yakuniy tekshiruv va Walkthrough
