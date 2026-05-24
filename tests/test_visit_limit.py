import pytest
from datetime import datetime, timezone
from app.models.visit_limit import VisitLimit
from app.services.visit_limit_store import set_limit, get_limit, get_limits_for_user, delete_limit, clear_all
from app.services.visit_store import add_visit, clear_visits
from app.models.domain_visit import DomainVisit
from app.api import create_app


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    clear_visits()
    yield
    clear_all()
    clear_visits()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, start, duration_seconds=300):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(start)
    v.duration_seconds = duration_seconds
    add_visit(v)
    return v


def test_visit_limit_defaults():
    limit = VisitLimit(user_id="u1", domain="example.com", max_visits_per_day=5)
    assert limit.enabled is True
    assert limit.max_visits_per_day == 5


def test_visit_limit_invalid_max_raises():
    with pytest.raises(ValueError):
        VisitLimit(user_id="u1", domain="example.com", max_visits_per_day=0)


def test_is_exceeded_when_at_limit():
    limit = VisitLimit(user_id="u1", domain="example.com", max_visits_per_day=3)
    assert limit.is_exceeded(3) is True
    assert limit.is_exceeded(2) is False


def test_is_exceeded_disabled_always_false():
    limit = VisitLimit(user_id="u1", domain="example.com", max_visits_per_day=1, enabled=False)
    assert limit.is_exceeded(10) is False


def test_percent_used_calculation():
    limit = VisitLimit(user_id="u1", domain="example.com", max_visits_per_day=10)
    assert limit.percent_used(5) == 50.0
    assert limit.percent_used(0) == 0.0


def test_set_and_get_limit():
    limit = VisitLimit(user_id="u1", domain="news.com", max_visits_per_day=4)
    set_limit(limit)
    result = get_limit("u1", "news.com")
    assert result is not None
    assert result.max_visits_per_day == 4


def test_get_limits_for_user_returns_only_that_user():
    set_limit(VisitLimit(user_id="u1", domain="a.com", max_visits_per_day=2))
    set_limit(VisitLimit(user_id="u2", domain="b.com", max_visits_per_day=3))
    results = get_limits_for_user("u1")
    assert len(results) == 1
    assert results[0].domain == "a.com"


def test_delete_limit_removes_entry():
    set_limit(VisitLimit(user_id="u1", domain="x.com", max_visits_per_day=5))
    deleted = delete_limit("u1", "x.com")
    assert deleted is True
    assert get_limit("u1", "x.com") is None


def test_upsert_limit_route_creates(client):
    resp = client.put("/visit-limits/u1/reddit.com", json={"max_visits_per_day": 10})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["max_visits_per_day"] == 10
    assert data["domain"] == "reddit.com"


def test_upsert_limit_route_missing_field(client):
    resp = client.put("/visit-limits/u1/reddit.com", json={})
    assert resp.status_code == 400


def test_check_one_route_not_exceeded(client):
    client.put("/visit-limits/u1/reddit.com", json={"max_visits_per_day": 5})
    resp = client.get("/visit-limits/u1/check/reddit.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["exceeded"] is False


def test_delete_limit_route_not_found(client):
    resp = client.delete("/visit-limits/u1/unknown.com")
    assert resp.status_code == 404
