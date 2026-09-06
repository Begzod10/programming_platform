"""One-off: seed the initial "early learner" (age 4-6) catalog — 4 draft
modules covering literacy/math/logic/creative (each a first pass, left
unpublished pending real media), plus 8 complete, published packs that use
emoji-first, icon-based content instead of image assets: 5 tap-to-match
("Kasblar shaharchasi" / "Fasllar dunyosi" / "Hayvonot olami" /
"Transport olami" / "Rang olami", content.mode="select"), 1
drag-to-assemble ("Yasash o'yinlari", content.mode="build"), 1
trace-the-outline ("Chizib o'rganamiz", content.mode="trace"), and 1
arrow-pathfinding maze ("Yo'lni topamiz", content.mode="maze"). See
project_student_platform memory / early_learning.py for the model design
rationale (no AI grading, star-based completion instead of points).

Every module/activity/item is authored in Uzbek first (title/description/
instruction_text/label — matches EarlyModule.source_lang's default) with a
Russian rendering alongside it (title_ru/description_ru/instruction_text_ru/
label_ru) — see early_learning.py's endpoint, which picks whichever the
request's ?lang asks for and falls back to uz when a ru field is missing.
The 4 draft modules only get title_ru/description_ru/activity title_ru —
their content_json bodies (letter tracing, number sequences, sort buckets...)
are left uz-only for now: they're unpublished and each activity_type shapes
its content differently, so translating them is its own pass, not something
that piggybacks on the matching-game packs' per-item label_ru convention.

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
# isn't recognizable enough at a glance, and the label under it is useless
# to a non-reader. Emoji are colorful, high-contrast, and kids recognize
# them without reading — so every `match`/select item also gets an `emoji`,
# keyed once here by item id rather than repeated inline (the same id shows
# up as a distractor in several other activities, and it must render
# identically everywhere it appears — unlike `label`/`label_ru`, which do
# occasionally vary by context, e.g. "grass" reads "Трава" for a cat but
# "Трава саванны" for a lion, so those stay authored inline per item).
# `icon` stays as a fallback for any id this dict doesn't cover.
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
        "title_ru": "Путешествие по буквам",
        "description": "Harflarni tanish, tovushlarni ajratish va birinchi so'zlar.",
        "description_ru": "Знакомство с буквами, различение звуков и первые слова.",
        "subject": EarlySubject.literacy,
        "icon_emoji": "🔤",
        "color_accent": "#FF6B6B",
        "display_order": 1,
        "activities": [
            {
                "title": "A dan D gacha — chizib yozamiz",
                "title_ru": "От А до D — обводим буквы",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Barmog'ing bilan harfni chiz.",
                "instruction_text_ru": "Обведи букву пальцем.",
                "content": {"targets": [
                    {"letter": "A", "outline_url": None},
                    {"letter": "B", "outline_url": None},
                    {"letter": "C", "outline_url": None},
                    {"letter": "D", "outline_url": None},
                ]},
            },
            {
                "title": "Tovush va rasm — moslashtir",
                "title_ru": "Соедини звук и картинку",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Harfni to'g'ri rasmga ulash.",
                "instruction_text_ru": "Соедини букву с правильной картинкой.",
                "content": {"pairs": [
                    {"left": "B", "right": "Bola", "image_url": None},
                    {"left": "M", "right": "Mushuk", "image_url": None},
                    {"left": "O", "right": "Olma", "image_url": None},
                ]},
            },
            {
                "title": "Ertak tinglaymiz",
                "title_ru": "Слушаем сказку",
                "activity_type": EarlyActivityType.audio_story,
                "instruction_text": None,
                "instruction_text_ru": None,
                "content": {
                    "text": "Kichkina quyoncha o'rmonda sayr qilib yurardi...",
                    "audio_url": None,
                    "image_url": None,
                },
            },
            {
                "title": "Harfiga qarab ajrat",
                "title_ru": "Раздели по первой букве",
                "activity_type": EarlyActivityType.sort,
                "instruction_text": "Rasmlarni boshlang'ich harfiga qarab joylashtir.",
                "instruction_text_ru": "Расставь картинки по первой букве.",
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
        "title_ru": "Мир чисел",
        "description": "Sanash, shakllarni solishtirish va oddiy tartib.",
        "description_ru": "Счёт, сравнение фигур и простой порядок.",
        "subject": EarlySubject.math,
        "icon_emoji": "🔢",
        "color_accent": "#4D96FF",
        "display_order": 2,
        "activities": [
            {
                "title": "Sanab ko'ramiz",
                "title_ru": "Посчитаем",
                "activity_type": EarlyActivityType.count,
                "instruction_text": "Nechta olma borligini sanab, to'g'ri sonni bos.",
                "instruction_text_ru": "Посчитай, сколько яблок, и нажми правильное число.",
                "content": {"object_image_url": None, "count": 4, "options": [3, 4, 5]},
            },
            {
                "title": "Kattami, kichikmi?",
                "title_ru": "Большой или маленький?",
                "activity_type": EarlyActivityType.sort,
                "instruction_text": "Shakllarni kattaligiga qarab joylashtir.",
                "instruction_text_ru": "Расставь фигуры по размеру.",
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
                "title_ru": "Соедини число и количество",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sonni tegishli miqdordagi rasmga ulang.",
                "instruction_text_ru": "Соедини число с нужным количеством картинок.",
                "content": {"pairs": [
                    {"left": "1", "right": "1 ta olma", "image_url": None},
                    {"left": "2", "right": "2 ta olma", "image_url": None},
                    {"left": "3", "right": "3 ta olma", "image_url": None},
                ]},
            },
            {
                "title": "1 dan 5 gacha tartibla",
                "title_ru": "Расставь от 1 до 5",
                "activity_type": EarlyActivityType.sequence,
                "instruction_text": "Sonlarni to'g'ri tartibda joylashtir.",
                "instruction_text_ru": "Расставь числа в правильном порядке.",
                "content": {"correct_order": [1, 2, 3, 4, 5], "shuffled": [3, 1, 5, 2, 4]},
            },
        ],
    },
    {
        "title": "Fikrlash o'yinlari",
        "title_ru": "Игры на мышление",
        "description": "Ketma-ketlik, naqshlar va yo'l topish.",
        "description_ru": "Последовательности, узоры и поиск пути.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🧩",
        "color_accent": "#9B5DE5",
        "display_order": 3,
        "activities": [
            {
                "title": "Kunlik tartib",
                "title_ru": "Распорядок дня",
                "activity_type": EarlyActivityType.sequence,
                "instruction_text": "Kun tartibini to'g'ri ketma-ketlikda joylashtir.",
                "instruction_text_ru": "Расставь распорядок дня в правильном порядке.",
                "content": {
                    "correct_order": ["Uyg'onish", "Tishlarni yuvish", "Nonushta", "Kiyinish"],
                    "shuffled": ["Kiyinish", "Uyg'onish", "Nonushta", "Tishlarni yuvish"],
                },
            },
            {
                "title": "Yo'lni top",
                "title_ru": "Найди путь",
                "activity_type": EarlyActivityType.maze,
                "instruction_text": "O'qlar yordamida boshidan oxirigacha yo'l top.",
                "instruction_text_ru": "С помощью стрелок найди путь от начала до конца.",
                "content": {"grid_size": [5, 5], "start": [0, 0], "end": [4, 4], "walls": []},
            },
            {
                "title": "Naqshni davom ettir",
                "title_ru": "Продолжи узор",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Naqshdagi keyingi rangni top.",
                "instruction_text_ru": "Найди следующий цвет в узоре.",
                "content": {"pattern": ["red", "blue", "red", "blue", "?"], "options": ["red", "blue", "green"], "answer": "red"},
            },
        ],
    },
    {
        "title": "Ijodkorlik burchagi",
        "title_ru": "Уголок творчества",
        "description": "Bo'yash va shakllarni chizish.",
        "description_ru": "Раскрашивание и рисование фигур.",
        "subject": EarlySubject.creative,
        "icon_emoji": "🎨",
        "color_accent": "#FFB84D",
        "display_order": 4,
        "activities": [
            {
                "title": "Erkin bo'yash",
                "title_ru": "Свободное раскрашивание",
                "activity_type": EarlyActivityType.coloring,
                "instruction_text": "Xohlagan rangda bo'ya.",
                "instruction_text_ru": "Раскрась любым цветом.",
                "content": {"templates": [
                    {"id": 1, "outline_url": None},
                    {"id": 2, "outline_url": None},
                    {"id": 3, "outline_url": None},
                ]},
            },
            {
                "title": "Shakllarni chizamiz",
                "title_ru": "Рисуем фигуры",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Shaklni barmog'ing bilan chiz.",
                "instruction_text_ru": "Обведи фигуру пальцем.",
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
        "title_ru": "Город профессий",
        "description": "Kasbni tanla va unga kerakli asboblarni top.",
        "description_ru": "Выбери профессию и найди нужные ей инструменты.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🏙️",
        "color_accent": "#FF9F40",
        "display_order": 5,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Oshpaz",
                "title_ru": "Повар",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Oshpazga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно повару.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👨‍🍳", "label": "Oshpaz", "label_ru": "Повар"},
                    "correct_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "label_ru": "Колпак повара", "icon": "ChefHat"},
                        {"id": "recipe_book", "label": "Retsept kitobi", "label_ru": "Книга рецептов", "icon": "BookOpen"},
                        {"id": "mixing_bowl", "label": "Aralashtirish kosasi", "label_ru": "Миска для смешивания", "icon": "CookingPot"},
                        {"id": "chef_knife", "label": "Oshpaz pichog'i", "label_ru": "Нож повара", "icon": "UtensilsCrossed"},
                        {"id": "fire", "label": "Olov", "label_ru": "Огонь", "icon": "Flame"},
                        {"id": "soup_pot", "label": "Sho'rva qozoni", "label_ru": "Кастрюля с супом", "icon": "Soup"},
                    ],
                    "distractor_items": [
                        {"id": "keyboard", "label": "Klaviatura", "label_ru": "Клавиатура", "icon": "Keyboard"},
                        {"id": "stethoscope", "label": "Stetoskop", "label_ru": "Стетоскоп", "icon": "Stethoscope"},
                        {"id": "hammer", "label": "Bolg'a", "label_ru": "Молоток", "icon": "Hammer"},
                        {"id": "shield", "label": "Qalqon", "label_ru": "Щит", "icon": "Shield"},
                    ],
                },
            },
            {
                "title": "Shifokor",
                "title_ru": "Врач",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Shifokorga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно врачу.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🩺", "label": "Shifokor", "label_ru": "Врач"},
                    "correct_items": [
                        {"id": "stethoscope", "label": "Stetoskop", "label_ru": "Стетоскоп", "icon": "Stethoscope"},
                        {"id": "syringe", "label": "Shprits", "label_ru": "Шприц", "icon": "Syringe"},
                        {"id": "pill", "label": "Dori", "label_ru": "Таблетка", "icon": "Pill"},
                        {"id": "heart_pulse", "label": "Yurak monitori", "label_ru": "Монитор сердца", "icon": "HeartPulse"},
                        {"id": "bandage", "label": "Bint", "label_ru": "Бинт", "icon": "Bandage"},
                        {"id": "thermometer", "label": "Termometr", "label_ru": "Термометр", "icon": "Thermometer"},
                    ],
                    "distractor_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "label_ru": "Колпак повара", "icon": "ChefHat"},
                        {"id": "wrench", "label": "Kalit", "label_ru": "Гаечный ключ", "icon": "Wrench"},
                        {"id": "telescope", "label": "Teleskop", "label_ru": "Телескоп", "icon": "Telescope"},
                        {"id": "graduation_cap", "label": "Bitiruv qalpog'i", "label_ru": "Выпускная шапочка", "icon": "GraduationCap"},
                    ],
                },
            },
            {
                "title": "Mexanik",
                "title_ru": "Механик",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Mexanikga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно механику.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔧", "label": "Mexanik", "label_ru": "Механик"},
                    "correct_items": [
                        {"id": "wrench", "label": "Kalit", "label_ru": "Гаечный ключ", "icon": "Wrench"},
                        {"id": "cog", "label": "Tishli g'ildirak", "label_ru": "Шестерёнка", "icon": "Cog"},
                        {"id": "battery", "label": "Akkumulyator", "label_ru": "Аккумулятор", "icon": "BatteryCharging"},
                        {"id": "truck", "label": "Yuk mashinasi", "label_ru": "Грузовик", "icon": "Truck"},
                        {"id": "gauge", "label": "O'lchagich", "label_ru": "Прибор измерения", "icon": "Gauge"},
                        {"id": "toolbox", "label": "Asboblar qutisi", "label_ru": "Ящик с инструментами", "icon": "Toolbox"},
                    ],
                    "distractor_items": [
                        {"id": "stethoscope", "label": "Stetoskop", "label_ru": "Стетоскоп", "icon": "Stethoscope"},
                        {"id": "book", "label": "Kitob", "label_ru": "Книга", "icon": "BookOpen"},
                        {"id": "microscope", "label": "Mikroskop", "label_ru": "Микроскоп", "icon": "Microscope"},
                        {"id": "shield", "label": "Qalqon", "label_ru": "Щит", "icon": "Shield"},
                    ],
                },
            },
            {
                "title": "Quruvchi",
                "title_ru": "Строитель",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Quruvchiga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно строителю.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👷", "label": "Quruvchi", "label_ru": "Строитель"},
                    "correct_items": [
                        {"id": "hard_hat", "label": "Qattiq shlyapa", "label_ru": "Каска", "icon": "HardHat"},
                        {"id": "hammer", "label": "Bolg'a", "label_ru": "Молоток", "icon": "Hammer"},
                        {"id": "ruler", "label": "Chizg'ich", "label_ru": "Линейка", "icon": "Ruler"},
                        {"id": "brick_wall", "label": "G'isht devor", "label_ru": "Кирпичная стена", "icon": "BrickWall"},
                        {"id": "construction", "label": "Qurilish belgisi", "label_ru": "Знак стройки", "icon": "Construction"},
                        {"id": "shovel", "label": "Belkurak", "label_ru": "Лопата", "icon": "Shovel"},
                    ],
                    "distractor_items": [
                        {"id": "syringe", "label": "Shprits", "label_ru": "Шприц", "icon": "Syringe"},
                        {"id": "keyboard", "label": "Klaviatura", "label_ru": "Клавиатура", "icon": "Keyboard"},
                        {"id": "fire", "label": "Olov", "label_ru": "Огонь", "icon": "Flame"},
                        {"id": "siren", "label": "Sirena", "label_ru": "Сирена", "icon": "Siren"},
                    ],
                },
            },
            {
                "title": "Tadqiqotchi",
                "title_ru": "Учёный",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Tadqiqotchiga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно учёному.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔬", "label": "Tadqiqotchi", "label_ru": "Учёный"},
                    "correct_items": [
                        {"id": "microscope", "label": "Mikroskop", "label_ru": "Микроскоп", "icon": "Microscope"},
                        {"id": "flask", "label": "Kolba", "label_ru": "Колба", "icon": "FlaskConical"},
                        {"id": "test_tube", "label": "Probirka", "label_ru": "Пробирка", "icon": "TestTube"},
                        {"id": "atom", "label": "Atom", "label_ru": "Атом", "icon": "Atom"},
                        {"id": "telescope", "label": "Teleskop", "label_ru": "Телескоп", "icon": "Telescope"},
                        {"id": "magnet", "label": "Magnit", "label_ru": "Магнит", "icon": "Magnet"},
                    ],
                    "distractor_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "label_ru": "Колпак повара", "icon": "ChefHat"},
                        {"id": "hammer", "label": "Bolg'a", "label_ru": "Молоток", "icon": "Hammer"},
                        {"id": "shield", "label": "Qalqon", "label_ru": "Щит", "icon": "Shield"},
                        {"id": "pencil", "label": "Qalam", "label_ru": "Карандаш", "icon": "Pencil"},
                    ],
                },
            },
            {
                "title": "Dasturchi",
                "title_ru": "Программист",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Dasturchiga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно программисту.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "💻", "label": "Dasturchi", "label_ru": "Программист"},
                    "correct_items": [
                        {"id": "laptop", "label": "Noutbuk", "label_ru": "Ноутбук", "icon": "Laptop"},
                        {"id": "keyboard", "label": "Klaviatura", "label_ru": "Клавиатура", "icon": "Keyboard"},
                        {"id": "monitor", "label": "Monitor", "label_ru": "Монитор", "icon": "Monitor"},
                        {"id": "code", "label": "Kod", "label_ru": "Код", "icon": "Code2"},
                        {"id": "cpu", "label": "Protsessor", "label_ru": "Процессор", "icon": "Cpu"},
                        {"id": "terminal", "label": "Terminal", "label_ru": "Терминал", "icon": "Terminal"},
                    ],
                    "distractor_items": [
                        {"id": "stethoscope", "label": "Stetoskop", "label_ru": "Стетоскоп", "icon": "Stethoscope"},
                        {"id": "hard_hat", "label": "Qattiq shlyapa", "label_ru": "Каска", "icon": "HardHat"},
                        {"id": "fire", "label": "Olov", "label_ru": "Огонь", "icon": "Flame"},
                        {"id": "graduation_cap", "label": "Bitiruv qalpog'i", "label_ru": "Выпускная шапочка", "icon": "GraduationCap"},
                    ],
                },
            },
            {
                "title": "O'qituvchi",
                "title_ru": "Учитель",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "O'qituvchiga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно учителю.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👩‍🏫", "label": "O'qituvchi", "label_ru": "Учитель"},
                    "correct_items": [
                        {"id": "graduation_cap", "label": "Bitiruv qalpog'i", "label_ru": "Выпускная шапочка", "icon": "GraduationCap"},
                        {"id": "textbook", "label": "Darslik", "label_ru": "Учебник", "icon": "BookMarked"},
                        {"id": "pen_tool", "label": "Qalam uchi", "label_ru": "Перо", "icon": "PenTool"},
                        {"id": "pencil", "label": "Qalam", "label_ru": "Карандаш", "icon": "Pencil"},
                        {"id": "backpack", "label": "Ryukzak", "label_ru": "Рюкзак", "icon": "Backpack"},
                        {"id": "apple", "label": "Olma", "label_ru": "Яблоко", "icon": "Apple"},
                    ],
                    "distractor_items": [
                        {"id": "wrench", "label": "Kalit", "label_ru": "Гаечный ключ", "icon": "Wrench"},
                        {"id": "syringe", "label": "Shprits", "label_ru": "Шприц", "icon": "Syringe"},
                        {"id": "fire", "label": "Olov", "label_ru": "Огонь", "icon": "Flame"},
                        {"id": "car", "label": "Mashina", "label_ru": "Машина", "icon": "CarFront"},
                    ],
                },
            },
            {
                "title": "Politsiyachi",
                "title_ru": "Полицейский",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Politsiyachiga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно полицейскому.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "👮", "label": "Politsiyachi", "label_ru": "Полицейский"},
                    "correct_items": [
                        {"id": "shield", "label": "Qalqon", "label_ru": "Щит", "icon": "Shield"},
                        {"id": "badge", "label": "Nishon", "label_ru": "Значок", "icon": "BadgeCheck"},
                        {"id": "siren", "label": "Sirena", "label_ru": "Сирена", "icon": "Siren"},
                        {"id": "car", "label": "Politsiya mashinasi", "label_ru": "Полицейская машина", "icon": "CarFront"},
                        {"id": "traffic_cone", "label": "Yo'l konusi", "label_ru": "Дорожный конус", "icon": "TrafficCone"},
                        {"id": "hand", "label": "To'xta belgisi", "label_ru": "Знак «стоп»", "icon": "Hand"},
                    ],
                    "distractor_items": [
                        {"id": "chef_hat", "label": "Oshpaz qalpog'i", "label_ru": "Колпак повара", "icon": "ChefHat"},
                        {"id": "textbook", "label": "Darslik", "label_ru": "Учебник", "icon": "BookMarked"},
                        {"id": "flask", "label": "Kolba", "label_ru": "Колба", "icon": "FlaskConical"},
                        {"id": "hammer", "label": "Bolg'a", "label_ru": "Молоток", "icon": "Hammer"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Fasllar dunyosi",
        "title_ru": "Мир времён года",
        "description": "Fasllarga mos narsalarni top.",
        "description_ru": "Найди то, что подходит каждому времени года.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🍂",
        "color_accent": "#4DAA57",
        "display_order": 6,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Bahor",
                "title_ru": "Весна",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Bahorga mos narsalarni top.",
                "instruction_text_ru": "Найди то, что подходит весне.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🌱", "label": "Bahor", "label_ru": "Весна"},
                    "correct_items": [
                        {"id": "flower", "label": "Gul", "label_ru": "Цветок", "icon": "Flower"},
                        {"id": "tulip", "label": "Lola", "label_ru": "Тюльпан", "icon": "Flower2"},
                        {"id": "sprout", "label": "Nihol", "label_ru": "Росток", "icon": "Sprout"},
                        {"id": "umbrella", "label": "Soyabon", "label_ru": "Зонт", "icon": "Umbrella"},
                        {"id": "rain_cloud", "label": "Yomg'irli bulut", "label_ru": "Дождевое облако", "icon": "CloudRain"},
                        {"id": "rainbow", "label": "Kamalak", "label_ru": "Радуга", "icon": "Rainbow"},
                    ],
                    "distractor_items": [
                        {"id": "snowflake", "label": "Qor parchasi", "label_ru": "Снежинка", "icon": "Snowflake"},
                        {"id": "ice_cream", "label": "Muzqaymoq", "label_ru": "Мороженое", "icon": "IceCream"},
                        {"id": "leaf", "label": "Barg", "label_ru": "Лист", "icon": "Leaf"},
                        {"id": "gift", "label": "Sovg'a", "label_ru": "Подарок", "icon": "Gift"},
                    ],
                },
            },
            {
                "title": "Yoz",
                "title_ru": "Лето",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Yozga mos narsalarni top.",
                "instruction_text_ru": "Найди то, что подходит лету.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "☀️", "label": "Yoz", "label_ru": "Лето"},
                    "correct_items": [
                        {"id": "sun", "label": "Quyosh", "label_ru": "Солнце", "icon": "Sun"},
                        {"id": "glasses", "label": "Ko'zoynak", "label_ru": "Очки", "icon": "Glasses"},
                        {"id": "ice_cream", "label": "Muzqaymoq", "label_ru": "Мороженое", "icon": "IceCream"},
                        {"id": "sailboat", "label": "Qayiq", "label_ru": "Лодка", "icon": "Sailboat"},
                        {"id": "droplets", "label": "Suv tomchilari", "label_ru": "Капли воды", "icon": "Droplets"},
                        {"id": "footprints", "label": "Yalangoyoq izlar", "label_ru": "Следы босых ног", "icon": "Footprints"},
                    ],
                    "distractor_items": [
                        {"id": "snowflake", "label": "Qor parchasi", "label_ru": "Снежинка", "icon": "Snowflake"},
                        {"id": "umbrella", "label": "Soyabon", "label_ru": "Зонт", "icon": "Umbrella"},
                        {"id": "leaf", "label": "Barg", "label_ru": "Лист", "icon": "Leaf"},
                        {"id": "tree_pine", "label": "Archa", "label_ru": "Ель", "icon": "TreePine"},
                    ],
                },
            },
            {
                "title": "Kuz",
                "title_ru": "Осень",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Kuzga mos narsalarni top.",
                "instruction_text_ru": "Найди то, что подходит осени.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🍂", "label": "Kuz", "label_ru": "Осень"},
                    "correct_items": [
                        {"id": "leaf", "label": "Barg", "label_ru": "Лист", "icon": "Leaf"},
                        {"id": "wind", "label": "Shamol", "label_ru": "Ветер", "icon": "Wind"},
                        {"id": "wheat", "label": "Bug'doy", "label_ru": "Пшеница", "icon": "Wheat"},
                        {"id": "tree_deciduous", "label": "Yaproqli daraxt", "label_ru": "Лиственное дерево", "icon": "TreeDeciduous"},
                        {"id": "backpack", "label": "Maktab ryukzagi", "label_ru": "Школьный рюкзак", "icon": "Backpack"},
                        {"id": "squirrel", "label": "Sincob", "label_ru": "Белка", "icon": "Squirrel"},
                    ],
                    "distractor_items": [
                        {"id": "sun", "label": "Quyosh", "label_ru": "Солнце", "icon": "Sun"},
                        {"id": "flower", "label": "Gul", "label_ru": "Цветок", "icon": "Flower"},
                        {"id": "snowflake", "label": "Qor parchasi", "label_ru": "Снежинка", "icon": "Snowflake"},
                        {"id": "ice_cream", "label": "Muzqaymoq", "label_ru": "Мороженое", "icon": "IceCream"},
                    ],
                },
            },
            {
                "title": "Qish",
                "title_ru": "Зима",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Qishga mos narsalarni top.",
                "instruction_text_ru": "Найди то, что подходит зиме.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "❄️", "label": "Qish", "label_ru": "Зима"},
                    "correct_items": [
                        {"id": "snowflake", "label": "Qor parchasi", "label_ru": "Снежинка", "icon": "Snowflake"},
                        {"id": "cold_thermometer", "label": "Sovuq termometri", "label_ru": "Термометр холода", "icon": "ThermometerSnowflake"},
                        {"id": "gift", "label": "Sovg'a", "label_ru": "Подарок", "icon": "Gift"},
                        {"id": "tree_pine", "label": "Archa", "label_ru": "Ель", "icon": "TreePine"},
                        {"id": "cloud_snow", "label": "Qorli bulut", "label_ru": "Снежное облако", "icon": "CloudSnow"},
                        {"id": "candy_cane", "label": "Konfet tayoqcha", "label_ru": "Леденец-трость", "icon": "CandyCane"},
                    ],
                    "distractor_items": [
                        {"id": "sun", "label": "Quyosh", "label_ru": "Солнце", "icon": "Sun"},
                        {"id": "flower", "label": "Gul", "label_ru": "Цветок", "icon": "Flower"},
                        {"id": "leaf", "label": "Barg", "label_ru": "Лист", "icon": "Leaf"},
                        {"id": "sprout", "label": "Nihol", "label_ru": "Росток", "icon": "Sprout"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Hayvonot olami",
        "title_ru": "Мир животных",
        "description": "Hayvonga kerakli narsalarni top.",
        "description_ru": "Найди то, что нужно животному.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🐾",
        "color_accent": "#FF8C69",
        "display_order": 7,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Mushuk",
                "title_ru": "Кошка",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Mushukka kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно кошке.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐱", "label": "Mushuk", "label_ru": "Кошка"},
                    "correct_items": [
                        {"id": "fish", "label": "Baliq", "label_ru": "Рыба", "icon": "Fish"},
                        {"id": "milk", "label": "Sut", "label_ru": "Молоко", "icon": "Milk"},
                        {"id": "mouse", "label": "Sichqon", "label_ru": "Мышь", "icon": "Mouse"},
                        {"id": "yarn", "label": "Yigiruv ipi", "label_ru": "Клубок ниток", "icon": "Yarn"},
                        {"id": "paw", "label": "Panja izi", "label_ru": "След лапы", "icon": "PawPrint"},
                        {"id": "basket", "label": "Savatcha", "label_ru": "Корзинка", "icon": "Basket"},
                    ],
                    "distractor_items": [
                        {"id": "bone", "label": "Suyak", "label_ru": "Кость", "icon": "Bone"},
                        {"id": "carrot", "label": "Sabzi", "label_ru": "Морковь", "icon": "Carrot"},
                        {"id": "grass", "label": "O't", "label_ru": "Трава", "icon": "Sprout"},
                        {"id": "meat", "label": "Go'sht", "label_ru": "Мясо", "icon": "Beef"},
                    ],
                },
            },
            {
                "title": "It",
                "title_ru": "Собака",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Itga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно собаке.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐶", "label": "It", "label_ru": "Собака"},
                    "correct_items": [
                        {"id": "bone", "label": "Suyak", "label_ru": "Кость", "icon": "Bone"},
                        {"id": "tennis_ball", "label": "To'pcha", "label_ru": "Мячик", "icon": "Circle"},
                        {"id": "pet_bowl", "label": "Idishcha", "label_ru": "Миска", "icon": "Soup"},
                        {"id": "doghouse", "label": "It uychasi", "label_ru": "Будка", "icon": "Home"},
                        {"id": "paw", "label": "Panja izi", "label_ru": "След лапы", "icon": "PawPrint"},
                        {"id": "rope_toy", "label": "Arqoncha", "label_ru": "Верёвочная игрушка", "icon": "Knot"},
                    ],
                    "distractor_items": [
                        {"id": "fish", "label": "Baliq", "label_ru": "Рыба", "icon": "Fish"},
                        {"id": "cabbage", "label": "Karam", "label_ru": "Капуста", "icon": "Leafy"},
                        {"id": "cheese", "label": "Pishloq", "label_ru": "Сыр", "icon": "Sandwich"},
                        {"id": "peanut", "label": "Yeryong'oq", "label_ru": "Арахис", "icon": "Nut"},
                    ],
                },
            },
            {
                "title": "Sigir",
                "title_ru": "Корова",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sigirga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно корове.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐄", "label": "Sigir", "label_ru": "Корова"},
                    "correct_items": [
                        {"id": "grass", "label": "O't", "label_ru": "Трава", "icon": "Sprout"},
                        {"id": "milk", "label": "Sut", "label_ru": "Молоко", "icon": "Milk"},
                        {"id": "cheese", "label": "Pishloq", "label_ru": "Сыр", "icon": "Sandwich"},
                        {"id": "cowbell", "label": "Qo'ng'iroqcha", "label_ru": "Колокольчик", "icon": "Bell"},
                        {"id": "bucket", "label": "Chelak", "label_ru": "Ведро", "icon": "Container"},
                        {"id": "wheat", "label": "Pichan", "label_ru": "Сено", "icon": "Wheat"},
                    ],
                    "distractor_items": [
                        {"id": "bone", "label": "Suyak", "label_ru": "Кость", "icon": "Bone"},
                        {"id": "banana", "label": "Banan", "label_ru": "Банан", "icon": "Banana"},
                        {"id": "crown", "label": "Toj", "label_ru": "Корона", "icon": "Crown"},
                        {"id": "clover", "label": "Beda", "label_ru": "Клевер", "icon": "Clover"},
                    ],
                },
            },
            {
                "title": "Quyon",
                "title_ru": "Кролик",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Quyonga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно кролику.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐰", "label": "Quyon", "label_ru": "Кролик"},
                    "correct_items": [
                        {"id": "carrot", "label": "Sabzi", "label_ru": "Морковь", "icon": "Carrot"},
                        {"id": "cabbage", "label": "Karam", "label_ru": "Капуста", "icon": "Leafy"},
                        {"id": "clover", "label": "Beda", "label_ru": "Клевер", "icon": "Clover"},
                        {"id": "dandelion", "label": "Qoqio't", "label_ru": "Одуванчик", "icon": "Flower2"},
                        {"id": "hole", "label": "Uyacha", "label_ru": "Норка", "icon": "CircleDashed"},
                        {"id": "sprout", "label": "Nihol", "label_ru": "Росток", "icon": "Sprout"},
                    ],
                    "distractor_items": [
                        {"id": "fish", "label": "Baliq", "label_ru": "Рыба", "icon": "Fish"},
                        {"id": "tennis_ball", "label": "To'pcha", "label_ru": "Мячик", "icon": "Circle"},
                        {"id": "cheese", "label": "Pishloq", "label_ru": "Сыр", "icon": "Sandwich"},
                        {"id": "meat", "label": "Go'sht", "label_ru": "Мясо", "icon": "Beef"},
                    ],
                },
            },
            {
                "title": "Sher",
                "title_ru": "Лев",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sherga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно льву.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🦁", "label": "Sher", "label_ru": "Лев"},
                    "correct_items": [
                        {"id": "meat", "label": "Go'sht", "label_ru": "Мясо", "icon": "Beef"},
                        {"id": "crown", "label": "Toj", "label_ru": "Корона", "icon": "Crown"},
                        {"id": "grass", "label": "Savana o'ti", "label_ru": "Трава саванны", "icon": "Sprout"},
                        {"id": "paw", "label": "Panja izi", "label_ru": "След лапы", "icon": "PawPrint"},
                        {"id": "sun", "label": "Quyosh", "label_ru": "Солнце", "icon": "Sun"},
                        {"id": "hole", "label": "Uyasi", "label_ru": "Логово", "icon": "CircleDashed"},
                    ],
                    "distractor_items": [
                        {"id": "milk", "label": "Sut", "label_ru": "Молоко", "icon": "Milk"},
                        {"id": "carrot", "label": "Sabzi", "label_ru": "Морковь", "icon": "Carrot"},
                        {"id": "peanut", "label": "Yeryong'oq", "label_ru": "Арахис", "icon": "Nut"},
                        {"id": "yarn", "label": "Yigiruv ipi", "label_ru": "Клубок ниток", "icon": "Yarn"},
                    ],
                },
            },
            {
                "title": "Fil",
                "title_ru": "Слон",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Filga kerakli narsalarni top.",
                "instruction_text_ru": "Найди то, что нужно слону.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🐘", "label": "Fil", "label_ru": "Слон"},
                    "correct_items": [
                        {"id": "peanut", "label": "Yeryong'oq", "label_ru": "Арахис", "icon": "Nut"},
                        {"id": "banana", "label": "Banan", "label_ru": "Банан", "icon": "Banana"},
                        {"id": "droplets", "label": "Suv", "label_ru": "Вода", "icon": "Droplets"},
                        {"id": "tree", "label": "Daraxt", "label_ru": "Дерево", "icon": "Trees"},
                        {"id": "grass", "label": "O't", "label_ru": "Трава", "icon": "Sprout"},
                        {"id": "green_leaf", "label": "Barg", "label_ru": "Лист", "icon": "Leaf"},
                    ],
                    "distractor_items": [
                        {"id": "bone", "label": "Suyak", "label_ru": "Кость", "icon": "Bone"},
                        {"id": "cheese", "label": "Pishloq", "label_ru": "Сыр", "icon": "Sandwich"},
                        {"id": "crown", "label": "Toj", "label_ru": "Корона", "icon": "Crown"},
                        {"id": "dandelion", "label": "Qoqio't", "label_ru": "Одуванчик", "icon": "Flower2"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Transport olami",
        "title_ru": "Мир транспорта",
        "description": "Transport turini tanla va unga mos vositalarni top.",
        "description_ru": "Выбери вид транспорта и найди то, что ему подходит.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🚦",
        "color_accent": "#4DA6FF",
        "display_order": 8,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Yer transporti",
                "title_ru": "Наземный транспорт",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Yerda yuradigan transportlarni top.",
                "instruction_text_ru": "Найди транспорт, который ездит по земле.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🚗", "label": "Yer transporti", "label_ru": "Наземный транспорт"},
                    "correct_items": [
                        {"id": "sedan_car", "label": "Mashina", "label_ru": "Машина", "icon": "Car"},
                        {"id": "bus", "label": "Avtobus", "label_ru": "Автобус", "icon": "Bus"},
                        {"id": "bicycle", "label": "Velosiped", "label_ru": "Велосипед", "icon": "Bike"},
                        {"id": "train", "label": "Poyezd", "label_ru": "Поезд", "icon": "TrainFront"},
                        {"id": "motorcycle", "label": "Mototsikl", "label_ru": "Мотоцикл", "icon": "Bike"},
                        {"id": "truck", "label": "Yuk mashinasi", "label_ru": "Грузовик", "icon": "Truck"},
                    ],
                    "distractor_items": [
                        {"id": "sailboat", "label": "Yelkanli qayiq", "label_ru": "Парусная лодка", "icon": "Sailboat"},
                        {"id": "airplane", "label": "Samolyot", "label_ru": "Самолёт", "icon": "Plane"},
                        {"id": "cargo_ship", "label": "Kema", "label_ru": "Корабль", "icon": "Ship"},
                        {"id": "helicopter", "label": "Vertolyot", "label_ru": "Вертолёт", "icon": "Rotate3d"},
                    ],
                },
            },
            {
                "title": "Suv transporti",
                "title_ru": "Водный транспорт",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Suvda yuradigan transportlarni top.",
                "instruction_text_ru": "Найди транспорт, который плавает по воде.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "⛵", "label": "Suv transporti", "label_ru": "Водный транспорт"},
                    "correct_items": [
                        {"id": "sailboat", "label": "Yelkanli qayiq", "label_ru": "Парусная лодка", "icon": "Sailboat"},
                        {"id": "cargo_ship", "label": "Kema", "label_ru": "Корабль", "icon": "Ship"},
                        {"id": "speedboat", "label": "Tezyurar qayiq", "label_ru": "Быстроходный катер", "icon": "Sailboat"},
                        {"id": "canoe", "label": "Kanoe", "label_ru": "Каноэ", "icon": "Sailboat"},
                        {"id": "ferry", "label": "Parom", "label_ru": "Паром", "icon": "Ship"},
                        {"id": "anchor", "label": "Langar", "label_ru": "Якорь", "icon": "Anchor"},
                    ],
                    "distractor_items": [
                        {"id": "sedan_car", "label": "Mashina", "label_ru": "Машина", "icon": "Car"},
                        {"id": "airplane", "label": "Samolyot", "label_ru": "Самолёт", "icon": "Plane"},
                        {"id": "train", "label": "Poyezd", "label_ru": "Поезд", "icon": "TrainFront"},
                        {"id": "rocket", "label": "Raketa", "label_ru": "Ракета", "icon": "Rocket"},
                    ],
                },
            },
            {
                "title": "Havo transporti",
                "title_ru": "Воздушный транспорт",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Havoda uchadigan transportlarni top.",
                "instruction_text_ru": "Найди транспорт, который летает по воздуху.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "✈️", "label": "Havo transporti", "label_ru": "Воздушный транспорт"},
                    "correct_items": [
                        {"id": "airplane", "label": "Samolyot", "label_ru": "Самолёт", "icon": "Plane"},
                        {"id": "helicopter", "label": "Vertolyot", "label_ru": "Вертолёт", "icon": "Rotate3d"},
                        {"id": "rocket", "label": "Raketa", "label_ru": "Ракета", "icon": "Rocket"},
                        {"id": "small_plane", "label": "Kichik samolyot", "label_ru": "Маленький самолёт", "icon": "Plane"},
                        {"id": "parachute", "label": "Parashyut", "label_ru": "Парашют", "icon": "Wind"},
                        {"id": "ufo", "label": "NUO", "label_ru": "НЛО", "icon": "Sparkle"},
                    ],
                    "distractor_items": [
                        {"id": "bus", "label": "Avtobus", "label_ru": "Автобус", "icon": "Bus"},
                        {"id": "cargo_ship", "label": "Kema", "label_ru": "Корабль", "icon": "Ship"},
                        {"id": "bicycle", "label": "Velosiped", "label_ru": "Велосипед", "icon": "Bike"},
                        {"id": "canoe", "label": "Kanoe", "label_ru": "Каноэ", "icon": "Sailboat"},
                    ],
                },
            },
        ],
    },
    {
        "title": "Rang olami",
        "title_ru": "Мир красок",
        "description": "Rangni tanla va unga mos narsalarni top.",
        "description_ru": "Выбери цвет и найди подходящие предметы.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🎨",
        "color_accent": "#FF6FA8",
        "display_order": 9,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Qizil",
                "title_ru": "Красный",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Qizil rangdagi narsalarni top.",
                "instruction_text_ru": "Найди предметы красного цвета.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔴", "label": "Qizil", "label_ru": "Красный"},
                    "correct_items": [
                        {"id": "apple", "label": "Olma", "label_ru": "Яблоко", "icon": "Apple"},
                        {"id": "strawberry", "label": "Qulupnay", "label_ru": "Клубника", "icon": "Cherry"},
                        {"id": "cherry", "label": "Gilos", "label_ru": "Вишня", "icon": "Cherry"},
                        {"id": "heart", "label": "Yurak", "label_ru": "Сердце", "icon": "Heart"},
                        {"id": "fire_truck", "label": "O't o'chirish mashinasi", "label_ru": "Пожарная машина", "icon": "Truck"},
                        {"id": "rose", "label": "Atirgul", "label_ru": "Роза", "icon": "Flower"},
                    ],
                    "distractor_items": [
                        {"id": "banana", "label": "Banan", "label_ru": "Банан", "icon": "Banana"},
                        {"id": "broccoli", "label": "Brokkoli", "label_ru": "Брокколи", "icon": "Broccoli"},
                        {"id": "blueberries", "label": "Ko'kat rezavor", "label_ru": "Черника", "icon": "Grape"},
                        {"id": "grapes", "label": "Uzum", "label_ru": "Виноград", "icon": "Grape"},
                    ],
                },
            },
            {
                "title": "Sariq",
                "title_ru": "Жёлтый",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sariq rangdagi narsalarni top.",
                "instruction_text_ru": "Найди предметы жёлтого цвета.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🟡", "label": "Sariq", "label_ru": "Жёлтый"},
                    "correct_items": [
                        {"id": "banana", "label": "Banan", "label_ru": "Банан", "icon": "Banana"},
                        {"id": "lemon", "label": "Limon", "label_ru": "Лимон", "icon": "Citrus"},
                        {"id": "sun", "label": "Quyosh", "label_ru": "Солнце", "icon": "Sun"},
                        {"id": "corn", "label": "Makkajo'xori", "label_ru": "Кукуруза", "icon": "Wheat"},
                        {"id": "chick", "label": "Jo'ja", "label_ru": "Цыплёнок", "icon": "Bird"},
                        {"id": "star", "label": "Yulduz", "label_ru": "Звезда", "icon": "Star"},
                    ],
                    "distractor_items": [
                        {"id": "apple", "label": "Olma", "label_ru": "Яблоко", "icon": "Apple"},
                        {"id": "cucumber", "label": "Bodring", "label_ru": "Огурец", "icon": "Salad"},
                        {"id": "blueberries", "label": "Ko'kat rezavor", "label_ru": "Черника", "icon": "Grape"},
                        {"id": "cherry", "label": "Gilos", "label_ru": "Вишня", "icon": "Cherry"},
                    ],
                },
            },
            {
                "title": "Yashil",
                "title_ru": "Зелёный",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Yashil rangdagi narsalarni top.",
                "instruction_text_ru": "Найди предметы зелёного цвета.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🟢", "label": "Yashil", "label_ru": "Зелёный"},
                    "correct_items": [
                        {"id": "broccoli", "label": "Brokkoli", "label_ru": "Брокколи", "icon": "Broccoli"},
                        {"id": "green_leaf", "label": "Barg", "label_ru": "Лист", "icon": "Leaf"},
                        {"id": "tree", "label": "Daraxt", "label_ru": "Дерево", "icon": "Trees"},
                        {"id": "frog", "label": "Qurbaqa", "label_ru": "Лягушка", "icon": "Turtle"},
                        {"id": "cucumber", "label": "Bodring", "label_ru": "Огурец", "icon": "Salad"},
                        {"id": "cactus", "label": "Kaktus", "label_ru": "Кактус", "icon": "Flower"},
                    ],
                    "distractor_items": [
                        {"id": "strawberry", "label": "Qulupnay", "label_ru": "Клубника", "icon": "Cherry"},
                        {"id": "banana", "label": "Banan", "label_ru": "Банан", "icon": "Banana"},
                        {"id": "blueberries", "label": "Ko'kat rezavor", "label_ru": "Черника", "icon": "Grape"},
                        {"id": "fire_truck", "label": "O't o'chirish mashinasi", "label_ru": "Пожарная машина", "icon": "Truck"},
                    ],
                },
            },
            {
                "title": "Ko'k",
                "title_ru": "Синий",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Ko'k rangdagi narsalarni top.",
                "instruction_text_ru": "Найди предметы синего цвета.",
                "content": {
                    "mode": "select",
                    "character": {"emoji": "🔵", "label": "Ko'k", "label_ru": "Синий"},
                    "correct_items": [
                        {"id": "blueberries", "label": "Ko'kat rezavor", "label_ru": "Черника", "icon": "Grape"},
                        {"id": "wave", "label": "To'lqin", "label_ru": "Волна", "icon": "Waves"},
                        {"id": "whale", "label": "Kit", "label_ru": "Кит", "icon": "Fish"},
                        {"id": "droplets", "label": "Suv tomchisi", "label_ru": "Капля воды", "icon": "Droplets"},
                        {"id": "blue_bird", "label": "Qush", "label_ru": "Птица", "icon": "Bird"},
                        {"id": "gem", "label": "Qimmatbaho tosh", "label_ru": "Драгоценный камень", "icon": "Gem"},
                    ],
                    "distractor_items": [
                        {"id": "apple", "label": "Olma", "label_ru": "Яблоко", "icon": "Apple"},
                        {"id": "lemon", "label": "Limon", "label_ru": "Лимон", "icon": "Citrus"},
                        {"id": "cactus", "label": "Kaktus", "label_ru": "Кактус", "icon": "Flower"},
                        {"id": "strawberry", "label": "Qulupnay", "label_ru": "Клубника", "icon": "Cherry"},
                    ],
                },
            },
        ],
    },
    # ── "Yasash o'yinlari": drag-to-assemble, activity_type=match with a
    # third content["mode"]="build" shape (character + slots +
    # distractor_items — slots carry the same per-occurrence label/label_ru/
    # emoji convention as mode="select"'s items, plus an x/y/w/h drop-zone
    # rectangle in percent of the scene). Reuses activity_type=match rather
    # than a new EarlyActivityType value for the same reason the packs above
    # stay subject=logic — avoiding an ALTER TYPE against the
    # already-materialized Postgres enum; activity_type is never branched on
    # server-side (see early_learning.py's _activity_out), only content.mode
    # is. subject=creative here (assembling a picture is a constructive act,
    # distinct from the tap-to-categorize packs above).
    {
        "title": "Yasash o'yinlari",
        "title_ru": "Собери сам",
        "description": "Bo'laklarni surib, rasmni yasab chiq.",
        "description_ru": "Перетаскивай детали и собери картинку.",
        "subject": EarlySubject.creative,
        "icon_emoji": "🧩",
        "color_accent": "#4ECDC4",
        "display_order": 7,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Qorbobo yasaymiz",
                "title_ru": "Собираем снеговика",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Har bir bo'lakni o'z joyiga sur.",
                "instruction_text_ru": "Перетащи каждую деталь на своё место.",
                "content": {
                    "mode": "build",
                    "scene": "snowman",
                    "character": {"emoji": "⛄", "label": "Qorbobo yasaymiz", "label_ru": "Собираем снеговика"},
                    "slots": [
                        {"id": "hat", "label": "Shlyapa", "label_ru": "Шляпа", "emoji": "🎩", "x": 38, "y": 3, "w": 24, "h": 16},
                        {"id": "nose", "label": "Burun", "label_ru": "Нос", "emoji": "🥕", "x": 42, "y": 20, "w": 16, "h": 12},
                        {"id": "scarf", "label": "Sharf", "label_ru": "Шарф", "emoji": "🧣", "x": 30, "y": 34, "w": 40, "h": 12},
                        # The 3 buttons are visually and semantically
                        # interchangeable (unlike hat/nose/scarf/arms, which
                        # are each unique) — matchGroup lets any of the 3
                        # button pieces fill any of the 3 button slots,
                        # rather than requiring the exact button1↔button1
                        # pairing a kid has no way to tell apart. See
                        # BuildActivity.js's resolveDrop.
                        {"id": "button1", "label": "Tugma", "label_ru": "Пуговица", "emoji": "⚫", "x": 46, "y": 50, "w": 8, "h": 8, "matchGroup": "button"},
                        {"id": "button2", "label": "Tugma", "label_ru": "Пуговица", "emoji": "⚫", "x": 46, "y": 60, "w": 8, "h": 8, "matchGroup": "button"},
                        {"id": "button3", "label": "Tugma", "label_ru": "Пуговица", "emoji": "⚫", "x": 46, "y": 70, "w": 8, "h": 8, "matchGroup": "button"},
                        {"id": "arm_l", "label": "Qo'l", "label_ru": "Рука", "emoji": "🌿", "x": 12, "y": 46, "w": 20, "h": 10},
                        {"id": "arm_r", "label": "Qo'l", "label_ru": "Рука", "emoji": "🌿", "x": 68, "y": 46, "w": 20, "h": 10},
                    ],
                    "distractor_items": [
                        {"id": "sunglasses", "label": "Ko'zoynak", "label_ru": "Очки", "emoji": "🕶️"},
                        {"id": "flipflops", "label": "Shippak", "label_ru": "Шлёпанцы", "emoji": "🩴"},
                        {"id": "sunhat", "label": "Salqin shlyapa", "label_ru": "Летняя шляпа", "emoji": "👒"},
                    ],
                },
            },
        ],
    },
    # ── "Chizib o'rganamiz": trace-the-outline, activity_type=trace (unlike
    # the "select"/"build" content above, `trace` was already a member of
    # EarlyActivityType from day one — SQLAlchemy registers every enum
    # member into the Postgres native type at DDL time, not just the ones
    # with data yet — so no ALTER TYPE workaround needed here). subject=motor
    # is its first real use: the enum's own comment names tracing as the
    # paradigm case ("tracing, cutting-practice style taps"). New dedicated
    # module rather than resurrecting the draft "Ijodkorlik burchagi"'s own
    # trace stub, same reasoning as "Yasash o'yinlari" above — that module
    # also holds an unbuilt "Erkin bo'yash" (coloring) draft, and
    # _upsert_activity has no per-activity publish override, so publishing
    # the module would publish that broken stub too.
    {
        "title": "Chizib o'rganamiz",
        "title_ru": "Учимся, рисуя",
        "description": "Barmog'ing bilan shakllarni chiz.",
        "description_ru": "Обводи фигуры пальцем.",
        "subject": EarlySubject.motor,
        "icon_emoji": "✏️",
        "color_accent": "#38BDF8",
        "display_order": 8,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Shakllarni chizamiz",
                "title_ru": "Рисуем фигуры",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Barmog'ing bilan shaklni chiz.",
                "instruction_text_ru": "Обведи фигуру пальцем.",
                "content": {
                    "mode": "trace",
                    "character": {"emoji": "✏️", "label": "Shakllarni chizamiz", "label_ru": "Рисуем фигуры"},
                    # `shape` is a closed set (circle/square/triangle) the
                    # frontend maps to a guide-drawing + checkpoint-geometry
                    # function — no hand-authored path data needed per shape.
                    "targets": [
                        {"id": "circle", "shape": "circle", "label": "Aylana", "label_ru": "Круг"},
                        {"id": "square", "shape": "square", "label": "Kvadrat", "label_ru": "Квадрат"},
                        {"id": "triangle", "shape": "triangle", "label": "Uchburchak", "label_ru": "Треугольник"},
                    ],
                },
            },
        ],
    },
    # ── "Yo'lni topamiz": arrow pathfinding, activity_type=maze — like
    # `trace`, `maze` was already a member of EarlyActivityType from day
    # one (no ALTER TYPE concern). subject=logic is EarlySubject's own
    # named case ("sequencing, patterns, mazes"). New dedicated module
    # rather than resurrecting the draft "Fikrlash o'yinlari"'s own maze
    # stub (grid_size/walls: [] — a trivial non-puzzle), which also holds
    # two other unbuilt drafts ("Kunlik tartib"/sequence, "Naqshni davom
    # ettir"/pattern) with no per-activity publish override.
    {
        "title": "Yo'lni topamiz",
        "title_ru": "Найдём путь",
        "description": "O'qlar yordamida qahramonni bayroqqa olib bor.",
        "description_ru": "Веди героя стрелками до флажка.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🧭",
        "color_accent": "#FFD166",
        "display_order": 9,
        "age_min": 5,
        "age_max": 8,
        "is_published": True,
        "activities": [
            {
                "title": "Yo'lni top",
                "title_ru": "Найди путь",
                "activity_type": EarlyActivityType.maze,
                "instruction_text": "O'qlar yordamida boshidan oxirigacha yo'l top.",
                "instruction_text_ru": "С помощью стрелок найди путь от начала до конца.",
                "content": {
                    "mode": "maze",
                    "character": {"emoji": "🦸", "label": "Yo'lni top", "label_ru": "Найди путь"},
                    # [row, col] throughout. Hand-verified solvable path:
                    # (0,0)->(1,0)->(2,0)->(3,0)->(3,1)->(3,2)->(4,2)->(4,3)->(4,4),
                    # 8 moves, none of them walls.
                    "grid": {"rows": 5, "cols": 5},
                    "start": [0, 0],
                    "end": [4, 4],
                    "walls": [[0, 2], [1, 1], [1, 3], [2, 1], [2, 3], [3, 3]],
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
    existing.description_ru = data.get("description_ru")
    existing.subject = data["subject"]
    existing.icon_emoji = data["icon_emoji"]
    existing.color_accent = data["color_accent"]
    existing.display_order = data["display_order"]
    existing.title = data["title"]
    existing.title_ru = data.get("title_ru")
    # Draft modules (literacy/math/logic/creative above) intentionally stay
    # is_published=False pending real media. The matching-game packs below
    # are icon-based (no missing assets) and ship complete, so they opt in
    # via this flag instead.
    existing.is_published = data.get("is_published", False)
    # Falls back to the model default (4-6, the drafts' original target)
    # for any module that doesn't specify its own — only the matching-game
    # packs below set 5-8 explicitly. Now actually enforced (see
    # early_learning.py's _is_age_eligible), not just advisory metadata.
    existing.age_min = data.get("age_min", 4)
    existing.age_max = data.get("age_max", 6)
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
    existing.title_ru = data.get("title_ru")
    existing.order = order
    existing.activity_type = data["activity_type"]
    existing.instruction_text = data["instruction_text"]
    existing.instruction_text_ru = data.get("instruction_text_ru")
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
