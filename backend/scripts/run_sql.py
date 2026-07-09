import asyncio
import os
import sys

# Loyiha papkasini tanitish
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine
from sqlalchemy import text

async def fix_columns():
    async with engine.begin() as conn:
        try:
            # 1. Telefon raqami uchun joyni 50 tagacha oshirish
            await conn.execute(text("ALTER TABLE students ALTER COLUMN phone TYPE VARCHAR(50);"))
            
            # 2. Token juda uzun bo'lgani uchun uni TEXT turiga o'tkazish
            await conn.execute(text("ALTER TABLE students ALTER COLUMN gennis_token TYPE TEXT;"))
            
            # 3. Ism-sharif ba'zan uzun bo'lishi mumkin, uni 255 tagacha oshiramiz
            await conn.execute(text("ALTER TABLE students ALTER COLUMN full_name TYPE VARCHAR(255);"))
            
            print("✅ Ustunlar hajmi muvaffaqiyatli oshirildi!")
        except Exception as e:
            print(f"❌ Xatolik yuz berdi: {e}")
    
    # Engine-ni yopish
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_columns())