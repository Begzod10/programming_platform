"""One-shot content-rollout script (already run in production — see
early_activity ids 57-154) that took every early-learning game category
from a mix of 1-8 activities up to a uniform 10 activities / 30 stars each.
Kept in the repo as a record of how that content was authored/validated,
same spirit as _seed_early_learning.py for the original catalog — not
meant to be re-run (it would insert a second copy of everything).

Validates every new activity structurally + logically (maze solvability,
count/pattern/cause_effect answer correctness, id uniqueness) before
touching the DB — see the VALIDATORS registry below. These were pure
INSERTs (no existing row modified), so a rollback would just be
DELETE FROM early_activities WHERE id BETWEEN 57 AND 154.

Sibling data files: _early_learning_30stars_data.py (select/maze/count/
sort/sequence/pattern/cause_effect/seasons/transport, content-generated)
and _early_learning_30stars_trace_build.py (trace/build, hand-authored to
reuse exact frontend-tuned geometry — see that file's own docstring).
"""
from __future__ import annotations

import asyncio
import json
from collections import deque

import _early_learning_30stars_data as D  # noqa: E402
import _early_learning_30stars_trace_build as TB  # noqa: E402

MODE_TO_TYPE = {
    "select": "match", "build": "match", "pattern": "match", "cause_effect": "match",
    "trace": "trace", "maze": "maze", "count": "count", "sort": "sort", "sequence": "sequence",
}

# module_id -> (name, activities list)
PLAN = [
    (5, "Kasblar shaharchasi (professions)", D.PROFESSIONS),
    (6, "Fasllar dunyosi (seasons)", D.SEASONS),
    (10, "Yasash o'yinlari (build)", TB.BUILD_ACTIVITIES),
    (7, "Hayvonot olami (animals)", D.ANIMALS),
    (11, "Chizib o'rganamiz (trace)", TB.TRACE_ACTIVITIES),
    (8, "Transport olami (transport)", D.TRANSPORT),
    (12, "Yo'lni topamiz (maze)", D.MAZE),
    (9, "Rang olami (colors)", D.COLORS),
    (13, "Dengiz olami (ocean)", D.OCEAN),
    (15, "Sanashni o'rganamiz (count)", D.COUNT),
    (16, "Mevami, sabzavotmi? (sort)", D.SORT),
    (17, "Kun tartibi (sequence)", D.SEQUENCE),
    (18, "Naqshni davom ettiramiz (pattern)", D.PATTERN),
    (19, "Sabab va natija (cause_effect)", D.CAUSE_EFFECT),
]

KNOWN_SHAPES = {"circle", "square", "triangle", "star", "rectangle", "diamond", "pentagon"}


def _req(cond, msg):
    if not cond:
        raise AssertionError(msg)


def validate_select_like(a, mode):
    c = a["content"]
    ci = c["correct_items"]
    di = c.get("distractor_items", [])
    _req(len(ci) >= 3, f"{a['title']}: too few correct_items ({len(ci)})")
    ids = set()
    for item in ci + di:
        for k in ("id", "label", "label_ru", "emoji"):
            _req(k in item and item[k], f"{a['title']}: item missing {k}: {item}")
        _req(item["id"] not in ids, f"{a['title']}: duplicate id {item['id']!r}")
        ids.add(item["id"])
    _req("character" in c and c["character"].get("emoji"), f"{a['title']}: missing character emoji")


def validate_build(a):
    c = a["content"]
    _req(c.get("scene") in ("snowman", "house"), f"{a['title']}: unknown scene {c.get('scene')!r}")
    slots = c["slots"]
    _req(len(slots) >= 4, f"{a['title']}: too few slots")
    ids = set()
    for s in slots:
        for k in ("id", "label", "label_ru", "emoji", "x", "y", "w", "h"):
            _req(k in s, f"{a['title']}: slot missing {k}: {s}")
        _req(0 <= s["x"] <= 100 and 0 <= s["y"] <= 100, f"{a['title']}: slot {s['id']} out of 0-100 range")
        _req(s["id"] not in ids or "matchGroup" in s, f"{a['title']}: dup slot id {s['id']}")
        ids.add(s["id"])
    for d in c.get("distractor_items", []):
        for k in ("id", "label", "label_ru", "emoji"):
            _req(k in d, f"{a['title']}: distractor missing {k}")


def validate_trace(a):
    c = a["content"]
    targets = c["targets"]
    _req(len(targets) >= 1, f"{a['title']}: no targets")
    for t in targets:
        _req(t["shape"] in KNOWN_SHAPES, f"{a['title']}: unknown shape {t['shape']!r}")
        for k in ("id", "label", "label_ru"):
            _req(k in t, f"{a['title']}: target missing {k}")


def _maze_solvable(rows, cols, start, end, walls):
    wall_set = {tuple(w) for w in walls}
    start, end = tuple(start), tuple(end)
    if start in wall_set or end in wall_set:
        return False
    seen = {start}
    q = deque([start])
    while q:
        r, c = q.popleft()
        if (r, c) == end:
            return True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in wall_set and (nr, nc) not in seen:
                seen.add((nr, nc))
                q.append((nr, nc))
    return False


def validate_maze(a):
    c = a["content"]
    rows, cols = c["grid"]["rows"], c["grid"]["cols"]
    start, end = c["start"], c["end"]
    walls = c["walls"]
    _req(0 <= start[0] < rows and 0 <= start[1] < cols, f"{a['title']}: start out of bounds")
    _req(0 <= end[0] < rows and 0 <= end[1] < cols, f"{a['title']}: end out of bounds")
    for w in walls:
        _req(0 <= w[0] < rows and 0 <= w[1] < cols, f"{a['title']}: wall {w} out of bounds")
    _req(_maze_solvable(rows, cols, start, end, walls), f"{a['title']}: MAZE NOT SOLVABLE — {c}")


def validate_count(a):
    for r in a["content"]["rounds"]:
        opts = r["options"]
        _req(len(opts) == 4 and len(set(opts)) == 4, f"{a['title']}: options not 4 distinct: {opts}")
        _req(opts == sorted(opts), f"{a['title']}: options not ascending: {opts}")
        _req(all(o >= 1 for o in opts), f"{a['title']}: option < 1: {opts}")
        _req(r["count"] in opts, f"{a['title']}: count {r['count']} not in options {opts}")


def validate_sort(a):
    c = a["content"]
    bins_ = c["bins"]
    _req(len(bins_) == 2, f"{a['title']}: expected 2 bins, got {len(bins_)}")
    bin_ids = {b["id"] for b in bins_}
    items = c["items"]
    _req(len(items) >= 6, f"{a['title']}: too few items ({len(items)})")
    ids = set()
    per_bin = {bid: 0 for bid in bin_ids}
    for it in items:
        _req(it["bin"] in bin_ids, f"{a['title']}: item {it['id']} bin {it['bin']!r} not in {bin_ids}")
        _req(it["id"] not in ids, f"{a['title']}: dup item id {it['id']}")
        ids.add(it["id"])
        per_bin[it["bin"]] += 1
    _req(all(v >= 2 for v in per_bin.values()), f"{a['title']}: a bin has <2 items: {per_bin}")


def validate_sequence(a):
    steps = a["content"]["steps"]
    _req(len(steps) >= 3, f"{a['title']}: too few steps ({len(steps)})")
    ids = set()
    for s in steps:
        for k in ("id", "emoji", "label", "label_ru"):
            _req(k in s, f"{a['title']}: step missing {k}")
        _req(s["id"] not in ids, f"{a['title']}: dup step id {s['id']}")
        ids.add(s["id"])


def _pattern_expected_next(seq):
    """Smallest period P (1..len-1) such that seq[i] == seq[i-P] for all i>=P.
    Returns the expected next element (seq[len-P]) for the smallest such P,
    or None if the sequence has no clean repeating period at all."""
    n = len(seq)
    for p in range(1, n):
        if all(seq[i] == seq[i - p] for i in range(p, n)):
            return seq[n - p]
    return None


def validate_pattern(a):
    for r in a["content"]["rounds"]:
        seq = r["sequence"]
        _req(len(seq) >= 4, f"{a['title']}: sequence too short: {seq}")
        expected = _pattern_expected_next(seq)
        _req(expected is not None, f"{a['title']}: no clean repeating period in {seq}")
        _req(r["answer"] == expected, f"{a['title']}: answer {r['answer']!r} != expected continuation {expected!r} for {seq}")
        _req(r["answer"] == r["options"][0], f"{a['title']}: answer not first option: {r}")
        _req(len(set(r["options"])) == len(r["options"]), f"{a['title']}: duplicate options: {r['options']}")


def validate_cause_effect(a):
    for r in a["content"]["rounds"]:
        opt_ids = [o["id"] for o in r["options"]]
        _req(len(set(opt_ids)) == len(opt_ids), f"{a['title']}: dup option ids: {opt_ids}")
        _req(r["answer"] in opt_ids, f"{a['title']}: answer {r['answer']!r} not among options {opt_ids}")
        _req(r["answer"] == opt_ids[0], f"{a['title']}: answer not the first option: {r}")
        for o in r["options"]:
            for k in ("id", "emoji", "label", "label_ru"):
                _req(k in o, f"{a['title']}: option missing {k}")


VALIDATORS = {
    "select": lambda a: validate_select_like(a, "select"),
    "build": validate_build,
    "trace": validate_trace,
    "maze": validate_maze,
    "count": validate_count,
    "sort": validate_sort,
    "sequence": validate_sequence,
    "pattern": validate_pattern,
    "cause_effect": validate_cause_effect,
}


def validate_all():
    total = 0
    for module_id, name, activities in PLAN:
        for a in activities:
            for k in ("title", "title_ru", "instruction_text", "instruction_text_ru", "content"):
                _req(k in a and a[k], f"[module {module_id} {name}] activity missing {k}: {a.get('title')}")
            mode = a["content"]["mode"]
            _req(mode in VALIDATORS, f"[module {module_id}] unknown mode {mode!r}")
            VALIDATORS[mode](a)
            total += 1
    print(f"Validation OK — {total} activities across {len(PLAN)} modules")
    return total


async def insert_all():
    from sqlalchemy import select, func  # noqa: E402
    from app.db import base as _all_models  # noqa: E402,F401
    from app.db.database import AsyncSessionLocal  # noqa: E402
    from app.models.early_learning import EarlyActivity  # noqa: E402

    async with AsyncSessionLocal() as db:
        created_ids = []
        for module_id, name, activities in PLAN:
            max_order = (
                await db.execute(select(func.max(EarlyActivity.order)).where(EarlyActivity.module_id == module_id))
            ).scalar() or 0
            next_order = max_order + 1
            for a in activities:
                mode = a["content"]["mode"]
                row = EarlyActivity(
                    module_id=module_id,
                    title=a["title"],
                    title_ru=a["title_ru"],
                    order=next_order,
                    activity_type=MODE_TO_TYPE[mode],
                    instruction_text=a["instruction_text"],
                    instruction_text_ru=a["instruction_text_ru"],
                    content_json=json.dumps(a["content"], ensure_ascii=False),
                    max_stars=3,
                    is_active=True,
                    is_published=True,
                )
                db.add(row)
                next_order += 1
            await db.flush()
            new_rows = (
                await db.execute(
                    select(EarlyActivity.id).where(EarlyActivity.module_id == module_id, EarlyActivity.order >= max_order + 1)
                )
            ).scalars().all()
            created_ids.extend(new_rows)
            print(f"module {module_id} ({name}): inserted {len(activities)} activities, new ids {min(new_rows)}-{max(new_rows)}")
        await db.commit()
        print(f"\nTotal inserted: {len(created_ids)}")
        print(f"ID range: {min(created_ids)}-{max(created_ids)}")
        with open("/tmp/new_early_activity_ids.txt", "w") as f:
            f.write(",".join(str(i) for i in sorted(created_ids)))


if __name__ == "__main__":
    validate_all()
    asyncio.run(insert_all())
