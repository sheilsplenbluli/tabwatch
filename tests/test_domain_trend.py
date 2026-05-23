"""Tests for domain trend computation and route."""
import pytest
from datetime import datetime, timedelta, timezone

from app.api import create_app
from app.services.visit_store import add_visit, _store
from app.services.domain_trend import compute_trend
from app.models.domain_visit import DomainVisit


NOW = datetime(2024, 6, 10, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(user_id, domain, start: datetime, minutes: float) -> DomainVisit:
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    end = start + timedelta(minutes=minutes)
    v.close(end)
    add_visit(v)
    return v


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_trend_up_when_more_recent_activity():
    # previous window: 10 min, current window: 30 min  => up
    make_closed_visit("u1", "example.com", NOW - timedelta(days=10), 10)
    make_closed_visit("u1", "example.com", NOW - timedelta(days=3), 30)

    trend = compute_trend("u1", "example.com", period_days=7, reference_dt=NOW)
    assert trend.direction == "up"
    assert trend.current_period_minutes == 30.0
    assert trend.previous_period_minutes == 10.0
    assert trend.delta_minutes == 20.0
    assert trend.percent_change == 200.0


def test_trend_down_when_less_recent_activity():
    make_closed_visit("u1", "example.com", NOW - timedelta(days=10), 40)
    make_closed_visit("u1", "example.com", NOW - timedelta(days=3), 10)

    trend = compute_trend("u1", "example.com", period_days=7, reference_dt=NOW)
    assert trend.direction == "down"
    assert trend.delta_minutes == -30.0


def test_trend_flat_when_equal():
    make_closed_visit("u1", "example.com", NOW - timedelta(days=10), 15)
    make_closed_visit("u1", "example.com", NOW - timedelta(days=3), 15)

    trend = compute_trend("u1", "example.com", period_days=7, reference_dt=NOW)
    assert trend.direction == "flat"
    assert trend.percent_change == 0.0


def test_percent_change_none_when_no_previous_data():
    make_closed_visit("u1", "example.com", NOW - timedelta(days=3), 20)

    trend = compute_trend("u1", "example.com", period_days=7, reference_dt=NOW)
    assert trend.percent_change is None
    assert trend.direction == "up"


def test_active_visits_excluded():
    # active visit (no end_time) should not count
    v = DomainVisit(user_id="u1", domain="example.com", start_time=NOW - timedelta(days=2))
    add_visit(v)

    trend = compute_trend("u1", "example.com", period_days=7, reference_dt=NOW)
    assert trend.current_period_minutes == 0.0


def test_other_domains_excluded():
    make_closed_visit("u1", "other.com", NOW - timedelta(days=3), 60)

    trend = compute_trend("u1", "example.com", period_days=7, reference_dt=NOW)
    assert trend.current_period_minutes == 0.0


def test_route_returns_200(client):
    make_closed_visit("u1", "example.com", NOW - timedelta(days=3), 10)
    resp = client.get("/trends/u1/example.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "direction" in data
    assert "current_period_minutes" in data


def test_route_invalid_period_days_returns_400(client):
    resp = client.get("/trends/u1/example.com?period_days=abc")
    assert resp.status_code == 400
