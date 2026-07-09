"""
Check and optionally promote a user to teacher role.

Usage:
    cd backend
    source venv/bin/activate
    python scripts/check_promote_teacher.py ikromovl8
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.db.database import AsyncSessionLocal
from app.models.user import Student, UserRole
from app.models.group import Group


async def main(username: str) -> None:
    async with AsyncSessionLocal() as db:
        user = (await db.execute(
            select(Student).where(Student.username == username)
        )).scalar_one_or_none()

        if not user:
            print(f"ERROR: user '{username}' not found in DB")
            return

        print(f"id       : {user.id}")
        print(f"username : {user.username}")
        print(f"email    : {user.email}")
        print(f"full_name: {user.full_name}")
        print(f"role     : {user.role}")

        groups = (await db.execute(
            select(Group).where(Group.teacher_id == user.id)
        )).scalars().all()
        print(f"groups   : {[g.name for g in groups] or '(none)'}")

        if user.role != UserRole.teacher:
            user.role = UserRole.teacher
            await db.commit()
            print(f"\n>>> Promoted '{username}' to teacher role.")
        else:
            print(f"\n>>> Role is already 'teacher'. No change needed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_promote_teacher.py <username>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
