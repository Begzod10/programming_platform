import httpx
import asyncio

async def run():
    async with httpx.AsyncClient() as client:
        resp = await client.post('https://admin.gennis.uz/api/base/login', json={'username': 'rimefara_teach', 'password': '22100122'})
        data = resp.json()
        print("Role:", data.get('user', {}).get('role'))
        print("Type_User:", data.get('type_user'))

asyncio.run(run())
