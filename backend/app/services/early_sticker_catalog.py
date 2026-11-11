"""Static sticker catalog for the kids' games (early learning).

Three of the four sticker kinds live here; the fourth ("module" badges) is
derived from the EarlyModule rows themselves, so it is not listed.

  star    one per STAR_STEP total stars            star:10 … star:510
  daily   one per "play day" (DAILY_PLAYS_NEEDED)  daily:01 … daily:26
  streak  consecutive play days                    streak:3/7/14/30

Keys are permanent: an award row stores only the key, so never renumber or
reuse one — append instead.
"""
from dataclasses import dataclass

STAR_STEP = 10
DAILY_PLAYS_NEEDED = 3
STREAK_DAYS = (3, 7, 14, 30)


@dataclass(frozen=True)
class StickerDef:
    key: str
    emoji: str
    name: str
    name_ru: str
    kind: str
    rarity: str


_STAR = [
    ("🐱", "Mushuk", "Кошка"), ("🐶", "Kuchuk", "Собака"), ("🐰", "Quyon", "Заяц"),
    ("🦊", "Tulki", "Лиса"), ("🦁", "Sher", "Лев"), ("🐻", "Ayiq", "Медведь"),
    ("🐼", "Panda", "Панда"), ("🐨", "Koala", "Коала"), ("🐯", "Yo'lbars", "Тигр"),
    ("🦄", "Yakkashox", "Единорог"), ("🐮", "Sigir", "Корова"), ("🐷", "Cho'chqacha", "Поросёнок"),
    ("🐸", "Qurbaqa", "Лягушка"), ("🐵", "Maymun", "Обезьяна"), ("🐲", "Ajdar", "Дракон"),
    ("🐔", "Tovuq", "Курица"), ("🐧", "Pingvin", "Пингвин"), ("🐦", "Qushcha", "Птичка"),
    ("🐤", "Jo'ja", "Цыплёнок"), ("🦅", "Burgut", "Орёл"), ("🦆", "O'rdak", "Утка"),
    ("🦉", "Boyqush", "Сова"), ("🐺", "Bo'ri", "Волк"), ("🐴", "Ot", "Лошадь"),
    ("🦖", "Dinozavr", "Динозавр"), ("🐝", "Asalari", "Пчела"), ("🦋", "Kapalak", "Бабочка"),
    ("🐌", "Shilliqqurt", "Улитка"), ("🐞", "Xonqizi", "Божья коровка"), ("🐢", "Toshbaqa", "Черепаха"),
    ("🐍", "Ilon", "Змея"), ("🦎", "Kaltakesak", "Ящерица"), ("🐙", "Sakkizoyoq", "Осьминог"),
    ("🦀", "Qisqichbaqa", "Краб"), ("🦈", "Akula", "Акула"), ("🐬", "Delfin", "Дельфин"),
    ("🐳", "Kit", "Кит"), ("🐠", "Baliqcha", "Рыбка"), ("🐊", "Timsoh", "Крокодил"),
    ("🦓", "Zebra", "Зебра"), ("🦍", "Gorilla", "Горилла"), ("🐘", "Fil", "Слон"),
    ("🦛", "Begemot", "Бегемот"), ("🦏", "Karkidon", "Носорог"), ("🐪", "Tuya", "Верблюд"),
    ("🦒", "Jirafa", "Жираф"), ("🦘", "Kenguru", "Кенгуру"), ("🐿️", "Olmaxon", "Белка"),
    ("🦔", "Tipratikan", "Ёж"), ("🦚", "Tovus", "Павлин"), ("🦜", "To'tiqush", "Попугай"),
]

_DAILY = [
    ("🚗", "Mashina", "Машина"), ("🚌", "Avtobus", "Автобус"), ("🚒", "O't o'chirish mashinasi", "Пожарная машина"),
    ("🚑", "Tez yordam", "Скорая помощь"), ("🚜", "Traktor", "Трактор"), ("🚲", "Velosiped", "Велосипед"),
    ("🚂", "Poyezd", "Поезд"), ("✈️", "Samolyot", "Самолёт"), ("🚁", "Vertolyot", "Вертолёт"),
    ("🚀", "Raketa", "Ракета"), ("⛵", "Yelkanli qayiq", "Парусник"), ("🚢", "Kema", "Корабль"),
    ("🍎", "Olma", "Яблоко"), ("🍌", "Banan", "Банан"), ("🍉", "Tarvuz", "Арбуз"),
    ("🍓", "Qulupnay", "Клубника"), ("🍇", "Uzum", "Виноград"), ("🍒", "Gilos", "Вишня"),
    ("🍑", "Shaftoli", "Персик"), ("🥕", "Sabzi", "Морковь"), ("🌻", "Kungaboqar", "Подсолнух"),
    ("🌈", "Kamalak", "Радуга"), ("🌙", "Oy", "Луна"), ("⭐", "Yulduz", "Звезда"),
    ("🌵", "Kaktus", "Кактус"), ("🍄", "Qo'ziqorin", "Гриб"),
]

_STREAK = {
    3: ("🥉", "3 kun", "3 дня"),
    7: ("🥈", "7 kun", "7 дней"),
    14: ("🥇", "14 kun", "14 дней"),
    30: ("🏆", "30 kun", "30 дней"),
}

STAR_STICKERS = [
    StickerDef(
        key=f"star:{(i + 1) * STAR_STEP}", emoji=e, name=uz, name_ru=ru, kind="star",
        rarity="rare" if ((i + 1) * STAR_STEP) % 50 == 0 else "common",
    )
    for i, (e, uz, ru) in enumerate(_STAR)
]
DAILY_STICKERS = [
    StickerDef(key=f"daily:{i + 1:02d}", emoji=e, name=uz, name_ru=ru, kind="daily", rarity="common")
    for i, (e, uz, ru) in enumerate(_DAILY)
]
STREAK_STICKERS = [
    StickerDef(key=f"streak:{n}", emoji=_STREAK[n][0], name=_STREAK[n][1], name_ru=_STREAK[n][2],
               kind="streak", rarity="epic")
    for n in STREAK_DAYS
]
CATALOG = {s.key: s for s in STAR_STICKERS + DAILY_STICKERS + STREAK_STICKERS}
