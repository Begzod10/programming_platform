import asyncio
from app import AsyncSessionLocal
from app import login

async def main():
    async with AsyncSessionLocal() as db:
        username, password = "rimefara_teach", "22100122"
        print(f"Testing TEACHER: {username}")
        result = await login(db, username, password)
        print("Done")

if __name__ == "__main__":
    asyncio.run(main())
