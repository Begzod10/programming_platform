"""One-off: seed the initial "early learner" (age 4-6) catalog — 4 draft
modules covering literacy/math/logic/creative (each a first pass, left
unpublished pending real media), plus 5 complete, published matching-game
packs ("Kasblar shaharchasi" / "Fasllar dunyosi" / "Hayvonot olami" /
"Transport olami" / "Rang olami") that use emoji-first, icon-based content
instead of image assets. See project_student_platform memory /
early_learning.py for the model design rationale (no AI grading, star-based
completion instead of points).

Creates the early_modules / early_activities / early_activity_completions
tables directly via Base.metadata.create_all() scoped to just those three,
rather than through `alembic upgrade` — per backend/.gitignore, this repo's
alembic/versions/ is "managed on server, never committed" (migrations are
applied out-of-band against the server DB, not through the git deploy
pipeline), and the local versions/ directory that does exist has a broken
revision graph on top of that. create_all() is additive-only and
checkfirst=True, so it's a no-op against any table that already exists —
safe to re-run.

Idempotent on content: re-running updates existing rows (matched by
module title / activity title+module) instead of duplicating them.

Media URLs are intentionally left as None — no real assets exist yet.
A content author needs to fill instruction_audio_url and the image/audio
fields inside content_json before publishing (is_published stays False
here on purpose).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401  (registers all models for the mapper registry)
from app.db.base_class import Base  # noqa: E402
from app.models.early_learning import (  # noqa: E402
    EarlyModule, EarlyActivity, EarlyActivityCompletion, EarlySubject, EarlyActivityType,
)

INSTRUCTOR_ID = 2  # rimefara_teach / Begzod Jumaniyozov — existing teacher account

# Many kids at this age (5-8) can't reliably read yet, in either language —
# the lucide `icon` name alone (rendered as a small monochrome line-glyph)
# isn't recognizable enough at a glance, and the Uzbek label under it is
# useless to a non-reader. Emoji are colorful, high-contrast, and kids
# recognize them without reading — so every `match`/select item also gets
# an `emoji`, keyed once here by item id rather than repeated inline (the
# same id shows up as a distractor in several other activities, and it
# must render identically everywhere it appears). `icon` stays as a
# fallback for any id this dict doesn't cover.
ITEM_EMOJI = {
    # Kasblar shaharchasi
    "chef_hat": "👨‍🍳", "recipe_book": "📖", "mixing_bowl": "🥣", "chef_knife": "🔪",
    "fire": "🔥", "soup_pot": "🍲",
    "stethoscope": "🩺", "syringe": "💉", "pill": "💊", "heart_pulse": "💓",
    "bandage": "🩹", "thermometer": "🌡️",
    "wrench": "🔧", "cog": "⚙️", "battery": "🔋", "truck": "🚚", "gauge": "🎛️", "toolbox": "🧰",
    "hard_hat": "⛑️", "hammer": "🔨", "ruler": "📏", "brick_wall": "🧱",
    "construction": "🚧", "shovel": "⛏️",
    "microscope": "🔬", "flask": "⚗️", "test_tube": "🧪", "atom": "⚛️",
    "telescope": "🔭", "magnet": "🧲",
    "laptop": "💻", "keyboard": "⌨️", "monitor": "🖥️", "code": "👨‍💻", "cpu": "🔌", "terminal": "🖱️",
    "graduation_cap": "🎓", "textbook": "📚", "pen_tool": "🖊️", "pencil": "✏️",
    "backpack": "🎒", "apple": "🍎",
    "shield": "🛡️", "badge": "🎖️", "siren": "🚨", "car": "🚓",
    "traffic_cone": "🚦", "hand": "✋", "book": "📖",
    # Fasllar dunyosi
    "flower": "🌸", "tulip": "🌷", "sprout": "🌱", "umbrella": "☔",
    "rain_cloud": "🌧️", "rainbow": "🌈",
    "snowflake": "❄️", "ice_cream": "🍦", "leaf": "🍁", "gift": "🎁",
    "sun": "☀️", "glasses": "🕶️", "sailboat": "⛵", "droplets": "💧", "footprints": "👣",
    "tree_pine": "🌲", "wind": "💨", "wheat": "🌾", "tree_deciduous": "🌳",
    "squirrel": "🐿️", "cold_thermometer": "🥶", "cloud_snow": "🌨️", "candy_cane": "🍬",
    # Hayvonot olami
    "fish": "🐟", "milk": "🥛", "mouse": "🐭", "yarn": "🧶", "paw": "🐾", "basket": "🧺",
    "bone": "🦴", "tennis_ball": "🎾", "pet_bowl": "🥣", "doghouse": "🏠", "rope_toy": "🪢",
    "grass": "🌿", "cheese": "🧀", "cowbell": "🔔", "bucket": "🪣",
    "carrot": "🥕", "cabbage": "🥬", "clover": "🍀", "dandelion": "🌼", "hole": "🕳️",
    "meat": "🍖", "crown": "👑", "peanut": "🥜", "banana": "🍌", "tree": "🌳", "green_leaf": "🍃",
    # Transport olami
    "sedan_car": "🚗", "bus": "🚌", "bicycle": "🚲", "train": "🚆", "motorcycle": "🏍️",
    "cargo_ship": "🚢", "speedboat": "🚤", "canoe": "🛶", "ferry": "⛴️", "anchor": "⚓",
    "airplane": "✈️", "rocket": "🚀", "small_plane": "🛩️", "parachute": "🪂", "ufo": "🛸",
    "helicopter": "🚁",
    # Rang olami
    "strawberry": "🍓", "cherry": "🍒", "heart": "❤️", "fire_truck": "🚒", "rose": "🌹",
    "lemon": "🍋", "corn": "🌽", "chick": "🐤", "star": "⭐",
    "broccoli": "🥦", "frog": "🐸", "cucumber": "🥒", "cactus": "🌵",
    "blueberries": "🫐", "wave": "🌊", "whale": "🐳", "blue_bird": "🐦", "gem": "💎",
    "grapes": "🍇",
}


def _with_emoji(content: dict) -> dict:
    """Inject `emoji` into every item of a mode="select" content dict,
    looked up from ITEM_EMOJI by id. No-op for any other content shape."""
    if content.get("mode") != "select":
        return content
    for key in ("correct_items", "distractor_items"):
        for item in content.get(key, []):
            item["emoji"] = ITEM_EMOJI.get(item["id"], "❓")
    return content

MODULES = [
    {
        "title": "Harflar sayohati",
        "description": "Harflarni tanish, tovushlarni ajratish va birinchi so'zlar.",
        "subject": EarlySubject.literacy,
        "icon_emoji": "🔤",
        "color_accent": "#FF6B6B",
        "display_order": 1,
        "activities": [
            {
                "title": "A dan D gacha — chizib yozamiz",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Barmog'ing bilan harfni chiz.",
                "content": {"targets": [
                    {"letter": "A", "outline_url": None},
                    {"letter": "B", "outline_url": None},
                    {"letter": "C", "outline_url": None},
                    {"letter": "D", "outline_url": None},
                ]},
            },
            {
                "title": "Tovush va rasm — moslashtir",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Harfni to'g'ri rasmga ulash.",
                "content": {"pairs": [
                    {"left": "B", "right": "Bola", "image_url": None},
                    {"left": "M", "right": "Mushuk", "image_url": None},
                    {"left": "O", "right": "Olma", "image_url": None},
                ]},
            },
            {
                "title": "Ertak tinglaymiz",
                "activity_type": EarlyActivityType.audio_story,
                "instruction_text": None,
                "content": {
                    "text": "Kichkina quyoncha o'rmonda sayr qilib yurardi...",
                    "audio_url": None,
                    "image_url": None,
                },
            },
            {
                "title": "Harfiga qarab ajrat",
                "activity_type": EarlyActivityType.sort,
                "instruction_text": "Rasmlarni boshlang'ich harfiga qarab joylashtir.",
                "content": {
                    "buckets": ["A", "B"],
                    "items": [
                        {"label": "Arik", "bucket": "A", "image_url": None},
                        {"label": "Baliq", "bucket": "B", "image_url": None},
                        {"label": "Bahor", "bucket": "B", "image_url": None},
                        {"label": "Asal", "bucket": "A", "image_url": None},
                    ],
                },
            },
        ],
    },
    {
        "title": "Sonlar dunyosi",
        "description": "Sanash, shakllarni solishtirish va oddiy tartib.",
        "subject": EarlySubject.math,
        "icon_emoji": "🔢",
        "color_accent": "#4D96FF",
        "display_order": 2,
        "activities": [
            {
                "title": "Sanab ko'ramiz",
                "activity_type": EarlyActivityType.count,
                "instruction_text": "Nechta olma borligini sanab, to'g'ri sonni bos.",
                "content": {"object_image_url": None, "count": 4, "options": [3, 4, 5]},
            },
            {
                "title": "Kattami, kichikmi?",
                "activity_type": EarlyActivityType.sort,
                "instruction_text": "Shakllarni kattaligiga qarab joylashtir.",
                "content": {
                    "buckets": ["Kichik", "Katta"],
                    "items": [
                        {"label": "Kichik doira", "bucket": "Kichik", "image_url": None},
                        {"label": "Katta doira", "bucket": "Katta", "image_url": None},
                        {"label": "Kichik kvadrat", "bucket": "Kichik", "image_url": None},
                        {"label": "Katta kvadrat", "bucket": "Katta", "image_url": None},
                    ],
                },
            },
            {
                "title": "Son va miqdorni ulash",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sonni tegishli miqdordagi rasmga ulang.",
                "content": {"pairs": [
                    {"left": "1", "right": "1 ta olma", "image_url": None},
                    {"left": "2", "right": "2 ta olma", "image_url": None},
                    {"left": "3", "right": "3 ta olma", "image_url": None},
                ]},
            },
            {
                "title": "1 dan 5 gacha tartibla",
                "activity_type": EarlyActivityType.sequence,
                "instruction_text": "Sonlarni to'g'ri tartibda joylashtir.",
                "content": {"correct_order": [1, 2, 3, 4, 5], "shuffled": [3, 1, 5, 2, 4]},
            },
        ],
    },
    {
        "title": "Fikrlash o'yinlari",
        "description": "Ketma-ketlik, naqshlar va yo'l topish.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🧩",
        "color_accent": "#9B5DE5",
        "display_order": 3,
        "activities": [
            {
                "title": "Kunlik tartib",
                "activity_type": EarlyActivityType.sequence,
                "instruction_text": "Kun tartibini to'g'ri ketma-ketlikda joylashtir.",
                "content": {
                    "correct_order": ["Uyg'onish", "Tishlarni yuvish", "Nonushta", "Kiyinish"],
                    "shuffled": ["Kiyinish", "Uyg'onish", "Nonushta", "Tishlarni yuvish"],
                },
            },
            {
                "title": "Yo'lni top",
                "activity_type": EarlyActivityType.maze,
                "instruction_text": "O'qlar yordamida boshidan oxirigacha yo'l top.",
                "content": {"grid_size": [5, 5], "start": [0, 0], "end": [4, 4], "walls": []},
            },
            {
                "title": "Naqshni davom ettir",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Naqshdagi keyingi rangni top.",
                "content": {"pattern": ["red", "blue", "red", "blue", "?"], "options": ["red", "blue", "green"], "answer": "red"},
            },
        ],
    },
    {
        "title": "Ijodkorlik burchagi",
        "description": "Bo'yash va shakllarni chizish.",
        "subject": EarlySubject.creative,
        "icon_emoji": "🎨",
        "color_accent": "#FFB84D",
        "display_order": 4,
        "activities": [
            {
                "title": "Erkin bo'yash",
                "activity_type": EarlyActivityType.coloring,
                "instruction_text": "Xohlagan rangda bo'ya.",
                "content": {"templates": [
                    {"id": 1, "outline_url": None},
                    {"id": 2, "outline_url": None},
                    {"id": 3, "outline_url": None},
                ]},
            },
            {
                "title": "Shakllarni chizamiz",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Shaklni barmog'ing bilan chiz.",
                "content": {"targets": [
                    {"shape": "circle", "outline_url": None},
                    {"shape": "square", "outline_url": None},
                    {"shape": "triangle", "outline_url": None},
                ]},
            },
        ],
    },
    # ── "Kasblar shaharchasi" / "Fasllar dunyosi": tap-to-select matching
    # packs, activity_type=match with a new content["mode"]="select" shape
    # (character + correct_items + distractor_items, each item carrying a
    # lucide-react icon name instead of an image_url) — unlike the drafts
    # above, these ship complete (icon-based, no missing media), so
    # is_published=True. See docs/plans or the early-learning feature plan
    # for the design rationale (subject stays "logic" — categorization is a
    # logic skill, and adding a new EarlySubject value would need an
    # ALTER TYPE against the already-materialized Postgres enum).
    {
        "title": "Kasblar shaharchasi",
        "description": "Kasbni tanla va unga kerakli asboblarni top.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🏙️",
        "color_accent": "#FF9F40",
        "display_order": 5,
        "is_published": True,
        "activities": [
            {
                "title": "Oshpaz",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Oshpazga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👨‍🍳", "label": "Oshpaz"},
                    "correct_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "icon": "ChefHat"},
                        {"id": "recipe_book", "label": "Retsept kitobi", "icon": "BookOpen"},
                        {"id": "mixing_bowl", "label": "Aralashtirish kosasi", "icon": "CookingPot"},
                        {"id": "chef_knife", "label": "Oshpaz pichog'i", "icon": "UtensilsCrossed"},
                        {"id": "fire", "label": "Olov", "icon": "Flame"},
                        {"id": "soup_pot", "label": "Sho'rva qozoni", "icon": "Soup"},
                    ],
                    "distractor_items": [
                        {"id": "keyboard", "label": "Klaviatura", "icon": "Keyboard"},
                        {"id": "stethoscope", "label": "Stetoskop", "icon": "Stethoscope"},
                        {"id": "hammer", "label": "Bolg'a", "icon": "Hammer"},
                        {"id": "shield", "label": "Qalqon", "icon": "Shield"},
                    ],
                },
            },
            {
                "title": "Shifokor",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Shifokorga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🩺", "label": "Shifokor"},
                    "correct_items": [
                        {"id": "stethoscope", "label": "Stetoskop", "icon": "Stethoscope"},
                        {"id": "syringe", "label": "Shprits", "icon": "Syringe"},
                        {"id": "pill", "label": "Dori", "icon": "Pill"},
                        {"id": "heart_pulse", "label": "Yurak monitori", "icon": "HeartPulse"},
                        {"id": "bandage", "label": "Bint", "icon": "Bandage"},
                        {"id": "thermometer", "label": "Termometr", "icon": "Thermometer"},
                    ],
                    "distractor_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "icon": "ChefHat"},
                        {"id": "wrench", "label": "Kalit", "icon": "Wrench"},
                        {"id": "telescope", "label": "Teleskop", "icon": "Telescope"},
                        {"id": "graduation_cap", "label": "Bitiruv qalpog'i", "icon": "GraduationCap"},
                    ],
                },
            },
            {
                "title": "Mexanik",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Mexanikga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔧", "label": "Mexanik"},
                    "correct_items": [
                        {"id": "wrench", "label": "Kalit", "icon": "Wrench"},
                        {"id": "cog", "label": "Tishli g'ildirak", "icon": "Cog"},
                        {"id": "battery", "label": "Akkumulyator", "icon": "BatteryCharging"},
                        {"id": "truck", "label": "Yuk mashinasi", "icon": "Truck"},
                        {"id": "gauge", "label": "O'lchagich", "icon": "Gauge"},
                        {"id": "toolbox", "label": "Asboblar qutisi", "icon": "Toolbox"},
                    ],
                    "distractor_items": [
                        {"id": "stethoscope", "label": "Stetoskop", "icon": "Stethoscope"},
                        {"id": "book", "label": "Kitob", "icon": "BookOpen"},
                        {"id": "microscope", "label": "Mikroskop", "icon": "Microscope"},
                        {"id": "shield", "label": "Qalqon", "icon": "Shield"},
                    ],
                },
            },
            {
                "title": "Quruvchi",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Quruvchiga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👷", "label": "Quruvchi"},
                    "correct_items": [
                        {"id": "hard_hat", "label": "Qattiq shlyapa", "icon": "HardHat"},
                        {"id": "hammer", "label": "Bolg'a", "icon": "Hammer"},
                        {"id": "ruler", "label": "Chizg'ich", "icon": "Ruler"},
                        {"id": "brick_wall", "label": "G'isht devor", "icon": "BrickWall"},
                        {"id": "construction", "label": "Qurilish belgisi", "icon": "Construction"},
                        {"id": "shovel", "label": "Belkurak", "icon": "Shovel"},
                    ],
                    "distractor_items": [
                        {"id": "syringe", "label": "Shprits", "icon": "Syringe"},
                        {"id": "keyboard", "label": "Klaviatura", "icon": "Keyboard"},
                        {"id": "fire", "label": "Olov", "icon": "Flame"},
                        {"id": "siren", "label": "Sirena", "icon": "Siren"},
                    ],
                },
            },
            {
                "title": "Tadqiqotchi",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Tadqiqotchiga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔬", "label": "Tadqiqotchi"},
                    "correct_items": [
                        {"id": "microscope", "label": "Mikroskop", "icon": "Microscope"},
                        {"id": "flask", "label": "Kolba", "icon": "FlaskConical"},
                        {"id": "test_tube", "label": "Probirka", "icon": "TestTube"},
                        {"id": "atom", "label": "Atom", "icon": "Atom"},
                        {"id": "telescope", "label": "Teleskop", "icon": "Telescope"},
                        {"id": "magnet", "label": "Magnit", "icon": "Magnet"},
                    ],
                    "distractor_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "icon": "ChefHat"},
                        {"id": "hammer", "label": "Bolg'a", "icon": "Hammer"},
                        {"id": "shield", "label": "Qalqon", "icon": "Shield"},
                        {"id": "pencil", "label": "Qalam", "icon": "Pencil"},
                    ],
                },
            },
            {
                "title": "Dasturchi",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Dasturchiga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "💻", "label": "Dasturchi"},
                    "correct_items": [
                        {"id": "laptop", "label": "Noutbuk", "icon": "Laptop"},
                        {"id": "keyboard", "label": "Klaviatura", "icon": "Keyboard"},
                        {"id": "monitor", "label": "Monitor", "icon": "Monitor"},
                        {"id": "code", "label": "Kod", "icon": "Code2"},
                        {"id": "cpu", "label": "Protsessor", "icon": "Cpu"},
                        {"id": "terminal", "label": "Terminal", "icon": "Terminal"},
                    ],
                    "distractor_items": [
                        {"id": "stethoscope", "label": "Stetoskop", "icon": "Stethoscope"},
                        {"id": "hard_hat", "label": "Qattiq shlyapa", "icon": "HardHat"},
                        {"id": "fire", "label": "Olov", "icon": "Flame"},
                        {"id": "graduation_cap", "label": "Bitiruv qalpog'i", "icon": "GraduationCap"},
                    ],
                },
            },
            {
                "title": "O'qituvchi",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "O'qituvchiga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👩‍🏫", "label": "O'qituvchi"},
                    "correct_items": [
                        {"id": "graduation_cap", "label": "Bitiruv qalpog'i", "icon": "GraduationCap"},
                        {"id": "textbook", "label": "Darslik", "icon": "BookMarked"},
                        {"id": "pen_tool", "label": "Qalam uchi", "icon": "PenTool"},
                        {"id": "pencil", "label": "Qalam", "icon": "Pencil"},
                        {"id": "backpack", "label": "Ryukzak", "icon": "Backpack"},
                        {"id": "apple", "label": "Olma", "icon": "Apple"},
                    ],
                    "distractor_items": [
                        {"id": "wrench", "label": "Kalit", "icon": "Wrench"},
                        {"id": "syringe", "label": "Shprits", "icon": "Syringe"},
                        {"id": "fire", "label": "Olov", "icon": "Flame"},
                        {"id": "car", "label": "Mashina", "icon": "CarFront"},
                    ],
                },
            },
            {
                "title": "Politsiyachi",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Politsiyachiga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👮", "label": "Politsiyachi"},
                    "correct_items": [
                        {"id": "shield", "label": "Qalqon", "icon": "Shield"},
                        {"id": "badge", "label": "Nishon", "icon": "BadgeCheck"},
                        {"id": "siren", "label": "Sirena", "icon": "Siren"},
                        {"id": "car", "label": "Politsiya mashinasi", "icon": "CarFront"},
                        {"id": "traffic_cone", "label": "Yo'l konusi", "icon": "TrafficCone"},
                        {"id": "hand", "label": "To'xta belgisi", "icon": "Hand"},
                    ],
                    "distractor_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "icon": "ChefHat"},
                        {"id": "textbook", "label": "Darslik", "icon": "BookMarked"},
                        {"id": "flask", "label": "Kolba", "icon": "FlaskConical"},
                        {"id": "hammer", "label": "Bolg'a", "icon": "Hammer"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Fasllar dunyosi",
        "description": "Fasllarga mos narsalarni top.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🍂",
        "color_accent": "#4DAA57",
        "display_order": 6,
        "is_published": True,
        "activities": [
            {
                "title": "Bahor",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Bahorga mos narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🌱", "label": "Bahor"},
                    "correct_items": [
                        {"id": "flower", "label": "Gul", "icon": "Flower"},
                        {"id": "tulip", "label": "Lola", "icon": "Flower2"},
                        {"id": "sprout", "label": "Nihol", "icon": "Sprout"},
                        {"id": "umbrella", "label": "Soyabon", "icon": "Umbrella"},
                        {"id": "rain_cloud", "label": "Yomg'irli bulut", "icon": "CloudRain"},
                        {"id": "rainbow", "label": "Kamalak", "icon": "Rainbow"},
                    ],
                    "distractor_items": [
                        {"id": "snowflake", "label": "Qor parchasi", "icon": "Snowflake"},
                        {"id": "ice_cream", "label": "Muzqaymoq", "icon": "IceCream"},
                        {"id": "leaf", "label": "Barg", "icon": "Leaf"},
                        {"id": "gift", "label": "Sovg'a", "icon": "Gift"},
                    ],
                },
            },
            {
                "title": "Yoz",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Yozga mos narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "☀️", "label": "Yoz"},
                    "correct_items": [
                        {"id": "sun", "label": "Quyosh", "icon": "Sun"},
                        {"id": "glasses", "label": "Ko'zoynak", "icon": "Glasses"},
                        {"id": "ice_cream", "label": "Muzqaymoq", "icon": "IceCream"},
                        {"id": "sailboat", "label": "Qayiq", "icon": "Sailboat"},
                        {"id": "droplets", "label": "Suv tomchilari", "icon": "Droplets"},
                        {"id": "footprints", "label": "Yalangoyoq izlar", "icon": "Footprints"},
                    ],
                    "distractor_items": [
                        {"id": "snowflake", "label": "Qor parchasi", "icon": "Snowflake"},
                        {"id": "umbrella", "label": "Soyabon", "icon": "Umbrella"},
                        {"id": "leaf", "label": "Barg", "icon": "Leaf"},
                        {"id": "tree_pine", "label": "Archa", "icon": "TreePine"},
                    ],
                },
            },
            {
                "title": "Kuz",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Kuzga mos narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🍂", "label": "Kuz"},
                    "correct_items": [
                        {"id": "leaf", "label": "Barg", "icon": "Leaf"},
                        {"id": "wind", "label": "Shamol", "icon": "Wind"},
                        {"id": "wheat", "label": "Bug'doy", "icon": "Wheat"},
                        {"id": "tree_deciduous", "label": "Yaproqli daraxt", "icon": "TreeDeciduous"},
                        {"id": "backpack", "label": "Maktab ryukzagi", "icon": "Backpack"},
                        {"id": "squirrel", "label": "Sincob", "icon": "Squirrel"},
                    ],
                    "distractor_items": [
                        {"id": "sun", "label": "Quyosh", "icon": "Sun"},
                        {"id": "flower", "label": "Gul", "icon": "Flower"},
                        {"id": "snowflake", "label": "Qor parchasi", "icon": "Snowflake"},
                        {"id": "ice_cream", "label": "Muzqaymoq", "icon": "IceCream"},
                    ],
                },
            },
            {
                "title": "Qish",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Qishga mos narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "❄️", "label": "Qish"},
                    "correct_items": [
                        {"id": "snowflake", "label": "Qor parchasi", "icon": "Snowflake"},
                        {"id": "cold_thermometer", "label": "Sovuq termometri", "icon": "ThermometerSnowflake"},
                        {"id": "gift", "label": "Sovg'a", "icon": "Gift"},
                        {"id": "tree_pine", "label": "Archa", "icon": "TreePine"},
                        {"id": "cloud_snow", "label": "Qorli bulut", "icon": "CloudSnow"},
                        {"id": "candy_cane", "label": "Konfet tayoqcha", "icon": "CandyCane"},
                    ],
                    "distractor_items": [
                        {"id": "sun", "label": "Quyosh", "icon": "Sun"},
                        {"id": "flower", "label": "Gul", "icon": "Flower"},
                        {"id": "leaf", "label": "Barg", "icon": "Leaf"},
                        {"id": "sprout", "label": "Nihol", "icon": "Sprout"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Hayvonot olami",
        "description": "Hayvonga kerakli narsalarni top.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🐾",
        "color_accent": "#FF8C69",
        "display_order": 7,
        "is_published": True,
        "activities": [
            {
                "title": "Mushuk",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Mushukka kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐱", "label": "Mushuk"},
                    "correct_items": [
                        {"id": "fish", "label": "Baliq", "icon": "Fish"},
                        {"id": "milk", "label": "Sut", "icon": "Milk"},
                        {"id": "mouse", "label": "Sichqon", "icon": "Mouse"},
                        {"id": "yarn", "label": "Yigiruv ipi", "icon": "Yarn"},
                        {"id": "paw", "label": "Panja izi", "icon": "PawPrint"},
                        {"id": "basket", "label": "Savatcha", "icon": "Basket"},
                    ],
                    "distractor_items": [
                        {"id": "bone", "label": "Suyak", "icon": "Bone"},
                        {"id": "carrot", "label": "Sabzi", "icon": "Carrot"},
                        {"id": "grass", "label": "O't", "icon": "Sprout"},
                        {"id": "meat", "label": "Go'sht", "icon": "Beef"},
                    ],
                },
            },
            {
                "title": "It",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Itga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐶", "label": "It"},
                    "correct_items": [
                        {"id": "bone", "label": "Suyak", "icon": "Bone"},
                        {"id": "tennis_ball", "label": "To'pcha", "icon": "Circle"},
                        {"id": "pet_bowl", "label": "Idishcha", "icon": "Soup"},
                        {"id": "doghouse", "label": "It uychasi", "icon": "Home"},
                        {"id": "paw", "label": "Panja izi", "icon": "PawPrint"},
                        {"id": "rope_toy", "label": "Arqoncha", "icon": "Knot"},
                    ],
                    "distractor_items": [
                        {"id": "fish", "label": "Baliq", "icon": "Fish"},
                        {"id": "cabbage", "label": "Karam", "icon": "Leafy"},
                        {"id": "cheese", "label": "Pishloq", "icon": "Sandwich"},
                        {"id": "peanut", "label": "Yeryong'oq", "icon": "Nut"},
                    ],
                },
            },
            {
                "title": "Sigir",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sigirga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐄", "label": "Sigir"},
                    "correct_items": [
                        {"id": "grass", "label": "O't", "icon": "Sprout"},
                        {"id": "milk", "label": "Sut", "icon": "Milk"},
                        {"id": "cheese", "label": "Pishloq", "icon": "Sandwich"},
                        {"id": "cowbell", "label": "Qo'ng'iroqcha", "icon": "Bell"},
                        {"id": "bucket", "label": "Chelak", "icon": "Container"},
                        {"id": "wheat", "label": "Pichan", "icon": "Wheat"},
                    ],
                    "distractor_items": [
                        {"id": "bone", "label": "Suyak", "icon": "Bone"},
                        {"id": "banana", "label": "Banan", "icon": "Banana"},
                        {"id": "crown", "label": "Toj", "icon": "Crown"},
                        {"id": "clover", "label": "Beda", "icon": "Clover"},
                    ],
                },
            },
            {
                "title": "Quyon",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Quyonga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐰", "label": "Quyon"},
                    "correct_items": [
                        {"id": "carrot", "label": "Sabzi", "icon": "Carrot"},
                        {"id": "cabbage", "label": "Karam", "icon": "Leafy"},
                        {"id": "clover", "label": "Beda", "icon": "Clover"},
                        {"id": "dandelion", "label": "Qoqio't", "icon": "Flower2"},
                        {"id": "hole", "label": "Uyacha", "icon": "CircleDashed"},
                        {"id": "sprout", "label": "Nihol", "icon": "Sprout"},
                    ],
                    "distractor_items": [
                        {"id": "fish", "label": "Baliq", "icon": "Fish"},
                        {"id": "tennis_ball", "label": "To'pcha", "icon": "Circle"},
                        {"id": "cheese", "label": "Pishloq", "icon": "Sandwich"},
                        {"id": "meat", "label": "Go'sht", "icon": "Beef"},
                    ],
                },
            },
            {
                "title": "Sher",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sherga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🦁", "label": "Sher"},
                    "correct_items": [
                        {"id": "meat", "label": "Go'sht", "icon": "Beef"},
                        {"id": "crown", "label": "Toj", "icon": "Crown"},
                        {"id": "grass", "label": "Savana o'ti", "icon": "Sprout"},
                        {"id": "paw", "label": "Panja izi", "icon": "PawPrint"},
                        {"id": "sun", "label": "Quyosh", "icon": "Sun"},
                        {"id": "hole", "label": "Uyasi", "icon": "CircleDashed"},
                    ],
                    "distractor_items": [
                        {"id": "milk", "label": "Sut", "icon": "Milk"},
                        {"id": "carrot", "label": "Sabzi", "icon": "Carrot"},
                        {"id": "peanut", "label": "Yeryong'oq", "icon": "Nut"},
                        {"id": "yarn", "label": "Yigiruv ipi", "icon": "Yarn"},
                    ],
                },
            },
            {
                "title": "Fil",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Filga kerakli narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐘", "label": "Fil"},
                    "correct_items": [
                        {"id": "peanut", "label": "Yeryong'oq", "icon": "Nut"},
                        {"id": "banana", "label": "Banan", "icon": "Banana"},
                        {"id": "droplets", "label": "Suv", "icon": "Droplets"},
                        {"id": "tree", "label": "Daraxt", "icon": "Trees"},
                        {"id": "grass", "label": "O't", "icon": "Sprout"},
                        {"id": "green_leaf", "label": "Barg", "icon": "Leaf"},
                    ],
                    "distractor_items": [
                        {"id": "bone", "label": "Suyak", "icon": "Bone"},
                        {"id": "cheese", "label": "Pishloq", "icon": "Sandwich"},
                        {"id": "crown", "label": "Toj", "icon": "Crown"},
                        {"id": "dandelion", "label": "Qoqio't", "icon": "Flower2"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Transport olami",
        "description": "Transport turini tanla va unga mos vositalarni top.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🚦",
        "color_accent": "#4DA6FF",
        "display_order": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Yer transporti",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Yerda yuradigan transportlarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🚗", "label": "Yer transporti"},
                    "correct_items": [
                        {"id": "sedan_car", "label": "Mashina", "icon": "Car"},
                        {"id": "bus", "label": "Avtobus", "icon": "Bus"},
                        {"id": "bicycle", "label": "Velosiped", "icon": "Bike"},
                        {"id": "train", "label": "Poyezd", "icon": "TrainFront"},
                        {"id": "motorcycle", "label": "Mototsikl", "icon": "Bike"},
                        {"id": "truck", "label": "Yuk mashinasi", "icon": "Truck"},
                    ],
                    "distractor_items": [
                        {"id": "sailboat", "label": "Yelkanli qayiq", "icon": "Sailboat"},
                        {"id": "airplane", "label": "Samolyot", "icon": "Plane"},
                        {"id": "cargo_ship", "label": "Kema", "icon": "Ship"},
                        {"id": "helicopter", "label": "Vertolyot", "icon": "Rotate3d"},
                    ],
                },
            },
            {
                "title": "Suv transporti",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Suvda yuradigan transportlarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "⛵", "label": "Suv transporti"},
                    "correct_items": [
                        {"id": "sailboat", "label": "Yelkanli qayiq", "icon": "Sailboat"},
                        {"id": "cargo_ship", "label": "Kema", "icon": "Ship"},
                        {"id": "speedboat", "label": "Tezyurar qayiq", "icon": "Sailboat"},
                        {"id": "canoe", "label": "Kanoe", "icon": "Sailboat"},
                        {"id": "ferry", "label": "Parom", "icon": "Ship"},
                        {"id": "anchor", "label": "Langar", "icon": "Anchor"},
                    ],
                    "distractor_items": [
                        {"id": "sedan_car", "label": "Mashina", "icon": "Car"},
                        {"id": "airplane", "label": "Samolyot", "icon": "Plane"},
                        {"id": "train", "label": "Poyezd", "icon": "TrainFront"},
                        {"id": "rocket", "label": "Raketa", "icon": "Rocket"},
                    ],
                },
            },
            {
                "title": "Havo transporti",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Havoda uchadigan transportlarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "✈️", "label": "Havo transporti"},
                    "correct_items": [
                        {"id": "airplane", "label": "Samolyot", "icon": "Plane"},
                        {"id": "helicopter", "label": "Vertolyot", "icon": "Rotate3d"},
                        {"id": "rocket", "label": "Raketa", "icon": "Rocket"},
                        {"id": "small_plane", "label": "Kichik samolyot", "icon": "Plane"},
                        {"id": "parachute", "label": "Parashyut", "icon": "Wind"},
                        {"id": "ufo", "label": "NUO", "icon": "Sparkle"},
                    ],
                    "distractor_items": [
                        {"id": "bus", "label": "Avtobus", "icon": "Bus"},
                        {"id": "cargo_ship", "label": "Kema", "icon": "Ship"},
                        {"id": "bicycle", "label": "Velosiped", "icon": "Bike"},
                        {"id": "canoe", "label": "Kanoe", "icon": "Sailboat"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Rang olami",
        "description": "Rangni tanla va unga mos narsalarni top.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🎨",
        "color_accent": "#FF6FA8",
        "display_order": 9,
        "is_published": True,
        "activities": [
            {
                "title": "Qizil",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Qizil rangdagi narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔴", "label": "Qizil"},
                    "correct_items": [
                        {"id": "apple", "label": "Olma", "icon": "Apple"},
                        {"id": "strawberry", "label": "Qulupnay", "icon": "Cherry"},
                        {"id": "cherry", "label": "Gilos", "icon": "Cherry"},
                        {"id": "heart", "label": "Yurak", "icon": "Heart"},
                        {"id": "fire_truck", "label": "O't o'chirish mashinasi", "icon": "Truck"},
                        {"id": "rose", "label": "Atirgul", "icon": "Flower"},
                    ],
                    "distractor_items": [
                        {"id": "banana", "label": "Banan", "icon": "Banana"},
                        {"id": "broccoli", "label": "Brokkoli", "icon": "Broccoli"},
                        {"id": "blueberries", "label": "Ko'kat rezavor", "icon": "Grape"},
                        {"id": "grapes", "label": "Uzum", "icon": "Grape"},
                    ],
                },
            },
            {
                "title": "Sariq",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sariq rangdagi narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🟡", "label": "Sariq"},
                    "correct_items": [
                        {"id": "banana", "label": "Banan", "icon": "Banana"},
                        {"id": "lemon", "label": "Limon", "icon": "Citrus"},
                        {"id": "sun", "label": "Quyosh", "icon": "Sun"},
                        {"id": "corn", "label": "Makkajo'xori", "icon": "Wheat"},
                        {"id": "chick", "label": "Jo'ja", "icon": "Bird"},
                        {"id": "star", "label": "Yulduz", "icon": "Star"},
                    ],
                    "distractor_items": [
                        {"id": "apple", "label": "Olma", "icon": "Apple"},
                        {"id": "cucumber", "label": "Bodring", "icon": "Salad"},
                        {"id": "blueberries", "label": "Ko'kat rezavor", "icon": "Grape"},
                        {"id": "cherry", "label": "Gilos", "icon": "Cherry"},
                    ],
                },
            },
            {
                "title": "Yashil",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Yashil rangdagi narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🟢", "label": "Yashil"},
                    "correct_items": [
                        {"id": "broccoli", "label": "Brokkoli", "icon": "Broccoli"},
                        {"id": "green_leaf", "label": "Barg", "icon": "Leaf"},
                        {"id": "tree", "label": "Daraxt", "icon": "Trees"},
                        {"id": "frog", "label": "Qurbaqa", "icon": "Turtle"},
                        {"id": "cucumber", "label": "Bodring", "icon": "Salad"},
                        {"id": "cactus", "label": "Kaktus", "icon": "Flower"},
                    ],
                    "distractor_items": [
                        {"id": "strawberry", "label": "Qulupnay", "icon": "Cherry"},
                        {"id": "banana", "label": "Banan", "icon": "Banana"},
                        {"id": "blueberries", "label": "Ko'kat rezavor", "icon": "Grape"},
                        {"id": "fire_truck", "label": "O't o'chirish mashinasi", "icon": "Truck"},
                    ],
                },
            },
            {
                "title": "Ko'k",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Ko'k rangdagi narsalarni top.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔵", "label": "Ko'k"},
                    "correct_items": [
                        {"id": "blueberries", "label": "Ko'kat rezavor", "icon": "Grape"},
                        {"id": "wave", "label": "To'lqin", "icon": "Waves"},
                        {"id": "whale", "label": "Kit", "icon": "Fish"},
                        {"id": "droplets", "label": "Suv tomchisi", "icon": "Droplets"},
                        {"id": "blue_bird", "label": "Qush", "icon": "Bird"},
                        {"id": "gem", "label": "Qimmatbaho tosh", "icon": "Gem"},
                    ],
                    "distractor_items": [
                        {"id": "apple", "label": "Olma", "icon": "Apple"},
                        {"id": "lemon", "label": "Limon", "icon": "Citrus"},
                        {"id": "cactus", "label": "Kaktus", "icon": "Flower"},
                        {"id": "strawberry", "label": "Qulupnay", "icon": "Cherry"},
                    ],
                },
            },
        ],
    },
]


async def _upsert_module(db, data: dict) -> EarlyModule:
    existing = (
        await db.execute(select(EarlyModule).where(EarlyModule.title == data["title"]))
    ).scalar_one_or_none()
    if existing is None:
        existing = EarlyModule(instructor_id=INSTRUCTOR_ID)
        db.add(existing)
    existing.description = data["description"]
    existing.subject = data["subject"]
    existing.icon_emoji = data["icon_emoji"]
    existing.color_accent = data["color_accent"]
    existing.display_order = data["display_order"]
    existing.title = data["title"]
    # Draft modules (literacy/math/logic/creative above) intentionally stay
    # is_published=False pending real media. The matching-game packs below
    # are icon-based (no missing assets) and ship complete, so they opt in
    # via this flag instead.
    existing.is_published = data.get("is_published", False)
    await db.flush()  # populate .id for a brand-new row
    return existing


async def _upsert_activity(db, module_id: int, order: int, data: dict, is_published: bool = False) -> None:
    existing = (
        await db.execute(
            select(EarlyActivity).where(
                EarlyActivity.module_id == module_id,
                EarlyActivity.title == data["title"],
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = EarlyActivity(module_id=module_id)
        db.add(existing)
    existing.title = data["title"]
    existing.order = order
    existing.activity_type = data["activity_type"]
    existing.instruction_text = data["instruction_text"]
    existing.content_json = json.dumps(_with_emoji(data["content"]), ensure_ascii=False)
    # Activities publish along with their module — this pack has no
    # per-activity draft state (unlike the module-level literacy/math/etc.
    # drafts, every activity here ships complete in one pass).
    existing.is_published = is_published


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all,
            tables=[
                EarlyModule.__table__,
                EarlyActivity.__table__,
                EarlyActivityCompletion.__table__,
            ],
        )

    modules_written = 0
    activities_written = 0
    async with AsyncSessionLocal() as db:
        for mod_data in MODULES:
            module = await _upsert_module(db, mod_data)
            modules_written += 1
            for i, act_data in enumerate(mod_data["activities"]):
                await _upsert_activity(db, module.id, i, act_data, is_published=mod_data.get("is_published", False))
                activities_written += 1
        await db.commit()

    print(f"wrote {modules_written} modules, {activities_written} activities "
          f"(publish state follows each module — drafts stay unpublished "
          f"pending media, the icon-based matching packs publish complete)")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
