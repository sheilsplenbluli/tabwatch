import pytest
from datetime import datetime, timezone, timedelta
from app.api import create_app
from app.services.visit_store import add_visit, clear_visits
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    clear_visits()
    yield
    clear_visits()


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as c:
        yield c


NOW = datetime(2024, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
START = datetime(2024, 6, 10, 0, 0, 0, tzinfo=timezone.utc)
END = datetime(2024, 6, 11, 0, 0, 0, tzinfo=timezone.utc)


def make_closed_visit(user_id, domain, start, seconds):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=start + timedelta(seconds=seconds))
    add_visit(v)
    return v


def test_leaderboard_aggregates_by_domain(client):
    make_closed_visit("u1", "github.com", NOW, 3600)
    make_closed_visit("u1", "github.com", NOW + timedelta(hours=1), 1800)
    make_closed_visit("u1", "news.ycombinator.com", NOW, 600)

    resp = client.get(f"/leaderboard/u1?start={START.isoformat()}&end={END.isoformat()}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["entries"][0]["domain"] == "github.com"
    assert data["entries"][0]["total_minutes"] == pytest.approx(90.0)
    assert data["entries"][0]["visit_count"] == 2
    assert data["entries"][1]["domain"] == "news.ycombinator.com"


def test_leaderboard_excludes_active_visits(client):
    v = DomainVisit(user_id="u1", domain="active.com", start_time=NOW)
    add_visit(v)
    make_closed_visit("u1", "closed.com", NOW, 120)

    resp = client.get(f"/leaderboard/u1?start={START.isoformat()}&end={END.isoformat()}")
    assert resp.status_code == 200
    domains = [e["domain"] for e in resp.get_json()["entries"]]
    assert "active.com" not in domains
    assert "closed.com" in domains


def test_leaderboard_excludes_visits_outside_range(client):
    outside = datetime(2024, 6, 9, 12, 0, 0, tzinfo=timezone.utc)
    make_closed_visit("u1", "old.com", outside, 7200)
    make_closed_visit("u1", "new.com", NOW, 300)

    resp = client.get(f"/leaderboard/u1?start={START.isoformat()}&end={END.isoformat()}")
    assert resp.status_code == 200
    domains = [e["domain"] for e in resp.get_json()["entries"]]
    assert "old.com" not in domains
    assert "new.com" in domains


def test_leaderboard_respects_limit(client):
    for i in range(5):
        make_closed_visit("u1", f"site{i}.com", NOW, (5 - i) * 600)

    resp = client.get(f"/leaderboard/u1?start={START.isoformat()}&end={END.isoformat()}&limit=3")
    assert resp.status_code == 200
    assert len(resp.get_json()["entries"]) == 3


def test_leaderboard_missing_params_returns_400(client):
    resp = client.get("/leaderboard/u1?start=2024-06-10T00:00:00")
    assert resp.status_code == 400


def test_leaderboard_invalid_range_returns_400(client):
    resp = client.get(f"/leaderboard/u1?start={END.isoformat()}&end={START.isoformat()}")
    assert resp.status_code == 400
