import asyncio
from app import AsyncSessionLocal
from app import login


async def run_test(username, password, label):
    print(f"\n--- Testing {label}: {username} ---")
    async with AsyncSessionLocal() as db:
        try:
            result = await login(db, username, password)
            print(f"Login Result: Success")
            user = result.get("user")
            if user:
                print(f"User in DB: ID={user.id}, Username={user.username}, Role={user.role}")
                print(f"Full Name: {user.full_name}")
                if hasattr(user, 'group_id'):
                    print(f"Group ID: {user.group_id}")
                if hasattr(user, 'balance'):
                    print(f"Balance: {user.balance}")
            else:
                print("No user returned in result")
        except Exception as e:
            print(f"Error during login/sync: {e}")
            import traceback
            traceback.print_exc()

async def main():
    # Test credentials provided by user
    tests = [
        ("rimefara_teach", "22100122", "TEACHER"),
        ("Bexruz35", "12345678", "STUDENT")
    ]
    
    for username, password, label in tests:
        await run_test(username, password, label)

if __name__ == "__main__":
    asyncio.run(main())
