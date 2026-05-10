import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys
import os

# App paths qo'shish
sys.path.append(os.getcwd())

from app.services.gennis_service import GennisService
from app.services.auth_service import login
from app.config import settings
from app.db.database import AsyncSessionLocal
import json

async def debug_login(username, password):
    data = await GennisService.login(username, password)
    if data and 'data' in data:
        print(f"DEBUG: data['data'] keys: {list(data['data'].keys())}")
        for key in data['data'].keys():
            val = data['data'][key]
            if isinstance(val, dict):
                print(f"DEBUG: data['data']['{key}'] keys: {list(val.keys())}")
            else:
                print(f"DEBUG: data['data']['{key}'] type: {type(val)}")
    return data

async def test_real_login(username, password):
    print(f"Testing login for {username}...")
    await debug_login(username, password)
    
    # DB session yaratish
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # Login funksiyasini chaqiramiz
            result = await login(db, username, password)
            print("Login success!")
            print(f"User: {result['user'].full_name} (Role: {result['user'].role})")
            print(f"Token: {result['access_token'][:20]}...")
            
            # Bazada ma'lumotlar yangilanganini tekshirish
            user = result['user']
            print(f"Synced Data - Phone: {user.phone}, Balance: {user.balance}, Surname: {user.surname}")
            
        except Exception as e:
            print(f"Login failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_login_flow.py <username> <password>")
    else:
        asyncio.run(test_real_login(sys.argv[1], sys.argv[2]))
