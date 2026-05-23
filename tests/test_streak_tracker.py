"""Tests for streak_tracker service and streak API route."""

import pytest
from datetime import date, timedelta, datetime, timezone
from app.api import create_app
from app.services.visit_store import add_visit, _store  # noqa: F401
from app.models.domain_visit import DomainVisit
from app.services.streak_tracker import (
    compute_current_streak,
    compute_longest_streak,
    get_streak_summary,
)


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id: str, day: date, domain: str = "example.com") -> DomainVisit:
    start = datetime(day.year, day.month, day.day, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)
    v = DomainVisit(visit_id=f"{user_id}-{day}", user_id=user_id, domain=domain, start_time=start)
    v.close(end)
    add_visit(v)
    return v


def test_no_visits_returns_zero_streak():
    assert compute_current_streak("u1") == 0
    assert compute_longest_streak("u1") == 0


def test_single_day_streak_is_one():
    today = date.today()
    make_closed_visit("u2", today)
    assert compute_current_streak("u2", today) == 1


def test_consecutive_days_build_streak():
    today = date.today()
    for i in range(4):
        make_closed_visit("u3", today - timedelta(days=i))
    assert compute_current_streak("u3", today) == 4


def test_gap_resets_current_streak():
    today = date.today()
    make_closed_visit("u4", today)
    make_closed_visit("u4", today - timedelta(days=2))  # gap on day-1
    assert compute_current_streak("u4", today) == 1


def test_longest_streak_across_history():
    today = date.today()
    # 3-day streak ending 10 days ago
    for i in range(3):
        make_closed_visit("u5", today - timedelta(days=10 + i))
    # 5-day streak ending 2 days ago
    for i in range(5):
        make_closed_visit("u5", today - timedelta(days=2 + i))
    assert compute_longest_streak("u5") == 5


def test_streak_counts_yesterday_if_not_today():
    today = date.today()
    yesterday = today - timedelta(days=1)
    make_closed_visit("u6", yesterday)
    # No visit today — streak should still show 1 (grace: yesterday counts)
    assert compute_current_streak("u6", today) == 1


def test_get_streak_summary_shape():
    today = date.today()
    make_closed_visit("u7", today)
    summary = get_streak_summary("u7", today)
    assert summary["user_id"] == "u7"
    assert summary["current_streak"] == 1
    assert summary["longest_streak"] == 1


def test_streak_route_returns_200(client):
    today = date.today()
    make_closed_visit("u8", today)
    resp = client.get(f"/streaks/u8?today={today.isoformat()}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["current_streak"] >= 1


def test_streak_route_invalid_date_returns_400(client):
    resp = client.get("/streaks/u9?today=not-a-date")
    assert resp.status_code == 400
