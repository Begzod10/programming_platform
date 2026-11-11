"""Sticker catalog invariants (see app/services/early_sticker_catalog.py)."""
from app.services.early_sticker_catalog import (
    CATALOG, DAILY_STICKERS, STAR_STICKERS, STREAK_STICKERS,
)


def test_counts_and_keys():
    assert [s.key for s in STAR_STICKERS] == [f"star:{n}" for n in range(10, 511, 10)]
    assert [s.key for s in DAILY_STICKERS] == [f"daily:{n:02d}" for n in range(1, 27)]
    assert [s.key for s in STREAK_STICKERS] == ["streak:3", "streak:7", "streak:14", "streak:30"]
    assert len(CATALOG) == 81


def test_emoji_unique_and_names_filled():
    all_ = STAR_STICKERS + DAILY_STICKERS + STREAK_STICKERS
    assert len({s.emoji for s in all_}) == len(all_)
    assert all(s.name.strip() and s.name_ru.strip() for s in all_)


def test_rarity():
    by = {s.key: s.rarity for s in STAR_STICKERS}
    assert by["star:50"] == "rare" and by["star:500"] == "rare" and by["star:10"] == "common"
    assert {s.rarity for s in DAILY_STICKERS} == {"common"}
    assert {s.rarity for s in STREAK_STICKERS} == {"epic"}


def test_award_table_registered():
    from app.db import base
    assert "early_sticker_awards" in base.Base.metadata.tables
