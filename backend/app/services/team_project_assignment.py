"""Deterministic split of a blueprint among the team's members.

The AI used to decide which member gets which file and endpoint, and kept breaking the integrability
rules (a file in two tasks or none, JavaScript for someone who never studied it, the wrong level).
The split is a pure function of the blueprint and the members' finished areas, so it is computed here;
the model only writes the human text of each piece (title, description, acceptance criteria).

`assign_blueprint` returns one skeleton task per member (index == member index) that already satisfies
`validate_plan`; it raises `AssignmentImpossible` when the team cannot cover the blueprint (the caller
then falls back to free-form AI planning).
"""
from __future__ import annotations

import re

from app.services.team_project_constants import SKILL_AREAS
from app.services.team_project_planner import (
    _BACKEND_AREAS, _CODE_FILE_EXT, _beginner_markup_task, _has_area, _norm_file, skeleton_owner_index,
)

LEVELS = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
_MARKUP_EXT = (".html", ".css")
_BACKEND_PREFIXES = ("backend/", "bot/")


class AssignmentImpossible(Exception):
    pass


def _ext(path: str) -> str:
    return "." + path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""


def _is_backend_file(path: str) -> bool:
    return path.startswith(_BACKEND_PREFIXES) or path == ".env.example"


def _candidate_areas(member: dict) -> list[str]:
    areas = [a for a in SKILL_AREAS if _has_area(member, a)]
    if not areas and _beginner_markup_task(member, "html_css"):
        return ["html_css"]
    return areas


def _python_blocked(member: dict, members: list[dict]) -> bool:
    """Mirror of validate_plan's rule: nobody without Python experience gets Python code while a teammate has it."""
    return any(m.get("has_python") for m in members) and not member.get("has_python", True)


def _area_for(member: dict, files: list[str], members: list[dict], preferred: list[str]) -> str | None:
    """The skill area a task owning `files` would declare for `member`, or None when the member cannot do it."""
    code_sets = [_CODE_FILE_EXT[_ext(f)] for f in files if _ext(f) in _CODE_FILE_EXT]
    if any(_ext(f) == ".py" for f in files) and _python_blocked(member, members):
        return None
    candidates = _candidate_areas(member)
    if not candidates:
        return None
    if code_sets:
        # every code file must be covered by SOME area the member finished (a full-stack member may mix two)
        if not all(any(a in s for a in candidates) for s in code_sets):
            return None
        covers = {a: sum(a in s for s in code_sets) for a in candidates}
        best = max(covers.values())
        candidates = [a for a in candidates if covers[a] == best]
    else:
        # markup only: any finished area is formally fine, but html_css is the honest one
        candidates = sorted(candidates, key=lambda a: (a != "html_css", a))
    for a in preferred:
        if a in candidates:
            return a
    return candidates[0]


def _level_in(member: dict, area: str) -> str:
    if _beginner_markup_task(member, area):
        return "Beginner"
    return (member.get("area_levels") or {}).get(area) or member["level"]


def _split_frontend(frontend: list[str]) -> tuple[list[str], list[str]]:
    markup = [f for f in frontend if _ext(f) in _MARKUP_EXT]
    scripts = [f for f in frontend if _ext(f) not in _MARKUP_EXT]
    return markup, scripts


def _endpoint_groups(blueprint: dict) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for e in blueprint["endpoints"]:
        groups.setdefault(e["id"].split(".", 1)[0], []).append(e["id"])
    return groups


def assign_blueprint(blueprint: dict, members: list[dict]) -> list[dict]:
    n = len(members)
    files = blueprint["files"]
    family_areas = _BACKEND_AREAS.get(blueprint.get("backend_family"), [])
    preferred = list(family_areas) + ["javascript", "html_css"]
    owner = skeleton_owner_index(members, blueprint)

    held: list[list[str]] = [[] for _ in range(n)]
    weight = [0] * n

    skeleton = list(files["skeleton"])
    if _area_for(members[owner], skeleton, members, preferred) is None:
        raise AssignmentImpossible(f"skeleton owner {owner} cannot own {skeleton}")
    held[owner] += skeleton
    weight[owner] += 2

    markup, scripts = _split_frontend(list(files["frontend"]))
    backend_units = [("backend", f) for f in files["backend"]]
    unit_order = backend_units + [("js", f) for f in scripts] + [("markup", f) for f in markup]
    unassigned = list(unit_order)

    def feasible(i: int, unit_file: str) -> bool:
        # Express routes are .js, the same language as the frontend: a JavaScript-only member could formally cover
        # them but has never studied Express, so server .js files need the backend's own course (node).
        # (Python server files are already limited to Python-family areas by the extension check.)
        if (_is_backend_file(unit_file) and _ext(unit_file) == ".js"
                and not any(_has_area(members[i], a) for a in family_areas)):
            return False
        return _area_for(members[i], held[i] + [unit_file], members, preferred) is not None

    def give(i: int, unit: tuple[str, str]) -> None:
        held[i].append(unit[1])
        weight[i] += 1 if unit[0] == "markup" else 2
        unassigned.remove(unit)

    # Pass 1: everybody gets a piece. The weakest members (fewest finished areas) choose first and
    # take the lightest pieces they can do; stronger members take backend / script pieces.
    def rank(i: int):
        return (len(_candidate_areas(members[i])), i)

    for i in sorted((i for i in range(n) if not held[i]), key=rank):
        markup_only = all(a == "html_css" for a in _candidate_areas(members[i]))
        kinds = ["markup", "js", "backend"] if markup_only else ["backend", "js", "markup"]
        pick = next((u for k in kinds for u in unassigned if u[0] == k and feasible(i, u[1])), None)
        if pick is None:
            raise AssignmentImpossible(f"member {i} cannot take any piece")
        give(i, pick)

    # Pass 2: the rest, heaviest kinds first, to whoever can do it and has the least so far.
    for unit in list(unassigned):
        able = [i for i in range(n) if feasible(i, unit[1])]
        if not able:
            raise AssignmentImpossible(f"nobody can take {unit[1]}")
        give(min(able, key=lambda i: (weight[i], -LEVELS.get(_level_in(members[i], _area_for(
            members[i], held[i] + [unit[1]], members, preferred)), 0), i)), unit)

    # Endpoints: bots tie flows to handler files by name; web teams share them among the backend holders.
    holders = [i for i in range(n) if any(_is_backend_file(f) for f in held[i])]
    produces: list[list[str]] = [[] for _ in range(n)]
    groups = _endpoint_groups(blueprint)
    if blueprint.get("kind") == "bot":
        by_stem = {f.rsplit("/", 1)[-1].rsplit(".", 1)[0]: i for i in range(n) for f in held[i] if f.startswith("bot/handlers/")}
        for prefix, ids in groups.items():
            produces[by_stem.get(prefix, by_stem.get("start", owner))] += ids
    else:
        script_owner = {f.rsplit("/", 1)[-1].rsplit(".", 1)[0]: i for i in range(n) for f in held[i]
                        if f.startswith("frontend/") and _ext(f) == ".js"}
        for prefix, ids in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            # the member who writes the page that calls these endpoints writes them too, when they can
            same_page = next((i for stem, i in script_owner.items()
                              if i in holders and (stem.startswith(prefix) or prefix.startswith(stem))), None)
            target = same_page if same_page is not None and len(produces[same_page]) <= min(
                len(produces[h]) for h in holders) + len(ids) else min(holders, key=lambda i: (len(produces[i]), i))
            produces[target] += ids

    # What each frontend script calls (a different task must produce it), and bot handlers waiting for the core.
    core_holder = next((i for i in range(n) if "bot/core/db.py" in held[i]), None)
    tasks = []
    for i in range(n):
        area = _area_for(members[i], held[i], members, preferred)
        scripts_here = [f for f in held[i] if f.startswith("frontend/") and _ext(f) == ".js"]
        consumes: list[str] = []
        for f in scripts_here:
            stem = f.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            wanted = [e["id"] for e in blueprint["endpoints"]
                      if (e["id"].split(".", 1)[0].startswith(stem) or stem.startswith(e["id"].split(".", 1)[0]))
                      and e["id"] not in produces[i]]
            consumes += [e for e in (wanted or [x["id"] for x in blueprint["endpoints"] if x["id"] not in produces[i]])[:2]
                         if e not in consumes]
        depends = [core_holder] if (core_holder is not None and core_holder != i
                                    and any(f.startswith("bot/handlers/") for f in held[i])) else []
        tasks.append({
            "assign_to_member_index": i,
            "required_level": _level_in(members[i], area),
            "interface_contract": {"files": list(held[i]), "produces": list(produces[i]),
                                   "consumes": consumes, "skill_area": area},
            "depends_on": depends,
            "estimated_hours": max(2, min(14, round(1.5 * len(held[i]) + 0.5 * len(produces[i])))),
        })
    return tasks


# --- the text the model still writes -----------------------------------------------------------------

def _describe_endpoint(e: dict, bot: bool) -> str:
    if bot:
        return f"{e['id']} ({e['method']} {e['path']}): kirish {e['request']!r} -> bot javobi {e['response']!r}"
    return f"{e['id']}: {e['method']} {e['path']} | so'rov: {e['request']!r} | javob: {e['response']!r}"


def build_text_prompt(theme_label: str, stack: dict, members: list[dict], blueprint: dict, skeleton: list[dict]) -> str:
    from app.services.team_project_planner import (
        MIN_ACCEPTANCE_CRITERIA, MIN_DESCRIPTION_LEN, _INJECTION_GUARD,
    )
    bot = blueprint.get("kind") == "bot"
    endpoints = {e["id"]: e for e in blueprint["endpoints"]}
    blocks = []
    for t in skeleton:
        i = t["assign_to_member_index"]
        c = t["interface_contract"]
        m = members[i]
        lines = [f"{i}. {m['full_name']} — daraja {t['required_level']}, soha {c['skill_area']}",
                 f"   Fayllar: {', '.join(c['files'])}"]
        if c["produces"]:
            lines.append("   Amalga oshiradi:\n" + "\n".join(f"     - {_describe_endpoint(endpoints[x], bot)}" for x in c["produces"]))
        if c["consumes"]:
            lines.append("   Foydalanadi (boshqa a'zo yozgan): " + ", ".join(c["consumes"]))
        if t["depends_on"]:
            lines.append(f"   Tayanadi: {t['depends_on']}-vazifa tayyor bo'lgach")
        lines.append(f"   A'zo xulosasi: <student_input>{m['summary']}</student_input>")
        blocks.append("\n".join(lines))
    kind = f"{stack['label']} (frontendsiz Telegram bot)" if bot else f"{stack['frontend']} (frontend) va {stack['backend']} (backend)"
    return f"""Sen tajribali dasturlash o'qituvchisisiz. {len(members)} nafar o'quvchidan iborat jamoa "{theme_label}" mavzusida, {kind} texnologiyalarida kichik, real loyiha quradi.

{_INJECTION_GUARD}

Loyiha shartnomasi va har bir a'zoning qismi (fayllar, endpoint/oqimlar, soha, daraja) TAYYOR va O'ZGARMAYDI. Sening vazifang — har bir qism uchun o'quvchiga tushunarli matn yozish.

QISMLAR (indeks — a'zo):
{chr(10).join(blocks)}

TALABLAR:
- `tasks` ro'yxatida har bir indeks uchun aynan bitta yozuv bo'lsin; `index` — yuqoridagi indeks. Fayl, endpoint, soha, daraja haqida hech narsa o'zgartirma va yangisini o'ylab topma.
- `description` — o'quvchi hech kimdan so'ramasdan ishni boshlay oladigan darajada aniq (kamida {MIN_DESCRIPTION_LEN} belgi, amalda 2-4 jumla): aynan shu qismdagi fayllar va endpoint/oqimlar nima qilishi kerakligini yoz.
- Qism darajasiga mos bo'lsin: Beginner uchun sodda, aniq qadamli ish; Advanced uchun murakkab mantiq (validatsiya, xatolarni boshqarish, holat).
- Faqat a'zoning xulosasida uchraydigan texnologiyalardan foydalan; yangi framework yoki kutubxona (Redux, TypeScript, Tailwind, Bootstrap va h.k.) QO'SHMA.
- `acceptance_criteria` kamida {MIN_ACCEPTANCE_CRITERIA} ta ANIQ, tekshirib bo'ladigan band (masalan "Noto'g'ri parolda forma ustida xato xabari chiqadi" — "Yaxshi ishlaydi" emas).
- `title_ru`, `description_ru`, `acceptance_criteria_ru` — o'zbekcha matnning tabiiy, TO'LIQ ruscha varianti (har band uchun bitta rus bandi, bir xil tartibda). Bo'sh yoki o'zbekcha qoldirish TAQIQLANADI.
- `project_title` va `project_description` — loyihaning qisqa nomi va tavsifi (uzbekcha).

JAVOB FORMATI — faqat quyidagi JSON, boshqa hech narsa yozma:
{{
  "project_title": "...",
  "project_description": "...",
  "tasks": [
    {{
      "index": 0,
      "title": "Login sahifasi", "title_ru": "Страница входа",
      "description": "Foydalanuvchi nomi va parol maydonlari bo'lgan login formasi yasang. Muvaffaqiyatli kirishda /dashboard sahifasiga yo'naltiring, xato bo'lsa forma ustida qizil xato xabari chiqsin.",
      "description_ru": "Создайте форму входа с полями имени пользователя и пароля. При успешном входе перенаправляйте на страницу /dashboard, при ошибке показывайте красное сообщение об ошибке над формой.",
      "acceptance_criteria": ["To'g'ri login/parolda /dashboard'ga yo'naltiradi", "Noto'g'ri parolda forma ustida xato xabari chiqadi"],
      "acceptance_criteria_ru": ["При верном логине и пароле перенаправляет на /dashboard", "При неверном пароле над формой показывается сообщение об ошибке"]
    }}
  ]
}}
"""


_TEXT_FIELDS = ("title", "title_ru", "description", "description_ru", "acceptance_criteria", "acceptance_criteria_ru")


def merge_texts(skeleton: list[dict], parsed: dict | None) -> dict:
    """The fixed assignment plus the model's text, matched by `index` (or by position when the index is missing)."""
    if not isinstance(parsed, dict) or not isinstance(parsed.get("tasks"), list):
        raise ValueError("AI did not return a usable plan")
    by_index: dict[int, dict] = {}
    for pos, item in enumerate(parsed["tasks"]):
        if isinstance(item, dict):
            idx = item.get("index", item.get("assign_to_member_index", pos))
            if isinstance(idx, int) and idx not in by_index:
                by_index[idx] = item
    tasks = []
    for t in skeleton:
        text = by_index.get(t["assign_to_member_index"], {})
        merged = {**{k: text.get(k) for k in _TEXT_FIELDS}, **t}
        merged["interface_contract"] = dict(t["interface_contract"])
        tasks.append(merged)
    return {
        "project_title": str(parsed.get("project_title") or "Jamoaviy loyiha")[:300],
        "project_description": str(parsed.get("project_description") or ""),
        "tasks": tasks,
    }


def build_text_repair_prompt(prompt: str, parsed: dict | None, errors: list[str]) -> str:
    import json
    shown = json.dumps(parsed, ensure_ascii=False)[:6000] if parsed else "(yo'q)"
    problems = "\n".join(f"- {e}" for e in errors[:15])
    return (f"{prompt}\n\nDIQQAT: avvalgi javobingizda quyidagi XATOLAR topildi:\n{problems}\n\n"
            f"Avvalgi javobingiz:\n{shown}\n\n"
            "Faqat matnni tuzating (fayl/endpoint/daraja o'zgarmaydi) va TO'LIQ JSONni qaytaring (faqat JSON).")
