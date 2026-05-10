# NanoMed Professional Funksiyalar - Walkthrough

Barcha so'ralgan professional funksiyalar muvaffaqiyatli amalga oshirildi. Quyida amalga oshirilgan ishlar va ulardan foydalanish bo'yicha qisqacha ma'lumot keltirilgan.

## 1. Ma'lumotlar bazasi va Modellar
Ma'lumotlar bazasi tahlil va xavfsizlik talablariga muvofiq yangilandi:
- **`User`**: `referral_source` (qayerdan kelgani) va `created_at` ustunlari qo'shildi.
- **`Appointment`**: `is_feedback_sent` ustuni orqali bildirishnoma holati kuzatiladi.
- **`HealthRecord`**: Bemorlarning PDF tahlil natijalarini shifrlangan holda saqlash uchun yangi jadval yaratildi.

## 2. Analytics Engine (Tahlil moduli)
`utils/analytics.py` faylida shifokorlar va klinika boshqaruvi uchun muhim funksiyalar yozildi:
- `get_doctor_retention_rate`: Bemorlarning qayta kelish foizini hisoblaydi.
- `get_referral_stats`: Mijozlar oqimi manbalarini (Google, Instagram va h.k.) aniqlaydi.

## 3. Smart Notifications (Delayed Feedback)
`utils/scheduler.py` va `handlers/patient_notifications.py` integratsiya qilindi:
- Bemor klinikaga kelganini tasdiqlaganidan keyin, bot avtomatik tarzda **2 soatdan keyin** feedback (baholash) so'rovnomasini yuboradi.
- Bu jarayon `APScheduler` orqali xavfsiz boshqariladi.

## 4. E-Health Record Security
`utils/security.py` moduli orqali tibbiy hujjatlar himoyasi ta'minlandi:
- `cryptography (Fernet)` yordamida har bir PDF fayli alohida kalit bilan shifrlanadi.
- Fayllar diskda shifrlangan (.enc) holda saqlanadi va faqat bot orqali deshifrlanib foydalanuvchiga beriladi.

## 5. TMA Bridge
`bot/tma_api.py` faylida Telegram Mini App bilan bog'lanish logikasi yaratildi:
- `validate_init_data`: Frontenddan kelgan ma'lumotlarni Bot Token orqali tekshirish.
- `get_tma_doctor_schedules`: Mini App kalendari uchun shifokorlar jadvalini JSON formatda taqdim etish.

## Keyingi qadamlar
1. `requirements.txt` dagi yangi kutubxonalarni o'rnating: `pip install -r requirements.txt`.
2. Ma'lumotlar bazasini yangilang yoki reset qiling (`reset_db.py`).
3. TMA frontendini `bot/tma_api.py` dagi funksiyalar bilan bog'lang.
