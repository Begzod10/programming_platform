from datetime import datetime, timedelta, timezone

from app.services.team_project_deadline_reminders import MILESTONES, days_left, message

NOW = datetime(2026, 10, 19, 6, 0, tzinfo=timezone.utc)       # 11:00 in Tashkent


def test_days_left_counts_calendar_days_in_tashkent_time():
    assert days_left(NOW + timedelta(days=3), NOW) == 3
    assert days_left(NOW + timedelta(hours=5), NOW) == 0                          # 16:00 the same local day
    assert days_left(NOW + timedelta(hours=14), NOW) == 1                         # 01:00 tomorrow (local)
    assert days_left(NOW - timedelta(days=2, hours=1), NOW) == -2
    assert days_left((NOW + timedelta(days=2)).replace(tzinfo=None), NOW) == 2    # naive = UTC (SQLite)


def test_the_morning_after_a_late_evening_deadline_is_overdue_not_today():
    deadline = datetime(2026, 10, 21, 18, 59, tzinfo=timezone.utc)                # Wed 23:59 Tashkent
    assert days_left(deadline, datetime(2026, 10, 21, 4, 0, tzinfo=timezone.utc)) == 0     # the 09:00 run on the day
    assert days_left(deadline, datetime(2026, 10, 22, 4, 0, tzinfo=timezone.utc)) == -1    # the morning after


def test_message_says_the_number_of_days_in_both_languages():
    head, body = message("Backend API", 3, NOW + timedelta(days=3))
    assert "3 kun" in head and "Backend API" in body and "осталось 3 дн." in body and "22.10.2026" in body


def test_message_for_today_and_overdue_keeps_the_deadline_soft():
    assert "bugun" in message("T", 0, NOW)[0]
    head, body = message("T", -2, NOW - timedelta(days=2))
    assert "2 kun oldin" in head and "topshirishingiz mumkin" in body and "можно сдать" in body


def test_milestones_are_sparse_enough_not_to_nag():
    assert MILESTONES == (7, 3, 1, 0, -1, -3)
