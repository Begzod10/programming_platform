"""Move ALL results of one student account onto another one.

Finds every table with a foreign key to students.id (submissions, quiz
results, lesson completions, early-learning stars, achievements, ...) and
re-points the SOURCE student's rows to the TARGET student. Points/balance
counters on the students row are added onto the target.

Not moved: student_groups (group membership stays as it is).
Rows that would collide with a unique constraint (e.g. both students have
a completion for the same lesson) are left on the source and reported.

Default is a DRY RUN: everything is executed inside one transaction that is
rolled back at the end, so you see the exact counts without changing
anything. Pass --apply to commit.

    cd /home/student_platform/backend && source venv/bin/activate
    python scripts/move_student_results.py --from Feruz1 --to Feruz12
    python scripts/move_student_results.py --from Feruz1 --to Feruz12 --apply
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.database import AsyncSessionLocal

SKIP_TABLES = {"student_groups"}
COUNTERS = ["total_points", "lifetime_points", "balance"]

FK_SQL = """
SELECT kcu.table_name, kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_name = ccu.constraint_name AND tc.table_schema = ccu.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND ccu.table_name = 'students' AND ccu.column_name = 'id'
  AND tc.table_schema = 'public'
ORDER BY kcu.table_name, kcu.column_name
"""


async def main(src_login: str, dst_login: str, apply: bool) -> None:
    async with AsyncSessionLocal() as db:
        async def one(login):
            r = (await db.execute(
                text("SELECT id, username, full_name, total_points, lifetime_points, balance "
                     "FROM students WHERE username = :u"), {"u": login})).mappings().first()
            if r is None:
                sys.exit(f"student not found: {login}")
            return r

        src, dst = await one(src_login), await one(dst_login)
        if src["id"] == dst["id"]:
            sys.exit("source and target are the same account")
        print(f"FROM {src['username']} (id {src['id']}, {src['full_name']})")
        print(f"TO   {dst['username']} (id {dst['id']}, {dst['full_name']})")
        print(f"mode: {'APPLY' if apply else 'DRY RUN (rolled back)'}\n")

        fks = (await db.execute(text(FK_SQL))).all()
        total_moved = total_conflict = 0
        for table, col in fks:
            if table in SKIP_TABLES:
                continue
            tid = (await db.execute(
                text(f'SELECT ctid::text FROM "{table}" WHERE "{col}" = :s'), {"s": src["id"]})).scalars().all()
            if not tid:
                continue
            moved = conflict = 0
            for ctid in tid:
                try:
                    async with db.begin_nested():
                        await db.execute(
                            text(f'UPDATE "{table}" SET "{col}" = :d WHERE ctid::text = :c'),
                            {"d": dst["id"], "c": ctid})
                    moved += 1
                except IntegrityError:
                    conflict += 1
            total_moved += moved
            total_conflict += conflict
            print(f"  {table}.{col}: moved {moved}" + (f", conflict (left on source) {conflict}" if conflict else ""))

        for c in COUNTERS:
            add = src[c] or 0
            if add:
                await db.execute(text(f'UPDATE students SET "{c}" = COALESCE("{c}", 0) + :a WHERE id = :d'),
                                 {"a": add, "d": dst["id"]})
                await db.execute(text(f'UPDATE students SET "{c}" = 0 WHERE id = :s'), {"s": src["id"]})
                print(f"  students.{c}: +{add} to target (source set to 0)")

        print(f"\nrows moved: {total_moved}, conflicts: {total_conflict}")
        if apply:
            await db.commit()
            print("COMMITTED.")
        else:
            await db.rollback()
            print("Dry run — nothing changed. Re-run with --apply to commit.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True, help="source username (results are taken from here)")
    ap.add_argument("--to", dest="dst", required=True, help="target username (results go here)")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    asyncio.run(main(a.src, a.dst, a.apply))
