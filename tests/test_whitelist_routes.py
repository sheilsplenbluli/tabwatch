import pytest
from flask import Flask
from app.api.whitelist_routes import bp
from app.services import whitelist_store


@pytest.fixture(autouse=True)
def reset_store():
    whitelist_store.clear_all()
    yield
    whitelist_store.clear_all()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_add_entry_success(client):
    resp = client.post("/whitelist/u1", json={"domain": "example.com", "label": "work"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "example.com"
    assert data["label"] == "work"


def test_add_entry_missing_domain(client):
    resp = client.post("/whitelist/u1", json={})
    assert resp.status_code == 400


def test_list_entries_for_user(client):
    client.post("/whitelist/u1", json={"domain": "a.com"})
    client.post("/whitelist/u1", json={"domain": "b.com"})
    client.post("/whitelist/u2", json={"domain": "c.com"})
    resp = client.get("/whitelist/u1")
    assert resp.status_code == 200
    domains = [e["domain"] for e in resp.get_json()]
    assert "a.com" in domains
    assert "b.com" in domains
    assert "c.com" not in domains


def test_remove_entry_success(client):
    client.post("/whitelist/u1", json={"domain": "remove.me"})
    resp = client.delete("/whitelist/u1/remove.me")
    assert resp.status_code == 200
    assert not whitelist_store.is_whitelisted("u1", "remove.me")


def test_remove_entry_not_found(client):
    resp = client.delete("/whitelist/u1/ghost.com")
    assert resp.status_code == 404


def test_check_entry_whitelisted(client):
    client.post("/whitelist/u1", json={"domain": "safe.org"})
    resp = client.get("/whitelist/u1/check/safe.org")
    assert resp.status_code == 200
    assert resp.get_json()["whitelisted"] is True


def test_check_entry_not_whitelisted(client):
    resp = client.get("/whitelist/u1/check/unknown.org")
    assert resp.status_code == 200
    assert resp.get_json()["whitelisted"] is False
