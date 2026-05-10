# Telegram WebApp va Eslatmalar tizimi rejasi (Yangilangan)

Ushbu reja shifokorlar uchun interaktiv WebApp kalendar yaratish va mavjud eslatmalar tizimini yanada barqaror qilishni o'z ichiga oladi.

## Proposed Changes

### 1. 🌐 Doctor WebApp (Kalendar)
- **Backend (API)**: `web_server.py` fayli yaratiladi (FastAPI). U quyidagi endpointlarga ega bo'ladi:
  - `GET /api/schedule/{doctor_id}`: Shifokorning joriy haftadagi vaqtlarini olish.
  - `POST /api/schedule/update`: Vaqtlarni qo'shish yoki o'chirish.
- **Frontend (UI)**: `web/` papkasida NanoMed brendi uslubidagi interfeys yaratiladi:
  - **Dizayn**: NanoMed logotipidagi **To'q sariq (#F28C28)** va **To'q kulrang/Qora (#1A1A1A)** ranglar palitrasidan foydalaniladi. Premium "Glassmorphism" va silliq UI elementlari.
  - **Funksiya**: Shifokor kalendarda bo'sh vaqtlarini bosish orqali band qila oladi yoki bo'shata oladi. Google Calendar kabi haftalik ko'rinish.
- **Bot Integratsiyasi**: Shifokor profiliga yangi "📅 Kalendar (WebApp)" tugmasi qo'shiladi.

### 2. ⏰ Eslatmalar tizimi (Reminders)
- **Mantiq**: Hozirgi 1 kun oldin va 2 soat oldin (har 30 minutda) eslatish tizimi haqiqiy ma'lumotlar bilan sinxronlashtiriladi.
- **Xabarlar**: "Hurmatli bemor, NanoMed klinikasi eslatib o'tadi..." kabi premium matnlar.

### 3. 🚀 Main Integratsiya
- `main.py` fayli `aiogram` va `fastapi`ni parallel ravishda ishga tushiradigan qilinadi (asyncio gather yordamida).

---

## User Review Required

> [!IMPORTANT]  
> WebApp ishlashi uchun HTTPS manzilli URL kerak. Mahalliy testlar uchun `localtunnel` (Node.js) yoki foydalanuvchi orqali boshqa usuldan foydalanishimiz mumkin.

> [!NOTE]  
> FastAPI va Uvicorn allaqachon o'rnatildi. Baza bilan integratsiya to'liq ta'minlanadi.

## Verification Plan

### Automated Tests
- API endpointlarni `curl` yordamida tekshirish.

### Manual Verification
1. Shifokor profilidan "Kalendar" tugmasini bosish.
2. WebApp'da vaqtlarni belgilash va bazada aks etishini tekshirish.
3. Eslatma xabarlarini vaqtida borishini tekshirish.
