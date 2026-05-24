import pytest
from datetime import datetime, timezone
from app.api import create_app
from app.models.domain_visit import DomainVisit
from app.services.visit_store import add_visit, _store


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


def make_closed_visit(user_id, domain, hour=10):
    start = datetime(2024, 6, 10, hour, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 6, 10, hour, 25, 0, tzinfo=timezone.utc)
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=end)
    add_visit(v)
    return v


def test_list_patterns_missing_user_id(client):
    r = client.get("/patterns/")
    assert r.status_code == 400


def test_list_patterns_returns_empty_for_no_visits(client):
    r = client.get("/patterns/?user_id=nobody")
    assert r.status_code == 200
    assert r.get_json() == []


def test_list_patterns_returns_patterns(client):
    make_closed_visit("u1", "alpha.com")
    make_closed_visit("u1", "beta.com")
    r = client.get("/patterns/?user_id=u1")
    assert r.status_code == 200
    data = r.get_json()
    domains = [p["domain"] for p in data]
    assert "alpha.com" in domains
    assert "beta.com" in domains


def test_domain_pattern_missing_params(client):
    r = client.get("/patterns/domain?user_id=u1")
    assert r.status_code == 400


def test_domain_pattern_not_found(client):
    r = client.get("/patterns/domain?user_id=u1&domain=ghost.com")
    assert r.status_code == 404


def test_domain_pattern_success(client):
    make_closed_visit("u1", "found.com", hour=15)
    r = client.get("/patterns/domain?user_id=u1&domain=found.com")
    assert r.status_code == 200
    data = r.get_json()
    assert data["domain"] == "found.com"
    assert data["peak_hour"] == 15
    assert data["total_visits"] == 1
