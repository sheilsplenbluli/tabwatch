import pytest
from datetime import datetime, timedelta, timezone
from app.api import create_app
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, start, duration_seconds=600):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.end_time = start + timedelta(seconds=duration_seconds)
    v.duration_seconds = duration_seconds
    add_visit(v)
    return v


def test_daily_heatmap_aggregates_by_date(client):
    now = datetime.now(timezone.utc)
    make_closed_visit("u1", "example.com", now - timedelta(days=1), 1800)
    make_closed_visit("u1", "example.com", now - timedelta(days=1), 600)
    resp = client.get("/heatmap/u1/daily")
    assert resp.status_code == 200
    data = resp.get_json()["daily"]
    day_key = (now - timedelta(days=1)).date().isoformat()
    assert day_key in data
    assert abs(data[day_key] - 40.0) < 0.01  # (1800+600)/60 = 40 minutes


def test_daily_heatmap_excludes_active_visits(client):
    now = datetime.now(timezone.utc)
    v = DomainVisit(user_id="u1", domain="open.com", start_time=now - timedelta(hours=1))
    add_visit(v)  # no end_time -> active
    resp = client.get("/heatmap/u1/daily")
    assert resp.status_code == 200
    assert resp.get_json()["daily"] == {}


def test_daily_heatmap_filters_by_domain(client):
    now = datetime.now(timezone.utc)
    make_closed_visit("u1", "a.com", now - timedelta(days=2), 3600)
    make_closed_visit("u1", "b.com", now - timedelta(days=2), 1800)
    resp = client.get("/heatmap/u1/daily?domain=a.com")
    data = resp.get_json()["daily"]
    assert all(v == 60.0 for v in data.values())


def test_hourly_heatmap_groups_by_hour(client):
    base = datetime(2024, 1, 10, 14, 0, 0, tzinfo=timezone.utc)
    make_closed_visit("u1", "x.com", base, 1200)
    make_closed_visit("u1", "x.com", base + timedelta(minutes=10), 600)
    resp = client.get("/heatmap/u1/hourly")
    assert resp.status_code == 200
    data = resp.get_json()["hourly"]
    assert "14" in data or 14 in data
    hour_val = data.get("14") or data.get(14)
    assert abs(hour_val - 30.0) < 0.01  # (1200+600)/60


def test_summary_includes_peak_fields(client):
    now = datetime.now(timezone.utc)
    make_closed_visit("u1", "z.com", now - timedelta(days=3), 7200)
    resp = client.get("/heatmap/u1")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "daily" in body
    assert "hourly" in body
    assert "peak_day" in body
    assert "peak_hour" in body


def test_invalid_days_param_returns_400(client):
    resp = client.get("/heatmap/u1/daily?days=0")
    assert resp.status_code == 400
    resp2 = client.get("/heatmap/u1/daily?days=400")
    assert resp2.status_code == 400


def test_unknown_user_returns_empty_heatmap(client):
    resp = client.get("/heatmap/ghost/daily")
    assert resp.status_code == 200
    assert resp.get_json()["daily"] == {}
