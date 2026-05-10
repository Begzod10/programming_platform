# Doctor WebApp & Reminders Checklist

## ⚙️ 1-qism: Muhitni sozlash [ ]
- [ ] FastAPI va Uvicorn o'rnatilganligini tekshirish (pydantic versiyasini aiogram bilan muvofiqlashtirish)
- [ ] Vite + React loyihasini yaratish (`npx create-vite webapp`)
- [ ] Kerakli kutubxonalarni o'rnatish (axios, react-router, lucide-react, date-fns)

## 🐍 2-qism: Backend (FastAPI) [ ]
- [ ] `web_server.py` yaratish
- [ ] SQLite MB bilan ulanish (SQLAlchemy)
- [ ] `GET /api/schedule/{doctor_id}` - Haftalik jadvalni olish
- [ ] `POST /api/schedule/toggle` - Slotni band qilish/bo'shatish
- [ ] CORS sozlamalari (React bilan ulanish uchun)

## 🎨 3-qism: Frontend (React) [ ]
- [ ] NanoMed brend ranglari uchun CSS o'zgaruvchilarini sozlash
- [ ] Dashboard sahifasi: Haftalik kalendar ko'rinishi
- [ ] Interaktiv slotlar (Click to Toggle)
- [ ] Telegram WebApp SDK integratsiyasi (MainButton, CloseApp)

## 🤖 4-qism: Bot Integratsiyasi [ ]
- [ ] `handlers/doctor_profile.py` ga "📅 Kalendar (WebApp)" tugmasini qo'shish
- [ ] `main.py` ni Parallel ishga tushirish (FastAPI + Aiogram)

## ⏰ 5-qism: Eslatmalar Polishi [ ]
- [ ] `utils/scheduler.py` matnlarini premium holatga keltirish
- [ ] Sinovdan o'tkazish
