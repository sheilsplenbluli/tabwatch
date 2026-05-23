import pytest
from app.api import create_app
from app.services.visit_store import add_visit, clear_visits
from app.services.tag_store import create_tag, clear_tags
from app.models.domain_visit import DomainVisit
from datetime import datetime, timedelta


def make_closed_visit(user_id, domain, minutes=10):
    start = datetime.utcnow() - timedelta(minutes=minutes + 1)
    end = start + timedelta(minutes=minutes)
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=end)
    add_visit(v)
    return v


@pytest.fixture(autouse=True)
def reset_store():
    clear_visits()
    clear_tags()
    yield
    clear_visits()
    clear_tags()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_search_returns_matching_domains(client):
    make_closed_visit("u1", "github.com", minutes=15)
    make_closed_visit("u1", "gitlab.com", minutes=5)
    make_closed_visit("u1", "google.com", minutes=20)

    resp = client.get("/search/domains?user_id=u1&q=git")
    assert resp.status_code == 200
    data = resp.get_json()
    domains = [r["domain"] for r in data["results"]]
    assert "github.com" in domains
    assert "gitlab.com" in domains
    assert "google.com" not in domains


def test_search_empty_query_returns_all(client):
    make_closed_visit("u1", "github.com")
    make_closed_visit("u1", "reddit.com")

    resp = client.get("/search/domains?user_id=u1&q=")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 2


def test_search_min_minutes_filter(client):
    make_closed_visit("u1", "github.com", minutes=30)
    make_closed_visit("u1", "reddit.com", minutes=2)

    resp = client.get("/search/domains?user_id=u1&q=&min_minutes=10")
    assert resp.status_code == 200
    data = resp.get_json()
    domains = [r["domain"] for r in data["results"]]
    assert "github.com" in domains
    assert "reddit.com" not in domains


def test_search_missing_user_id_returns_400(client):
    resp = client.get("/search/domains?q=github")
    assert resp.status_code == 400


def test_search_invalid_limit_returns_400(client):
    resp = client.get("/search/domains?user_id=u1&q=&limit=abc")
    assert resp.status_code == 400


def test_search_results_sorted_by_minutes_desc(client):
    make_closed_visit("u1", "slow.com", minutes=5)
    make_closed_visit("u1", "fast.com", minutes=50)
    make_closed_visit("u1", "mid.com", minutes=20)

    resp = client.get("/search/domains?user_id=u1&q=")
    assert resp.status_code == 200
    data = resp.get_json()
    minutes = [r["total_minutes"] for r in data["results"]]
    assert minutes == sorted(minutes, reverse=True)


def test_search_unknown_user_returns_empty(client):
    resp = client.get("/search/domains?user_id=nobody&q=")
    assert resp.status_code == 200
    assert resp.get_json()["count"] == 0
