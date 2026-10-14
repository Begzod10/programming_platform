"""Hand-written catalogue of the Telegram-bot team-project themes (design doc §3.6).

A web blueprint is a set of HTTP endpoints between a frontend and a backend. A bot has neither: the
contract between a team's pieces is the list of FLOWS the bot offers — commands, inline-button callbacks,
multi-step FSM forms and scheduled jobs — plus the tables behind them and the files that implement them.
Flows reuse the endpoint shape (`id`, `method`, `path`, `auth`, `request`, `response`) so the planner, its
validation and the stored contract work unchanged: `method` is the flow kind, `path` its trigger,
`auth` means "admin only" (the ids in ADMIN_IDS).

Naming: flow id `<area>.<action>`; trigger `/command`, `cb:<area>:<action>[:<id>]` (callback_data),
`fsm:<name>` (a form the bot walks the user through) or `job:<name>` (scheduled). Every theme has the three
COMMON flows plus 5-8 feature flows, and 5 handler files (`bot/handlers/<name>.py`).
"""

COMMAND, CALLBACK, FSM, JOB = "COMMAND", "CALLBACK", "FSM", "JOB"

SKELETON_FILES = ["README.md", ".env.example", "bot/requirements.txt", "bot/main.py", "bot/config.py"]
CORE_FILES = ["bot/core/db.py", "bot/core/models.py", "bot/keyboards.py", "bot/states.py"]
RUN = {"backend": "cp .env.example .env && pip install -r bot/requirements.txt && python -m bot.main", "frontend": ""}


def flow(id_: str, kind: str, trigger: str, request, response, *, admin: bool = False) -> dict:
    return {"id": id_, "method": kind, "path": trigger, "auth": admin, "request": request, "response": response}


COMMON_FLOWS = [
    flow("start.menu", COMMAND, "/start", "/start", "salom va asosiy menyu (reply keyboard)"),
    flow("help.show", COMMAND, "/help", "/help", "buyruqlar ro'yxati"),
    flow("admin.stats", COMMAND, "/stats", "/stats", "foydalanuvchilar va yozuvlar soni", admin=True),
]


def _handlers(*names: str) -> list:
    return [f"bot/handlers/{n}.py" for n in names]


BOT_THEME_DATA = {
    "delivery_bot": {
        "entities": {"product": {"id": "int", "name": "str", "price": "int (so'm)"},
                     "cart_item": {"user_id": "int", "product_id": "int", "quantity": "int"},
                     "order": {"id": "int", "user_id": "int", "address": "str", "phone": "str", "status": "str"}},
        "handlers": _handlers("start", "catalog", "cart", "order", "admin"),
        "flows": [
            flow("catalog.browse", CALLBACK, "cb:catalog:page:<n>", {"page": "int"}, "mahsulotlar ro'yxati (inline tugmalar)"),
            flow("catalog.item", CALLBACK, "cb:catalog:item:<id>", {"product_id": "int"}, "mahsulot kartochkasi + 'Savatga' tugmasi"),
            flow("cart.add", CALLBACK, "cb:cart:add:<id>", {"product_id": "int"}, "savat yangilanadi"),
            flow("cart.view", COMMAND, "/cart", "/cart", "savat tarkibi va jami summa"),
            flow("order.create", FSM, "fsm:order", {"address": "str", "phone": "str"}, "buyurtma yaratiladi, tasdiq xabari"),
            flow("order.status", COMMAND, "/orders", "/orders", "foydalanuvchining buyurtmalari va holati"),
            flow("admin.set_status", CALLBACK, "cb:admin:status:<order_id>:<status>", {"order_id": "int", "status": "str"},
                 "buyurtma holati o'zgaradi, mijozga xabar", admin=True),
        ],
        "needs": [],
    },
    "quiz_bot": {
        "entities": {"question": {"id": "int", "text": "str", "options": "list[str]", "correct": "int"},
                     "attempt": {"id": "int", "user_id": "int", "score": "int", "finished_at": "datetime"}},
        "handlers": _handlers("start", "quiz", "scores", "questions", "admin"),
        "flows": [
            flow("quiz.start", CALLBACK, "cb:quiz:topic:<id>", {"topic_id": "int"}, "birinchi savol (inline javoblar)"),
            flow("quiz.answer", CALLBACK, "cb:quiz:answer:<q>:<opt>", {"question_id": "int", "option": "int"}, "to'g'ri/noto'g'ri va keyingi savol"),
            flow("quiz.finish", COMMAND, "/finish", "/finish", "yakuniy ball"),
            flow("scores.mine", COMMAND, "/score", "/score", "foydalanuvchining natijalari"),
            flow("scores.top", COMMAND, "/top", "/top", "eng yaxshi 10 ta natija"),
            flow("admin.add_question", FSM, "fsm:add_question", {"text": "str", "options": "list[str]", "correct": "int"},
                 "savol saqlanadi", admin=True),
            flow("admin.delete_question", CALLBACK, "cb:admin:delq:<id>", {"question_id": "int"}, "savol o'chiriladi", admin=True),
        ],
        "needs": [],
    },
    "queue_bot": {
        "entities": {"service": {"id": "int", "name": "str"},
                     "ticket": {"id": "int", "user_id": "int", "service_id": "int", "number": "int", "status": "str"}},
        "handlers": _handlers("start", "services", "tickets", "notify", "admin"),
        "flows": [
            flow("services.list", COMMAND, "/services", "/services", "xizmatlar ro'yxati (inline tugmalar)"),
            flow("ticket.take", CALLBACK, "cb:ticket:take:<service>", {"service_id": "int"}, "navbat raqami va oldingilar soni"),
            flow("ticket.mine", COMMAND, "/myturn", "/myturn", "mening navbatim va holati"),
            flow("ticket.cancel", CALLBACK, "cb:ticket:cancel:<id>", {"ticket_id": "int"}, "navbat bekor qilinadi"),
            flow("admin.call_next", COMMAND, "/next", "/next", "keyingi navbat chaqiriladi", admin=True),
            flow("admin.queue", COMMAND, "/queue", "/queue", "joriy navbat ro'yxati", admin=True),
            flow("notify.turn", JOB, "job:notify_turn", None, "navbati yaqinlashganda xabar"),
        ],
        "needs": [],
    },
    "expense_bot": {
        "entities": {"category": {"id": "int", "name": "str"},
                     "expense": {"id": "int", "user_id": "int", "category_id": "int", "amount": "int", "note": "str", "date": "date"}},
        "handlers": _handlers("start", "expenses", "categories", "reports", "admin"),
        "flows": [
            flow("expense.add", FSM, "fsm:expense", {"amount": "int", "category_id": "int", "note": "str"}, "xarajat saqlanadi"),
            flow("expense.list", COMMAND, "/expenses", "/expenses", "oxirgi xarajatlar ro'yxati"),
            flow("expense.delete", CALLBACK, "cb:expense:del:<id>", {"expense_id": "int"}, "xarajat o'chiriladi"),
            flow("category.pick", CALLBACK, "cb:category:pick:<id>", {"category_id": "int"}, "kategoriya tanlanadi"),
            flow("report.month", COMMAND, "/report", "/report", "oylik hisobot: kategoriya bo'yicha summa"),
            flow("report.weekly", JOB, "job:weekly_report", None, "har hafta qisqa hisobot yuboriladi"),
        ],
        "needs": [],
    },
    "flashcards_bot": {
        "entities": {"card": {"id": "int", "user_id": "int", "word": "str", "translation": "str"},
                     "review": {"card_id": "int", "known": "bool", "at": "datetime"}},
        "handlers": _handlers("start", "cards", "practice", "stats", "admin"),
        "flows": [
            flow("card.add", FSM, "fsm:add_card", {"word": "str", "translation": "str"}, "kartochka saqlanadi"),
            flow("card.list", COMMAND, "/cards", "/cards", "kartochkalar ro'yxati"),
            flow("card.delete", CALLBACK, "cb:card:del:<id>", {"card_id": "int"}, "kartochka o'chiriladi"),
            flow("practice.next", CALLBACK, "cb:practice:next", None, "keyingi kartochka (so'z)"),
            flow("practice.flip", CALLBACK, "cb:practice:flip:<id>", {"card_id": "int"}, "tarjimasi ko'rsatiladi"),
            flow("practice.answer", CALLBACK, "cb:practice:known:<id>:<flag>", {"card_id": "int", "known": "bool"}, "natija yoziladi"),
            flow("stats.progress", COMMAND, "/progress", "/progress", "nechta so'z bilindi"),
        ],
        "needs": [],
    },
    "events_bot": {
        "entities": {"event": {"id": "int", "title": "str", "date": "datetime", "seats": "int"},
                     "registration": {"event_id": "int", "user_id": "int"}},
        "handlers": _handlers("start", "events", "registration", "reminders", "admin"),
        "flows": [
            flow("events.list", COMMAND, "/events", "/events", "kelgusi tadbirlar (inline tugmalar)"),
            flow("events.details", CALLBACK, "cb:event:show:<id>", {"event_id": "int"}, "tadbir tavsifi, joylar soni"),
            flow("registration.join", CALLBACK, "cb:event:join:<id>", {"event_id": "int"}, "ro'yxatdan o'tildi yoki joy yo'q"),
            flow("registration.cancel", CALLBACK, "cb:event:leave:<id>", {"event_id": "int"}, "ro'yxatdan chiqildi"),
            flow("registration.mine", COMMAND, "/mine", "/mine", "mening tadbirlarim"),
            flow("admin.add_event", FSM, "fsm:add_event", {"title": "str", "date": "datetime", "seats": "int"}, "tadbir qo'shiladi", admin=True),
            flow("reminders.day_before", JOB, "job:event_reminder", None, "tadbirdan bir kun oldin eslatma"),
        ],
        "needs": [],
    },
    "support_bot": {
        "entities": {"ticket": {"id": "int", "user_id": "int", "text": "str", "status": "str"},
                     "reply": {"ticket_id": "int", "text": "str", "at": "datetime"}},
        "handlers": _handlers("start", "tickets", "replies", "status", "admin"),
        "flows": [
            flow("ticket.create", FSM, "fsm:ticket", {"subject": "str", "text": "str"}, "murojaat raqami bilan tasdiq"),
            flow("ticket.mine", COMMAND, "/tickets", "/tickets", "mening murojaatlarim va holati"),
            flow("ticket.show", CALLBACK, "cb:ticket:show:<id>", {"ticket_id": "int"}, "murojaat va javoblar"),
            flow("ticket.close", CALLBACK, "cb:ticket:close:<id>", {"ticket_id": "int"}, "murojaat yopiladi"),
            flow("admin.open_list", COMMAND, "/open", "/open", "ochiq murojaatlar", admin=True),
            flow("admin.reply", FSM, "fsm:reply", {"ticket_id": "int", "text": "str"}, "javob foydalanuvchiga yuboriladi", admin=True),
        ],
        "needs": [],
    },
    "habits_bot": {
        "entities": {"habit": {"id": "int", "user_id": "int", "name": "str", "reminder_time": "time"},
                     "checkin": {"habit_id": "int", "date": "date"}},
        "handlers": _handlers("start", "habits", "checkins", "reminders", "admin"),
        "flows": [
            flow("habit.add", FSM, "fsm:add_habit", {"name": "str", "reminder_time": "time"}, "odat saqlanadi"),
            flow("habit.list", COMMAND, "/habits", "/habits", "odatlar ro'yxati (bugun belgilanganlari bilan)"),
            flow("habit.checkin", CALLBACK, "cb:habit:done:<id>", {"habit_id": "int"}, "bugun belgilandi, seriya yangilandi"),
            flow("habit.delete", CALLBACK, "cb:habit:del:<id>", {"habit_id": "int"}, "odat o'chiriladi"),
            flow("streak.show", COMMAND, "/streak", "/streak", "har odat bo'yicha ketma-ket kunlar"),
            flow("report.week", COMMAND, "/week", "/week", "haftalik hisobot"),
            flow("reminder.send", JOB, "job:daily_reminder", None, "belgilangan vaqtda eslatma"),
        ],
        "needs": [],
    },
    "library_bot": {
        "entities": {"book": {"id": "int", "title": "str", "author": "str", "available": "bool"},
                     "loan": {"book_id": "int", "user_id": "int", "due": "date"}},
        "handlers": _handlers("start", "books", "loans", "search", "admin"),
        "flows": [
            flow("books.list", COMMAND, "/books", "/books", "kitoblar ro'yxati (sahifalab)"),
            flow("books.search", FSM, "fsm:search", {"query": "str"}, "topilgan kitoblar"),
            flow("loan.take", CALLBACK, "cb:loan:take:<id>", {"book_id": "int"}, "kitob olindi, qaytarish sanasi"),
            flow("loan.return", CALLBACK, "cb:loan:return:<id>", {"book_id": "int"}, "kitob qaytarildi"),
            flow("loan.mine", COMMAND, "/loans", "/loans", "menda turgan kitoblar"),
            flow("admin.add_book", FSM, "fsm:add_book", {"title": "str", "author": "str"}, "kitob qo'shiladi", admin=True),
            flow("loan.overdue", JOB, "job:overdue_notice", None, "muddati o'tgan kitoblar haqida ogohlantirish"),
        ],
        "needs": [],
    },
    "survey_bot": {
        "entities": {"survey": {"id": "int", "title": "str"},
                     "question": {"id": "int", "survey_id": "int", "text": "str", "kind": "str"},
                     "answer": {"survey_id": "int", "user_id": "int", "question_id": "int", "value": "str"}},
        "handlers": _handlers("start", "surveys", "answering", "results", "admin"),
        "flows": [
            flow("surveys.list", COMMAND, "/surveys", "/surveys", "so'rovnomalar ro'yxati"),
            flow("survey.start", CALLBACK, "cb:survey:start:<id>", {"survey_id": "int"}, "birinchi savol"),
            flow("survey.answer", FSM, "fsm:survey_answer", {"value": "str"}, "javob saqlanadi, keyingi savol"),
            flow("survey.finish", CALLBACK, "cb:survey:finish", None, "rahmat xabari"),
            flow("results.show", COMMAND, "/results", "/results", "natijalar jamlanmasi", admin=True),
            flow("admin.add_survey", FSM, "fsm:add_survey", {"title": "str", "questions": "list[str]"}, "so'rovnoma qo'shiladi", admin=True),
            flow("admin.export", COMMAND, "/export", "/export", "javoblar CSV fayli", admin=True),
        ],
        "needs": [],
    },
    "booking_bot": {
        "entities": {"service": {"id": "int", "name": "str", "duration_min": "int"},
                     "slot": {"id": "int", "service_id": "int", "starts_at": "datetime", "booked": "bool"},
                     "booking": {"id": "int", "user_id": "int", "slot_id": "int", "status": "str"}},
        "handlers": _handlers("start", "services", "slots", "bookings", "admin"),
        "flows": [
            flow("services.list", COMMAND, "/services", "/services", "xizmatlar ro'yxati"),
            flow("slots.pick_date", CALLBACK, "cb:slot:date:<yyyymmdd>", {"date": "str"}, "shu kundagi bo'sh vaqtlar"),
            flow("slots.pick_time", CALLBACK, "cb:slot:time:<id>", {"slot_id": "int"}, "tanlangan vaqt tasdiqqa yuboriladi"),
            flow("booking.confirm", FSM, "fsm:booking", {"name": "str", "phone": "str"}, "band qilindi, tasdiq xabari"),
            flow("booking.mine", COMMAND, "/bookings", "/bookings", "mening bandlarim"),
            flow("booking.cancel", CALLBACK, "cb:booking:cancel:<id>", {"booking_id": "int"}, "band bekor qilinadi"),
            flow("admin.schedule", COMMAND, "/schedule", "/schedule", "kunlik jadval", admin=True),
        ],
        "needs": [],
    },
    "notes_bot": {
        "entities": {"note": {"id": "int", "user_id": "int", "text": "str"},
                     "tag": {"id": "int", "name": "str"},
                     "note_tag": {"note_id": "int", "tag_id": "int"}},
        "handlers": _handlers("start", "notes", "tags", "search", "admin"),
        "flows": [
            flow("note.add", FSM, "fsm:note", {"text": "str"}, "eslatma saqlanadi"),
            flow("note.list", COMMAND, "/notes", "/notes", "oxirgi eslatmalar"),
            flow("note.delete", CALLBACK, "cb:note:del:<id>", {"note_id": "int"}, "eslatma o'chiriladi"),
            flow("tag.add", CALLBACK, "cb:note:tag:<id>:<tag>", {"note_id": "int", "tag": "str"}, "teg qo'shiladi"),
            flow("tag.list", COMMAND, "/tags", "/tags", "teglar va ular bo'yicha eslatmalar soni"),
            flow("note.search", FSM, "fsm:note_search", {"query": "str"}, "topilgan eslatmalar"),
            flow("note.export", COMMAND, "/export", "/export", "eslatmalar matn fayli"),
        ],
        "needs": [],
    },
}
