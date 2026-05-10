# Nanomed Premium Yangilanishlar (V2) — Walkthrough

Botingizga yana 3 ta yirik biznes-funksiya muvaffaqiyatli qo'shildi.

## 🤖 1. AI Shifokor Tavsiyasi (Mockup)
Bemorlar endi o'z simptomlarini yozib, qaysi shifokorga borish kerakligi bo'yicha "Aqlli" tavsiya olishlari mumkin.
- **Hozirgi holat**: Tizim to'laqonli UI/UX ga ega, hozircha "Mockup" (soxta javob) beradi. Gemini API kaliti qo'shilishi bilan haqiqiy AI ga aylanadi.
- **Sinab ko'ring**: Bemor menyusidan "🤖 AI Tavsiya" tugmasini bosing.

## 📊 2. Admin uchun Statistik Grafiklar
Admin endi nafaqat raqamlarni, balki daromad dinamikasini grafikli ko'rinishda ko'ra oladi.
- **Texnologiya**: `matplotlib` yordamida har gal yangi grafik rasm shaklida generatsiya qilinadi.
- **Sinab ko'ring**: Admin panelidan "📊 Grafik" tugmasini bosing.

## 🕒 3. Avtomatik Kutish Ro'yxati (Waitlist)
Shifokorda bo'sh vaqt qolmagan bo'lsa, bemorlar navbatga turishlari mumkin.
- **Mantiq**: Agar shifokorda bo'sh vaqt bo'lmasa -> Bemor "Navbatga turish"ni bosadi -> Boshqa bemor qabulni bekor qilsa -> Navbatdagiga avtomatik xabar boradi.
- **Foyda**: Klinikadagi bo'sh qolgan vaqtlardan 100% samarali foydalanish.

---

## 🛠 O'zgarishlar:
- `database/models.py`: `Waitlist` jadvali qo'shildi.
- `handlers/admin_panel.py`: Grafik generatsiya qilish mantiqi qo'shildi.
- `handlers/patient_features.py`: AI handlerlari qo'shildi.
- `requirements.txt`: `matplotlib` kutubxonasi qo'shildi.

> [!TIP]
> Yangi funksiyalarni ko'rish uchun botni o'chirib, qayta **`py main.py`** qilib ishga tushiring!
