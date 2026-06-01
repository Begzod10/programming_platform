"""Compare live DB schema against SQLAlchemy model metadata.

Usage:
    python scripts/check_schema_drift.py

Reports, per table:
  - columns declared in models but missing in DB
  - columns present in DB but not in models
  - column type / nullable / default mismatches
  - missing unique constraints / indexes (name + columns)

Exit code 0 = clean, 1 = drift found, 2 = connection error.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make `app.*` importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import MetaData  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 — registers all models


_TYPE_ALIASES = {
    # Generic SQLAlchemy ↔ what Postgres reports via reflect()
    "DATETIME": "TIMESTAMP",
    "FLOAT": "DOUBLEPRECISION",
}


def _norm_type(t: str) -> str:
    s = str(t).upper().replace(" ", "")
    return _TYPE_ALIASES.get(s, s)


def _col_signature(col) -> tuple:
    """Compact comparable column signature.

    Notes:
    - Type is normalized so DATETIME/TIMESTAMP and FLOAT/DOUBLEPRECISION don't
      flag as drift on Postgres.
    - Only ``server_default`` counts — Python-side ``default=`` is invisible to
      the DB and would always look like drift after reflect().
    - Autoincrement INTEGER PKs reflect with a ``nextval(...)`` server_default;
      we ignore the default bit for them.
    """
    is_autoincrement_pk = bool(
        col.primary_key
        and col.autoincrement is True
        and _norm_type(col.type) == "INTEGER"
    )
    has_server_default = col.server_default is not None and not is_autoincrement_pk
    return (_norm_type(col.type), bool(col.nullable), has_server_default)


def _index_signature(ix) -> tuple:
    return (ix.unique, tuple(c.name for c in ix.columns))


def _uq_signature(uq) -> tuple:
    return tuple(c.name for c in uq.columns)


async def main() -> int:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    model_md = _base.Base.metadata
    live_md = MetaData()

    try:
        async with engine.connect() as conn:
            await conn.run_sync(live_md.reflect)
    except Exception as e:
        print(f"[ERROR] reflect failed: {e}")
        return 2
    finally:
        await engine.dispose()

    model_tables = set(model_md.tables.keys())
    live_tables = set(live_md.tables.keys())

    drift = False

    missing_tables = model_tables - live_tables
    if missing_tables:
        drift = True
        print(f"[MISSING TABLES] {sorted(missing_tables)}")

    extra_tables = live_tables - model_tables - {"alembic_version"}
    if extra_tables:
        print(f"[EXTRA TABLES]   {sorted(extra_tables)}  (not in models — review)")

    shared = sorted(model_tables & live_tables)
    for tname in shared:
        m_tab = model_md.tables[tname]
        l_tab = live_md.tables[tname]
        issues = []

        m_cols = {c.name: c for c in m_tab.columns}
        l_cols = {c.name: c for c in l_tab.columns}

        for cname in m_cols.keys() - l_cols.keys():
            issues.append(f"  + column missing in DB: {cname} ({m_cols[cname].type})")
        for cname in l_cols.keys() - m_cols.keys():
            issues.append(f"  - column extra in DB:   {cname} ({l_cols[cname].type})")

        for cname in m_cols.keys() & l_cols.keys():
            m_sig = _col_signature(m_cols[cname])
            l_sig = _col_signature(l_cols[cname])
            if m_sig != l_sig:
                issues.append(
                    f"  ~ column drift {cname}: model={m_sig} db={l_sig}"
                )

        # Indexes — compare by signature only (names vary).
        m_ix = {_index_signature(ix) for ix in m_tab.indexes}
        l_ix = {_index_signature(ix) for ix in l_tab.indexes}
        for sig in m_ix - l_ix:
            issues.append(f"  + index missing in DB: unique={sig[0]} cols={sig[1]}")

        # Unique constraints — same.
        m_uq = {_uq_signature(uq) for uq in m_tab.constraints if uq.__class__.__name__ == "UniqueConstraint"}
        l_uq = {_uq_signature(uq) for uq in l_tab.constraints if uq.__class__.__name__ == "UniqueConstraint"}
        for sig in m_uq - l_uq:
            # If a matching unique index already covers it, don't double-flag.
            if (True, sig) in l_ix:
                continue
            issues.append(f"  + unique constraint missing in DB: cols={sig}")

        if issues:
            drift = True
            print(f"\n[DRIFT] {tname}")
            for line in issues:
                print(line)

    if not drift:
        print("Schema clean — models and DB agree.")
        return 0
    print("\nDrift detected.")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
