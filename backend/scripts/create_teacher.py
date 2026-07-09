"""
Create a teacher account directly in the DB.

Usage:
    cd backend
    source venv/bin/activate
    python scripts/create_teacher.py --username ikromovl8 --password SECRET --email ikromov@example.com

The script is idempotent: if the username already exists it just prints the existing ID.
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.user import Student, UserRole
from app.core.security import get_password_hash


async def main(username: str, password: str, email: str, full_name: str) -> None:
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(
            select(Student).where(Student.username == username)
        )).scalar_one_or_none()

        if existing:
            if existing.role != UserRole.teacher:
                existing.role = UserRole.teacher
                await db.commit()
                print(f"Updated existing user '{username}' (id={existing.id}) to teacher role.")
            else:
                print(f"Teacher '{username}' already exists (id={existing.id}).")
            return

        teacher = Student(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name or username,
            role=UserRole.teacher,
            is_active=True,
        )
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        print(f"Created teacher '{username}' with id={teacher.id}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", default="")
    args = parser.parse_args()

    asyncio.run(main(args.username, args.password, args.email, args.full_name))
