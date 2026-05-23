import pytest
from app.services.domain_blocker import clear_all
from app.api import create_app


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    yield
    clear_all()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_block_domain_success(client):
    r = client.post("/blocklist/u1", json={"domain": "reddit.com", "reason": "distraction"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["domain"] == "reddit.com"
    assert data["reason"] == "distraction"


def test_block_domain_missing_field(client):
    r = client.post("/blocklist/u1", json={})
    assert r.status_code == 400


def test_list_blocked_domains(client):
    client.post("/blocklist/u1", json={"domain": "twitter.com"})
    client.post("/blocklist/u1", json={"domain": "facebook.com"})
    r = client.get("/blocklist/u1")
    assert r.status_code == 200
    domains = [e["domain"] for e in r.get_json()]
    assert "twitter.com" in domains
    assert "facebook.com" in domains


def test_list_blocked_empty_for_unknown_user(client):
    r = client.get("/blocklist/nobody")
    assert r.status_code == 200
    assert r.get_json() == []


def test_check_blocked_returns_true(client):
    client.post("/blocklist/u1", json={"domain": "tiktok.com"})
    r = client.get("/blocklist/u1/check/tiktok.com")
    assert r.status_code == 200
    assert r.get_json()["blocked"] is True


def test_check_unblocked_domain_returns_false(client):
    r = client.get("/blocklist/u1/check/github.com")
    assert r.status_code == 200
    assert r.get_json()["blocked"] is False


def test_remove_blocked_domain(client):
    client.post("/blocklist/u1", json={"domain": "news.ycombinator.com"})
    r = client.delete("/blocklist/u1/news.ycombinator.com")
    assert r.status_code == 200
    check = client.get("/blocklist/u1/check/news.ycombinator.com")
    assert check.get_json()["blocked"] is False


def test_remove_nonexistent_returns_404(client):
    r = client.delete("/blocklist/u1/notblocked.com")
    assert r.status_code == 404


def test_blocked_domains_are_user_scoped(client):
    client.post("/blocklist/u1", json={"domain": "example.com"})
    r = client.get("/blocklist/u2")
    assert r.get_json() == []
