"""Hand-authored content for the two modes I'm generating myself (not via
agent) because they need exact reuse of frontend-tuned geometry:

- trace (module 11): only 5 shapes existed (circle/square/triangle/star/
  rectangle), and the module's single existing activity already used all 5
  in one go. Added 2 new shapes (diamond, pentagon) to TraceActivity.js's
  SHAPES registry — reusing the existing generic pointsOnPolygon() helper,
  same pattern as square/triangle/star — giving a pool of 7 to draw fresh
  subsets from across 9 new activities.
- build (module 10): BuildActivity.js only has two scene backgrounds
  (snowman, house) baked in as hand-tuned CSS silhouettes with slots
  positioned by percentage coordinates tied to that exact geometry.
  Inventing a third scene blind (no visual pipeline to check alignment)
  risks shipping a misaligned drag target. Instead: 8 new activities reuse
  the EXACT existing slot x/y/w/h for each scene (proven correct — already
  shipped and verified) with a new dress-up theme (different hat/buttons
  for snowman, different flower/doormat for house) — safe, and still 8
  genuinely new mini-games, not literal duplicates.
"""

TRACE_ACTIVITIES = [
    dict(
        title="Aylana va kvadrat",
        title_ru="Круг и квадрат",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "⭕", "label": "Aylana va kvadrat", "label_ru": "Круг и квадрат"},
            targets=[
                {"id": "circle", "shape": "circle", "label": "Aylana", "label_ru": "Круг"},
                {"id": "square", "shape": "square", "label": "Kvadrat", "label_ru": "Квадрат"},
            ],
        ),
    ),
    dict(
        title="Uchburchak va to'rtburchak",
        title_ru="Треугольник и прямоугольник",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "🔺", "label": "Uchburchak va to'rtburchak", "label_ru": "Треугольник и прямоугольник"},
            targets=[
                {"id": "triangle", "shape": "triangle", "label": "Uchburchak", "label_ru": "Треугольник"},
                {"id": "rectangle", "shape": "rectangle", "label": "To'rtburchak", "label_ru": "Прямоугольник"},
            ],
        ),
    ),
    dict(
        title="Romb va beshburchak",
        title_ru="Ромб и пятиугольник",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "🔷", "label": "Romb va beshburchak", "label_ru": "Ромб и пятиугольник"},
            targets=[
                {"id": "diamond", "shape": "diamond", "label": "Romb", "label_ru": "Ромб"},
                {"id": "pentagon", "shape": "pentagon", "label": "Beshburchak", "label_ru": "Пятиугольник"},
            ],
        ),
    ),
    dict(
        title="Aylana, romb va yulduz",
        title_ru="Круг, ромб и звезда",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "🌟", "label": "Aylana, romb va yulduz", "label_ru": "Круг, ромб и звезда"},
            targets=[
                {"id": "circle", "shape": "circle", "label": "Aylana", "label_ru": "Круг"},
                {"id": "diamond", "shape": "diamond", "label": "Romb", "label_ru": "Ромб"},
                {"id": "star", "shape": "star", "label": "Yulduz", "label_ru": "Звезда"},
            ],
        ),
    ),
    dict(
        title="Kvadrat, uchburchak va beshburchak",
        title_ru="Квадрат, треугольник и пятиугольник",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "🔻", "label": "Kvadrat, uchburchak va beshburchak", "label_ru": "Квадрат, треугольник и пятиугольник"},
            targets=[
                {"id": "square", "shape": "square", "label": "Kvadrat", "label_ru": "Квадрат"},
                {"id": "triangle", "shape": "triangle", "label": "Uchburchak", "label_ru": "Треугольник"},
                {"id": "pentagon", "shape": "pentagon", "label": "Beshburchak", "label_ru": "Пятиугольник"},
            ],
        ),
    ),
    dict(
        title="Barcha burchakli shakllar",
        title_ru="Все фигуры с углами",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "📐", "label": "Barcha burchakli shakllar", "label_ru": "Все фигуры с углами"},
            targets=[
                {"id": "square", "shape": "square", "label": "Kvadrat", "label_ru": "Квадрат"},
                {"id": "triangle", "shape": "triangle", "label": "Uchburchak", "label_ru": "Треугольник"},
                {"id": "rectangle", "shape": "rectangle", "label": "To'rtburchak", "label_ru": "Прямоугольник"},
                {"id": "diamond", "shape": "diamond", "label": "Romb", "label_ru": "Ромб"},
                {"id": "pentagon", "shape": "pentagon", "label": "Beshburchak", "label_ru": "Пятиугольник"},
            ],
        ),
    ),
    dict(
        title="Yumaloq va yulduzli shakllar",
        title_ru="Круглые и звёздчатые фигуры",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "✨", "label": "Yumaloq va yulduzli shakllar", "label_ru": "Круглые и звёздчатые фигуры"},
            targets=[
                {"id": "circle", "shape": "circle", "label": "Aylana", "label_ru": "Круг"},
                {"id": "star", "shape": "star", "label": "Yulduz", "label_ru": "Звезда"},
                {"id": "diamond", "shape": "diamond", "label": "Romb", "label_ru": "Ромб"},
            ],
        ),
    ),
    dict(
        title="Katta mashq: 6 shakl",
        title_ru="Большая тренировка: 6 фигур",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "🎯", "label": "Katta mashq: 6 shakl", "label_ru": "Большая тренировка: 6 фигур"},
            targets=[
                {"id": "circle", "shape": "circle", "label": "Aylana", "label_ru": "Круг"},
                {"id": "square", "shape": "square", "label": "Kvadrat", "label_ru": "Квадрат"},
                {"id": "triangle", "shape": "triangle", "label": "Uchburchak", "label_ru": "Треугольник"},
                {"id": "star", "shape": "star", "label": "Yulduz", "label_ru": "Звезда"},
                {"id": "diamond", "shape": "diamond", "label": "Romb", "label_ru": "Ромб"},
                {"id": "pentagon", "shape": "pentagon", "label": "Beshburchak", "label_ru": "Пятиугольник"},
            ],
        ),
    ),
    dict(
        title="Super mashq: barcha shakllar",
        title_ru="Супер-тренировка: все фигуры",
        instruction_text="Barmog'ing bilan shaklni chiz.",
        instruction_text_ru="Обведи фигуру пальцем.",
        content=dict(
            mode="trace",
            character={"emoji": "🏆", "label": "Super mashq: barcha shakllar", "label_ru": "Супер-тренировка: все фигуры"},
            targets=[
                {"id": "circle", "shape": "circle", "label": "Aylana", "label_ru": "Круг"},
                {"id": "square", "shape": "square", "label": "Kvadrat", "label_ru": "Квадрат"},
                {"id": "triangle", "shape": "triangle", "label": "Uchburchak", "label_ru": "Треугольник"},
                {"id": "rectangle", "shape": "rectangle", "label": "To'rtburchak", "label_ru": "Прямоугольник"},
                {"id": "star", "shape": "star", "label": "Yulduz", "label_ru": "Звезда"},
                {"id": "diamond", "shape": "diamond", "label": "Romb", "label_ru": "Ромб"},
                {"id": "pentagon", "shape": "pentagon", "label": "Beshburchak", "label_ru": "Пятиугольник"},
            ],
        ),
    ),
]

# Exact coordinates reused from the existing, already-shipped snowman/house
# activities (see EarlyActivityDailyStars-adjacent investigation this
# session — pulled straight from the live DB rows for activities 39 & 42).
_SNOWMAN_HAT = dict(x=38, y=3, w=24, h=16)
_SNOWMAN_NOSE = dict(x=42, y=20, w=16, h=12)
_SNOWMAN_SCARF = dict(x=30, y=34, w=40, h=12)
_SNOWMAN_BUTTON_POS = [dict(x=46, y=50, w=8, h=8), dict(x=46, y=60, w=8, h=8), dict(x=46, y=70, w=8, h=8)]
_SNOWMAN_ARM_L = dict(x=12, y=46, w=20, h=10)
_SNOWMAN_ARM_R = dict(x=68, y=46, w=20, h=10)
_SNOWMAN_DISTRACTORS = [
    {"id": "sunglasses", "label": "Ko'zoynak", "label_ru": "Очки", "emoji": "🕶️"},
    {"id": "flipflops", "label": "Shippak", "label_ru": "Шлёпанцы", "emoji": "🩴"},
    {"id": "sunhat", "label": "Salqin shlyapa", "label_ru": "Летняя шляпа", "emoji": "👒"},
]


def _snowman(title, title_ru, char_emoji, hat, buttons_emoji, buttons_label, buttons_label_ru):
    return dict(
        title=title, title_ru=title_ru,
        instruction_text="Har bir bo'lakni o'z joyiga sur.",
        instruction_text_ru="Перетащи каждую деталь на своё место.",
        content=dict(
            mode="build", scene="snowman",
            character={"emoji": char_emoji, "label": title, "label_ru": title_ru},
            slots=[
                {"id": "hat", "label": hat["label"], "label_ru": hat["label_ru"], "emoji": hat["emoji"], **_SNOWMAN_HAT},
                {"id": "nose", "label": "Burun", "label_ru": "Нос", "emoji": "🥕", **_SNOWMAN_NOSE},
                {"id": "scarf", "label": "Sharf", "label_ru": "Шарф", "emoji": "🧣", **_SNOWMAN_SCARF},
                {"id": "button1", "label": buttons_label, "label_ru": buttons_label_ru, "emoji": buttons_emoji, "matchGroup": "button", **_SNOWMAN_BUTTON_POS[0]},
                {"id": "button2", "label": buttons_label, "label_ru": buttons_label_ru, "emoji": buttons_emoji, "matchGroup": "button", **_SNOWMAN_BUTTON_POS[1]},
                {"id": "button3", "label": buttons_label, "label_ru": buttons_label_ru, "emoji": buttons_emoji, "matchGroup": "button", **_SNOWMAN_BUTTON_POS[2]},
                {"id": "arm_l", "label": "Qo'l", "label_ru": "Рука", "emoji": "🌿", **_SNOWMAN_ARM_L},
                {"id": "arm_r", "label": "Qo'l", "label_ru": "Рука", "emoji": "🌿", **_SNOWMAN_ARM_R},
            ],
            distractor_items=_SNOWMAN_DISTRACTORS,
        ),
    )


_HOUSE_DOOR = dict(x=41, y=58, w=18, h=20)
_HOUSE_WINDOW_L = dict(x=24, y=48, w=14, h=14)
_HOUSE_WINDOW_R = dict(x=62, y=48, w=14, h=14)
_HOUSE_CHIMNEY = dict(x=56, y=28, w=12, h=12)
_HOUSE_SMOKE = dict(x=55, y=8, w=14, h=14)
_HOUSE_DOORBELL = dict(x=61, y=64, w=8, h=8)
_HOUSE_FLOWER = dict(x=22, y=64, w=16, h=10)
_HOUSE_DOORMAT = dict(x=38, y=80, w=24, h=8)
_HOUSE_DISTRACTORS = [
    {"id": "car", "label": "Mashina", "label_ru": "Машина", "emoji": "🚗"},
    {"id": "bicycle", "label": "Velosiped", "label_ru": "Велосипед", "emoji": "🚲"},
    {"id": "traffic_light", "label": "Svetofor", "label_ru": "Светофор", "emoji": "🚦"},
]


def _house(title, title_ru, char_emoji, deco_label, deco_label_ru, deco_emoji, mat_label, mat_label_ru, mat_emoji):
    return dict(
        title=title, title_ru=title_ru,
        instruction_text="Har bir bo'lakni o'z joyiga sur.",
        instruction_text_ru="Перетащи каждую деталь на своё место.",
        content=dict(
            mode="build", scene="house",
            character={"emoji": char_emoji, "label": title, "label_ru": title_ru},
            slots=[
                {"id": "door", "label": "Eshik", "label_ru": "Дверь", "emoji": "🚪", **_HOUSE_DOOR},
                {"id": "window_l", "label": "Deraza", "label_ru": "Окно", "emoji": "🪟", "matchGroup": "window", **_HOUSE_WINDOW_L},
                {"id": "window_r", "label": "Deraza", "label_ru": "Окно", "emoji": "🪟", "matchGroup": "window", **_HOUSE_WINDOW_R},
                {"id": "chimney", "label": "Mo'ri", "label_ru": "Труба", "emoji": "🧱", **_HOUSE_CHIMNEY},
                {"id": "smoke", "label": "Tutun", "label_ru": "Дым", "emoji": "💨", **_HOUSE_SMOKE},
                {"id": "doorbell", "label": "Qo'ng'iroq", "label_ru": "Звонок", "emoji": "🔔", **_HOUSE_DOORBELL},
                {"id": "flower", "label": deco_label, "label_ru": deco_label_ru, "emoji": deco_emoji, **_HOUSE_FLOWER},
                {"id": "doormat", "label": mat_label, "label_ru": mat_label_ru, "emoji": mat_emoji, **_HOUSE_DOORMAT},
            ],
            distractor_items=_HOUSE_DISTRACTORS,
        ),
    )


BUILD_ACTIVITIES = [
    _snowman(
        "Sport qorbobo", "Спортивный снеговик", "⚽",
        hat={"label": "Sport qalpog'i", "label_ru": "Спортивная кепка", "emoji": "🧢"},
        buttons_emoji="⚽", buttons_label="To'p nishon", buttons_label_ru="Значок-мяч",
    ),
    _snowman(
        "Bayramona qorbobo", "Праздничный снеговик", "🎉",
        hat={"label": "Bayram qalpog'i", "label_ru": "Праздничный колпак", "emoji": "🥳"},
        buttons_emoji="🎊", buttons_label="Konfetti", buttons_label_ru="Конфетти",
    ),
    _snowman(
        "Qishloq qorbobo", "Снеговик-фермер", "🌾",
        hat={"label": "Fermer shlyapasi", "label_ru": "Шляпа фермера", "emoji": "🤠"},
        buttons_emoji="🌽", buttons_label="Makkajo'xori", buttons_label_ru="Кукуруза",
    ),
    _snowman(
        "Qirol qorbobo", "Снеговик-король", "👑",
        hat={"label": "Toj", "label_ru": "Корона", "emoji": "👑"},
        buttons_emoji="💎", buttons_label="Marvarid", buttons_label_ru="Драгоценность",
    ),
    _house(
        "Qishloq uyi", "Деревенский дом", "🌾", "G'alla boylami", "Сноп пшеницы", "🌾", "Somon gilamchasi", "Соломенный коврик", "🟫",
    ),
    _house(
        "Qishki uy", "Зимний домик", "❄️", "Archa", "Ёлочка", "🎄", "Muzlik gilamchasi", "Снежный коврик", "❄️",
    ),
    _house(
        "Bayram uyi", "Праздничный дом", "🎁", "Bantik", "Бант", "🎀", "Sovg'a", "Подарок", "🎁",
    ),
    _house(
        "Bog' uyi", "Дом с садом", "🌻", "Kungaboqar", "Подсолнух", "🌻", "Gulli tuvak", "Цветочный горшок", "🪴",
    ),
]
