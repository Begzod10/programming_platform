from datetime import datetime, timedelta, timezone

from app.services.team_project_deadline_reminders import MILESTONES, days_left, message

NOW = datetime(2026, 10, 19, 6, 0, tzinfo=timezone.utc)


def test_days_left_rounds_up_and_goes_negative_when_overdue():
    assert days_left(NOW + timedelta(days=3), NOW) == 3
    assert days_left(NOW + timedelta(hours=5), NOW) == 1
    assert days_left(NOW - timedelta(hours=5), NOW) == 0
    assert days_left(NOW - timedelta(days=2, hours=1), NOW) == -2
    assert days_left((NOW + timedelta(days=2)).replace(tzinfo=None), NOW) == 2          # naive = UTC (SQLite)


def test_message_says_the_number_of_days_in_both_languages():
    head, body = message("Backend API", 3, NOW + timedelta(days=3))
    assert "3 kun" in head and "Backend API" in body and "осталось 3 дн." in body and "22.10.2026" in body


def test_message_for_today_and_overdue_keeps_the_deadline_soft():
    assert "bugun" in message("T", 0, NOW)[0]
    head, body = message("T", -2, NOW - timedelta(days=2))
    assert "2 kun oldin" in head and "topshirishingiz mumkin" in body and "можно сдать" in body


def test_milestones_are_sparse_enough_not_to_nag():
    assert MILESTONES == (7, 3, 1, 0, -1, -3)
