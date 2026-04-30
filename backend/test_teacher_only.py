import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.services.auth_service import login

async def main():
    async with AsyncSessionLocal() as db:
        username, password = "rimefara_teach", "22100122"
        print(f"Testing TEACHER: {username}")
        result = await login(db, username, password)
        print("Done")

if __name__ == "__main__":
    asyncio.run(main())
