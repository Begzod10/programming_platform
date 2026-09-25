"""Question generators for the 1-vs-1 duel ("Poyga").

Every generator returns {"kind", "text", "options", "answer"} and takes a
difficulty `level` ("easy" | "medium" | "hard"). The server doesn't know a
player's language, so language-dependent content is shipped as
{"uz": ..., "ru": ...} and the client picks one:

  * `text` is a plain string (numbers/emoji) or a {"uz","ru"} dict;
  * an option is a plain string or {"v", "uz", "ru"} — the client shows the
    label but always sends `v`, and `answer` is compared against `v`.

Emoji/numbers are used wherever possible so most kinds need no translation.
"""
import random
from typing import Dict, List, Optional

LEVELS = ("easy", "medium", "hard")


def _pick(level: str, easy, medium, hard):
    return {"easy": easy, "medium": medium}.get(level, hard)


def _near_numbers(answer: int, extra: List[int], lo: int = 0, hi: int = 30, spread: int = 3) -> List[str]:
    """3 distinct wrong numbers close to `answer`, plus the answer, shuffled."""
    wrongs: List[int] = []
    cands = extra + [answer + d for d in (-1, 1, -2, 2, 3, -3, 4, -4, 5, -5, 10, -10)
                     if abs(d) <= max(spread, 3) + 2]
    for c in cands:
        if lo <= c <= hi and c != answer and c not in wrongs:
            wrongs.append(c)
    random.shuffle(wrongs)
    picked = wrongs[:3]
    n = lo
    while len(picked) < 3:
        if n != answer and n not in picked:
            picked.append(n)
        n += 1
    options = [str(answer)] + [str(w) for w in picked]
    random.shuffle(options)
    return options


def _loc(uz: str, ru: str) -> Dict[str, str]:
    return {"uz": uz, "ru": ru}


# ── math ────────────────────────────────────────────────────────────────────

def q_arith(level: str) -> dict:
    hi = _pick(level, 9, 30, 99)
    a, b = random.randint(0, hi), random.randint(0, hi)
    if random.random() < 0.5:
        text, answer = f"{a} + {b}", a + b
    else:
        if a < b:
            a, b = b, a
        text, answer = f"{a} − {b}", a - b
    return {"kind": "arith", "text": text, "answer": str(answer),
            "options": _near_numbers(answer, [], hi=hi * 2, spread=_pick(level, 3, 5, 10))}


def q_compare(level: str) -> dict:
    hi = _pick(level, 20, 99, 999)
    a = random.randint(0, hi)
    b = a if random.random() < 0.17 else random.randint(0, hi)
    if level == "hard" and random.random() < 0.5:  # near-misses, e.g. 407 ? 470
        b = a + random.choice([-10, -1, 1, 10]) if a > 10 else b
    sign = "<" if a < b else ">" if a > b else "="
    return {"kind": "compare", "text": f"{a} ? {b}", "options": ["<", "=", ">"], "answer": sign}


def q_mult(level: str) -> dict:
    lo, hi = _pick(level, (2, 5), (2, 9), (6, 12))
    a, b = random.randint(lo, hi), random.randint(2, hi if level != "easy" else 9)
    ans = a * b
    return {"kind": "mult", "text": f"{a} × {b}", "answer": str(ans),
            "options": _near_numbers(ans, [ans + a, ans - a, ans + b, ans - b], hi=200, spread=6)}


# ── visual / logic ──────────────────────────────────────────────────────────

_COUNT_EMOJI = ["🍎", "⭐", "🐟", "🎈", "🍪", "🐥", "🌸", "⚽"]


def q_count(level: str) -> dict:
    n = random.randint(*_pick(level, (1, 6), (1, 9), (6, 14)))
    emoji = random.choice(_COUNT_EMOJI)
    return {"kind": "count", "text": f"{emoji * n} ?", "answer": str(n),
            "options": _near_numbers(n, [], lo=1, hi=16)}


_PATTERN_COLORS = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟠"]


def q_pattern(level: str) -> dict:
    shapes = _pick(level, ["AB"], ["AAB", "ABC", "AB"], ["ABC", "AABB", "ABCD", "ABB"])
    shape = random.choice(shapes)
    colors = random.sample(_PATTERN_COLORS, 4)
    unit = ["ABCD".index(ch) for ch in shape]
    shown_len = len(unit) * 2 + random.randint(1, len(unit) - 1)
    shown = [colors[unit[i % len(unit)]] for i in range(shown_len)]
    answer = colors[unit[shown_len % len(unit)]]
    others = [c for c in _PATTERN_COLORS if c != answer]
    options = [answer] + random.sample(others, 3)
    random.shuffle(options)
    return {"kind": "pattern", "text": " ".join(shown) + " ?", "options": options, "answer": answer}


def q_sequence(level: str) -> dict:
    if level == "hard" and random.random() < 0.4:  # doubling / tripling
        start, mult = random.randint(1, 4), random.choice([2, 3])
        nums = [start * mult ** i for i in range(4)]
        answer = start * mult ** 4
        return {"kind": "sequence", "text": ", ".join(map(str, nums)) + ", ?", "answer": str(answer),
                "options": _near_numbers(answer, [answer + start, answer - start], hi=600, spread=8)}
    step = random.randint(*_pick(level, (1, 3), (2, 6), (3, 12)))
    start = random.randint(0, 10) + (step * 4 if level == "hard" and random.random() < 0.5 else 0)
    if level == "hard" and start >= step * 5 and random.random() < 0.5:
        step = -step  # counting down
    count = 3 if level != "hard" else 4
    nums = [start + step * i for i in range(count)]
    answer = start + step * count
    return {"kind": "sequence", "text": ", ".join(map(str, nums)) + ", ?", "answer": str(answer),
            "options": _near_numbers(answer, [answer - abs(step), answer + abs(step)], hi=200, spread=abs(step))}


_ODD_CATEGORIES = {
    "fruit": ["🍎", "🍌", "🍇", "🍓", "🍒", "🍊"],
    "animal": ["🐶", "🐱", "🐰", "🐻", "🐼", "🦊"],
    "vehicle": ["🚗", "🚌", "🚕", "🚓", "🚑", "🚒"],
    "sea": ["🐟", "🐙", "🦀", "🐬", "🐳", "🦈"],
    "bird": ["🐥", "🦆", "🦉", "🦅", "🐧", "🦜"],
    "sport": ["⚽", "🏀", "🎾", "🏐", "🏈", "🎱"],
}
# "hard": categories that are easy to mix up (all animals, one is a bird etc.).
_ODD_HARD_PAIRS = [("animal", "bird"), ("animal", "sea"), ("bird", "sea"), ("fruit", "sport")]


def q_odd(level: str) -> dict:
    if level == "hard":
        main, other = random.choice(_ODD_HARD_PAIRS)
        if random.random() < 0.5:
            main, other = other, main
    else:
        main, other = random.sample(list(_ODD_CATEGORIES), 2)
    three = random.sample(_ODD_CATEGORIES[main], 3)
    odd = random.choice(_ODD_CATEGORIES[other])
    options = three + [odd]
    random.shuffle(options)
    return {"kind": "odd", "text": "❓", "options": options, "answer": odd}


# ── clock ───────────────────────────────────────────────────────────────────
_CLOCK_HOUR = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚"
_CLOCK_HALF = "🕧🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦"  # 12:30, 1:30, ... 11:30


def q_clock(level: str) -> dict:
    h = random.randint(1, 12)
    if level == "easy" or random.random() < 0.4:
        face, answer = _CLOCK_HOUR[h % 12], f"{h}:00"
        pool = [f"{x}:00" for x in range(1, 13)]
    else:
        face, answer = _CLOCK_HALF[h % 12], f"{h}:30"
        pool = [f"{x}:30" for x in range(1, 13)] + ([f"{h}:00", f"{h % 12 + 1}:30"] if level == "hard" else [])
    wrongs = random.sample([p for p in dict.fromkeys(pool) if p != answer], 3)
    options = [answer] + wrongs
    random.shuffle(options)
    return {"kind": "clock", "text": face, "options": options, "answer": answer}


# ── colour (Stroop): what colour is the INK, not the word? ──────────────────
_COLORS = [
    ("🔴", "#e53935", _loc("QIZIL", "КРАСНЫЙ")),
    ("🔵", "#1e88e5", _loc("KO'K", "СИНИЙ")),
    ("🟢", "#43a047", _loc("YASHIL", "ЗЕЛЁНЫЙ")),
    ("🟡", "#f9a825", _loc("SARIQ", "ЖЁЛТЫЙ")),
    ("🟣", "#8e24aa", _loc("BINAFSHA", "ФИОЛЕТОВЫЙ")),
]


def q_color(level: str) -> dict:
    word_c, ink_c = random.sample(_COLORS, 2)
    others = [c[0] for c in _COLORS if c[0] != ink_c[0]]
    options = [ink_c[0]] + random.sample(others, 3)
    random.shuffle(options)
    return {"kind": "color", "text": word_c[2], "ink": ink_c[1], "options": options, "answer": ink_c[0]}


# ── words (Uzbek, with a picture) ───────────────────────────────────────────
_WORDS = {
    "easy": [("🐱", "MUSHUK"), ("🐶", "IT"), ("🐄", "SIGIR"), ("🍎", "OLMA"), ("🍞", "NON"), ("☀️", "QUYOSH"),
             ("🌸", "GUL"), ("📖", "KITOB"), ("🐟", "BALIQ"), ("🏠", "UY"), ("🌙", "OY"), ("🚗", "MASHINA")],
    "medium": [("🌳", "DARAXT"), ("🐘", "FIL"), ("🍇", "UZUM"), ("🍉", "QOVUN"), ("✈️", "SAMOLYOT"),
               ("🚌", "AVTOBUS"), ("🐴", "OT"), ("🦁", "SHER"), ("🍌", "BANAN"), ("⚽", "TO'P"),
               ("🎒", "SUMKA"), ("⭐", "YULDUZ")],
    "hard": [("🚀", "RAKETA"), ("🐢", "TOSHBAQA"), ("🌈", "OMONKAMON"), ("🐦", "QUSH"), ("🍓", "QULUPNAY"),
             ("🚲", "VELOSIPED"), ("🎹", "PIANINO"), ("🦋", "KAPALAK"), ("🐝", "ARI"), ("🏫", "MAKTAB")],
}
_LETTERS = "ABDEFGHIJKLMNOPQRSTUVXYZ"


def q_word(level: str) -> dict:
    emoji, word = random.choice(_WORDS[level if level in _WORDS else "medium"])
    idxs = [i for i, ch in enumerate(word) if ch.isalpha()]
    i = random.choice(idxs)
    answer = word[i]
    shown = word[:i] + "_" + word[i + 1:]
    wrongs = random.sample([c for c in _LETTERS if c != answer], 3)
    options = [answer] + wrongs
    random.shuffle(options)
    return {"kind": "word", "text": f"{emoji}  {shown}", "options": options, "answer": answer}


# ── general knowledge (uz/ru) ───────────────────────────────────────────────
# (level, question uz, question ru, correct (uz, ru), [wrong (uz, ru)...])
_QUIZ = [
    ("easy", "Qaysi hayvon uchadi?", "Какое животное летает?", ("Qush", "Птица"), [("Baliq", "Рыба"), ("Sigir", "Корова"), ("Ot", "Лошадь")]),
    ("easy", "Suvda qaysi hayvon yashaydi?", "Кто живёт в воде?", ("Baliq", "Рыба"), [("Ot", "Лошадь"), ("Mushuk", "Кошка"), ("Qo'y", "Овца")]),
    ("easy", "Osmonda nima porlaydi?", "Что светит на небе?", ("Quyosh", "Солнце"), [("Tosh", "Камень"), ("Daraxt", "Дерево"), ("Non", "Хлеб")]),
    ("easy", "Sut kimdan olinadi?", "Кто даёт молоко?", ("Sigir", "Корова"), [("Tovuq", "Курица"), ("Baliq", "Рыба"), ("It", "Собака")]),
    ("easy", "Qor qanday rangda?", "Какого цвета снег?", ("Oq", "Белый"), [("Qora", "Чёрный"), ("Qizil", "Красный"), ("Yashil", "Зелёный")]),
    ("easy", "Bir haftada necha kun bor?", "Сколько дней в неделе?", ("7", "7"), [("5", "5"), ("6", "6"), ("10", "10")]),
    ("easy", "Odamning nechta ko'zi bor?", "Сколько глаз у человека?", ("2", "2"), [("1", "1"), ("3", "3"), ("4", "4")]),
    ("easy", "Tuxumni kim qo'yadi?", "Кто несёт яйца?", ("Tovuq", "Курица"), [("Mushuk", "Кошка"), ("Ot", "Лошадь"), ("Echki", "Коза")]),
    ("medium", "O'zbekiston poytaxti qaysi?", "Столица Узбекистана?", ("Toshkent", "Ташкент"), [("Samarqand", "Самарканд"), ("Buxoro", "Бухара"), ("Xiva", "Хива")]),
    ("medium", "Yilda nechta fasl bor?", "Сколько времён года?", ("4", "4"), [("3", "3"), ("5", "5"), ("6", "6")]),
    ("medium", "Yilda nechta oy bor?", "Сколько месяцев в году?", ("12", "12"), [("10", "10"), ("11", "11"), ("13", "13")]),
    ("medium", "Qaysi sayyora Quyoshga eng yaqin?", "Какая планета ближе всех к Солнцу?", ("Merkuriy", "Меркурий"), [("Yer", "Земля"), ("Mars", "Марс"), ("Venera", "Венера")]),
    ("medium", "Eng katta hayvon qaysi?", "Самое большое животное?", ("Kit", "Кит"), [("Fil", "Слон"), ("Jirafa", "Жираф"), ("Ayiq", "Медведь")]),
    ("medium", "Suv necha darajada muzlaydi?", "При скольких градусах замерзает вода?", ("0", "0"), [("10", "10"), ("50", "50"), ("100", "100")]),
    ("medium", "Qaysi fasl eng sovuq?", "Какое время года самое холодное?", ("Qish", "Зима"), [("Yoz", "Лето"), ("Bahor", "Весна"), ("Kuz", "Осень")]),
    ("medium", "Ari bizga nima beradi?", "Что нам дают пчёлы?", ("Asal", "Мёд"), [("Sut", "Молоко"), ("Non", "Хлеб"), ("Yog'", "Масло")]),
    ("hard", "Yer nechanchi sayyora (Quyoshdan)?", "Какая по счёту от Солнца планета Земля?", ("3", "3"), [("2", "2"), ("4", "4"), ("5", "5")]),
    ("hard", "Amir Temur qaysi shaharda dafn etilgan?", "В каком городе похоронен Амир Темур?", ("Samarqand", "Самарканд"), [("Toshkent", "Ташкент"), ("Buxoro", "Бухара"), ("Shahrisabz", "Шахрисабз")]),
    ("hard", "Eng uzun daryo qaysi (O'rta Osiyoda)?", "Самая длинная река Средней Азии?", ("Amudaryo", "Амударья"), [("Sirdaryo", "Сырдарья"), ("Zarafshon", "Зарафшан"), ("Chirchiq", "Чирчик")]),
    ("hard", "Suvning kimyoviy formulasi?", "Химическая формула воды?", ("H₂O", "H₂O"), [("CO₂", "CO₂"), ("O₂", "O₂"), ("NaCl", "NaCl")]),
    ("hard", "Uchburchakning nechta tomoni bor?", "Сколько сторон у треугольника?", ("3", "3"), [("4", "4"), ("5", "5"), ("6", "6")]),
    ("hard", "Qaysi qit'a eng katta?", "Какой материк самый большой?", ("Osiyo", "Азия"), [("Afrika", "Африка"), ("Yevropa", "Европа"), ("Avstraliya", "Австралия")]),
    ("hard", "Bir soatda necha daqiqa bor?", "Сколько минут в часе?", ("60", "60"), [("30", "30"), ("100", "100"), ("24", "24")]),
    ("hard", "O'simliklar yorug'likda nimani chiqaradi?", "Что выделяют растения на свету?", ("Kislorod", "Кислород"), [("Azot", "Азот"), ("Vodorod", "Водород"), ("Tuz", "Соль")]),
]


def q_quiz(level: str) -> dict:
    pool = [x for x in _QUIZ if x[0] == level] or _QUIZ
    _, q_uz, q_ru, correct, wrongs = random.choice(pool)
    options = [{"v": correct[0], "uz": correct[0], "ru": correct[1]}] + [
        {"v": w[0], "uz": w[0], "ru": w[1]} for w in wrongs
    ]
    random.shuffle(options)
    return {"kind": "quiz", "text": _loc(q_uz, q_ru), "options": options, "answer": correct[0]}


# ── registry ────────────────────────────────────────────────────────────────
GENERATORS = {
    "arith": (q_arith, 20),
    "compare": (q_compare, 10),
    "mult": (q_mult, 10),
    "count": (q_count, 10),
    "pattern": (q_pattern, 10),
    "sequence": (q_sequence, 10),
    "odd": (q_odd, 10),
    "clock": (q_clock, 8),
    "color": (q_color, 8),
    "word": (q_word, 10),
    "quiz": (q_quiz, 10),
}
ALL_KINDS = list(GENERATORS)
DEFAULT_KINDS = [k for k in ALL_KINDS if k != "mult"]  # ×-table is a big-kids game: opt in


def make_question(kinds: Optional[List[str]] = None, level: str = "medium") -> dict:
    kinds = [k for k in (kinds or DEFAULT_KINDS) if k in GENERATORS] or DEFAULT_KINDS
    level = level if level in LEVELS else "medium"
    gen = random.choices([GENERATORS[k][0] for k in kinds], weights=[GENERATORS[k][1] for k in kinds])[0]
    return gen(level)


def option_value(opt) -> str:
    return opt["v"] if isinstance(opt, dict) else opt
