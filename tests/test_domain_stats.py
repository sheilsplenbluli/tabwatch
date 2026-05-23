import pytest
from datetime import datetime, timezone, timedelta
from app.services import visit_store
from app.services.domain_stats import (
    get_busiest_hour,
    get_busiest_day,
    get_domain_visit_count,
    get_total_time_seconds,
    get_stats_summary,
)
from app.models.domain_visit import DomainVisit
from app import create_app


@pytest.fixture(autouse=True)
def reset_store():
    visit_store._store.clear()
    visit_store._counter = 0
    yield
    visit_store._store.clear()
    visit_store._counter = 0


START = datetime(2024, 6, 3, 0, 0, 0, tzinfo=timezone.utc)  # Monday
END = datetime(2024, 6, 9, 23, 59, 59, tzinfo=timezone.utc)  # Sunday


def make_closed_visit(user_id, domain, start: datetime, duration_seconds: float):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    end = start + timedelta(seconds=duration_seconds)
    v.close(end_time=end)
    visit_store.add_visit(v)
    return v


def test_total_time_seconds_sums_correctly():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 300)
    make_closed_visit("u1", "b.com", datetime(2024, 6, 4, 14, 0, tzinfo=timezone.utc), 600)
    total = get_total_time_seconds("u1", START, END)
    assert total == 900.0


def test_total_time_excludes_out_of_range():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc), 300)
    total = get_total_time_seconds("u1", START, END)
    assert total == 0.0


def test_busiest_hour_returns_correct_hour():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc), 120)
    make_closed_visit("u1", "b.com", datetime(2024, 6, 3, 9, 30, tzinfo=timezone.utc), 300)
    make_closed_visit("u1", "c.com", datetime(2024, 6, 3, 14, 0, tzinfo=timezone.utc), 60)
    hour = get_busiest_hour("u1", START, END)
    assert hour == 9


def test_busiest_hour_no_visits_returns_none():
    assert get_busiest_hour("u1", START, END) is None


def test_busiest_day_returns_correct_day():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 100)  # Monday
    make_closed_visit("u1", "b.com", datetime(2024, 6, 5, 10, 0, tzinfo=timezone.utc), 900)  # Wednesday
    day = get_busiest_day("u1", START, END)
    assert day == "Wednesday"


def test_domain_visit_count_correct():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 60)
    make_closed_visit("u1", "a.com", datetime(2024, 6, 4, 10, 0, tzinfo=timezone.utc), 60)
    make_closed_visit("u1", "b.com", datetime(2024, 6, 4, 10, 0, tzinfo=timezone.utc), 60)
    count = get_domain_visit_count("u1", "a.com", START, END)
    assert count == 2


def test_stats_summary_has_expected_keys():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 120)
    summary = get_stats_summary("u1", START, END)
    assert "total_seconds" in summary
    assert "total_minutes" in summary
    assert "busiest_hour" in summary
    assert "busiest_day" in summary
    assert summary["total_seconds"] == 120.0


def test_stats_summary_different_users_isolated():
    make_closed_visit("u1", "a.com", datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 200)
    make_closed_visit("u2", "b.com", datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 500)
    assert get_total_time_seconds("u1", START, END) == 200.0
    assert get_total_time_seconds("u2", START, END) == 500.0
