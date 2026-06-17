"""Seed category-based achievements into the database.

Idempotent: skips any achievement where the same
criteria_type + criteria_value + name already exists.

Usage:
    cd backend
    python scripts/seed_achievements.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.achievement import Achievement  # noqa: E402

ACHIEVEMENTS = [
    # --- LEARNING ---
    {
        "category": "learning",
        "icon": "📖",
        "name": "Birinchi qadam",
        "description": "Birinchi darsni tugatdingiz!",
        "criteria_type": "lesson_count",
        "criteria_value": 1,
        "points_reward": 50,
    },
    {
        "category": "learning",
        "icon": "📚",
        "name": "O'quvchi",
        "description": "10 ta darsni tugatdingiz",
        "criteria_type": "lesson_count",
        "criteria_value": 10,
        "points_reward": 100,
    },
    {
        "category": "learning",
        "icon": "🎓",
        "name": "Bilimli",
        "description": "50 ta darsni tugatdingiz",
        "criteria_type": "lesson_count",
        "criteria_value": 50,
        "points_reward": 250,
    },
    {
        "category": "learning",
        "icon": "🏫",
        "name": "Birinchi kurs",
        "description": "Birinchi kursni muvaffaqiyatli tugatdingiz",
        "criteria_type": "course_count",
        "criteria_value": 1,
        "points_reward": 200,
    },
    {
        "category": "learning",
        "icon": "🧠",
        "name": "Kurs yig'uvchi",
        "description": "3 ta kursni tugatdingiz",
        "criteria_type": "course_count",
        "criteria_value": 3,
        "points_reward": 500,
    },
    {
        "category": "learning",
        "icon": "🌟",
        "name": "Mutaxassis",
        "description": "5 ta kursni tugatdingiz",
        "criteria_type": "course_count",
        "criteria_value": 5,
        "points_reward": 1000,
    },
    # --- PROJECTS ---
    {
        "category": "projects",
        "icon": "🚀",
        "name": "Birinchi loyiha",
        "description": "Birinchi loyihani topshirdingiz va qabul qilindi",
        "criteria_type": "project_count",
        "criteria_value": 1,
        "points_reward": 75,
    },
    {
        "category": "projects",
        "icon": "💻",
        "name": "Dasturchi",
        "description": "5 ta loyiha qabul qilindi",
        "criteria_type": "project_count",
        "criteria_value": 5,
        "points_reward": 150,
    },
    {
        "category": "projects",
        "icon": "⚡",
        "name": "Loyiha ustasi",
        "description": "10 ta loyiha qabul qilindi",
        "criteria_type": "project_count",
        "criteria_value": 10,
        "points_reward": 300,
    },
    {
        "category": "projects",
        "icon": "🏗️",
        "name": "Quriluvchi",
        "description": "20 ta loyiha qabul qilindi",
        "criteria_type": "project_count",
        "criteria_value": 20,
        "points_reward": 600,
    },
    # --- VOCABULARY ---
    {
        "category": "vocabulary",
        "icon": "📝",
        "name": "So'z yig'uvchi",
        "description": "Lug'atga 10 ta so'z qo'shdingiz",
        "criteria_type": "word_count",
        "criteria_value": 10,
        "points_reward": 50,
    },
    {
        "category": "vocabulary",
        "icon": "📒",
        "name": "Lug'at",
        "description": "Lug'atga 50 ta so'z qo'shdingiz",
        "criteria_type": "word_count",
        "criteria_value": 50,
        "points_reward": 150,
    },
    {
        "category": "vocabulary",
        "icon": "📕",
        "name": "Leksikon",
        "description": "Lug'atga 100 ta so'z qo'shdingiz",
        "criteria_type": "word_count",
        "criteria_value": 100,
        "points_reward": 300,
    },
    {
        "category": "vocabulary",
        "icon": "🔤",
        "name": "So'z usta",
        "description": "Lug'atga 200 ta so'z qo'shdingiz",
        "criteria_type": "word_count",
        "criteria_value": 200,
        "points_reward": 600,
    },
    # --- POINTS ---
    {
        "category": "points",
        "icon": "⭐",
        "name": "Yulduz",
        "description": "100 ball to'pladingiz",
        "criteria_type": "points_threshold",
        "criteria_value": 100,
        "points_reward": 0,
    },
    {
        "category": "points",
        "icon": "🌠",
        "name": "Ko'tariluvchi",
        "description": "1,000 ball to'pladingiz",
        "criteria_type": "points_threshold",
        "criteria_value": 1000,
        "points_reward": 50,
    },
    {
        "category": "points",
        "icon": "💫",
        "name": "Elite",
        "description": "5,000 ball to'pladingiz",
        "criteria_type": "points_threshold",
        "criteria_value": 5000,
        "points_reward": 100,
    },
    {
        "category": "points",
        "icon": "🏆",
        "name": "Chempion",
        "description": "10,000 ball to'pladingiz",
        "criteria_type": "points_threshold",
        "criteria_value": 10000,
        "points_reward": 200,
    },
]


async def seed() -> None:
    created = 0
    skipped = 0

    async with AsyncSessionLocal() as db:
        for data in ACHIEVEMENTS:
            existing = (
                await db.execute(
                    select(Achievement).where(
                        Achievement.criteria_type == data["criteria_type"],
                        Achievement.criteria_value == data["criteria_value"],
                        Achievement.name == data["name"],
                    )
                )
            ).scalar_one_or_none()

            if existing is not None:
                print(f"  SKIP  [{data['category']}] {data['icon']} {data['name']}")
                skipped += 1
                continue

            achievement = Achievement(
                name=data["name"],
                description=data["description"],
                badge_image_url="",
                points_reward=data["points_reward"],
                criteria_type=data["criteria_type"],
                criteria_value=data["criteria_value"],
                category=data["category"],
                icon=data["icon"],
            )
            db.add(achievement)
            print(f"  CREATE [{data['category']}] {data['icon']} {data['name']}")
            created += 1

        if created:
            await db.commit()

    print(f"\nDone. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
