# NanoMed: Bot va Mini App Integratsiyasi - Yakuniy Walkthrough

NanoMed loyihasining barcha qismlari (Bot, API Server va React TMA) endi yagona ekotizim sifatida bir-biri bilan to'liq bog'langan.

## 🔗 Integratsiya qanday ishlaydi?

### 1. Botdan kirish (Telegram Interface)
- Botning asosiy menyusida **"🏥 Mini App orqali yozilish"** tugmasi paydo bo'ldi.
- Ushbu tugma bosilganda Telegram avtomatik tarzda bizning React ilovamizni ochadi va xavfsizlik uchun `initData` ni uzatadi.

### 2. API Server (FastAPI)
- `tma_server.py` nomli alohida API server yaratildi.
- U Mini Appdan kelgan so'rovlarni qabul qiladi, `initData` ni Bot Token orqali tekshiradi va ma'lumotlar bazasi (SQLAlchemy) bilan ishlaydi.

### 3. Real Ma'lumotlar Almashinuvi (End-to-End)
- **Ma'lumot olish**: Ilova ochilganda, React `api.js` orqali FastAPI dan shifokorlar ro'yxati va bemorning shaxsiy dashbordini (Dashboard) yuklab oladi.
- **Band qilish**: Bemor Mini Appda vaqtni tanlab "Band qilish" tugmasini bossa, ma'lumotlar FastAPI ga yuboriladi va u yerda `appointments` jadvaliga saqlanadi.
- **Bot Bildirishnomasi**: Muvaffaqiyatli band qilishdan so'ng, FastAPI bot orqali bemorga darhol **"Muvaffaqiyatli yozildingiz"** degan xabarni yuboradi.

## 📁 Yangi komponentlar:
- `tma_server.py`: API server (Backend connector).
- `frontend/src/utils/api.js`: Axios ulanish moduli.
- `keyboards/patient_kb.py`: WebApp tugmasi bilan yangilangan menyu.

## 🚀 Ishga tushirish tartibi:
1. Birinchi terminalda botni boshlang: `python main.py`
2. Ikkinchi terminalda API serverni boshlang: `python tma_server.py`
3. Uchinchi terminalda frontendni boshlang: `cd frontend && npm run dev`

Tizim endi to'liq avtomatlashtirilgan va foydalanishga tayyor!
