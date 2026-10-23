from app.config import settings


def test_pool_defaults_leave_room_for_a_burst_of_simultaneous_requests():
    assert settings.DB_POOL_SIZE + settings.DB_MAX_OVERFLOW >= 30      # the old 5 + 10 ran dry in a team game


def test_pool_options_are_postgresql_only_and_sqlite_keeps_its_own_pooling():
    import app.db.database as database
    assert settings.DATABASE_URL.startswith("sqlite")                  # the test suite runs on SQLite
    assert database._pool_options == {}
