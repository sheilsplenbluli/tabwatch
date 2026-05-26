import pytest
from flask import Flask
from app.api.domain_flag_routes import bp
import app.services.domain_flag_store as flag_store
from app.models.domain_flag import DomainFlag


@pytest.fixture(autouse=True)
def reset_store():
    flag_store.clear_all()
    yield
    flag_store.clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    return app.test_client()


def make_flag(**kwargs) -> DomainFlag:
    defaults = {"user_id": "u1", "domain": "twitter.com", "reason": "too distracting"}
    defaults.update(kwargs)
    return DomainFlag(**defaults)


def test_create_flag_success(client):
    resp = client.post("/flags", json={"user_id": "u1", "domain": "reddit.com", "reason": "waste of time"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "reddit.com"
    assert data["resolved"] is False
    assert data["flag_id"]


def test_create_flag_missing_field(client):
    resp = client.post("/flags", json={"user_id": "u1", "domain": "reddit.com"})
    assert resp.status_code == 400


def test_create_flag_blank_reason(client):
    resp = client.post("/flags", json={"user_id": "u1", "domain": "reddit.com", "reason": "  "})
    assert resp.status_code == 400


def test_list_flags_for_user(client):
    flag_store.add_flag(make_flag(domain="a.com"))
    flag_store.add_flag(make_flag(domain="b.com"))
    resp = client.get("/flags?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_flags_for_domain(client):
    flag_store.add_flag(make_flag(domain="a.com"))
    flag_store.add_flag(make_flag(domain="b.com"))
    resp = client.get("/flags?user_id=u1&domain=a.com")
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["domain"] == "a.com"


def test_list_flags_missing_user_id(client):
    resp = client.get("/flags")
    assert resp.status_code == 400


def test_resolve_flag(client):
    flag = make_flag()
    flag_store.add_flag(flag)
    resp = client.post(f"/flags/{flag.flag_id}/resolve", json={"notes": "handled"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["resolved"] is True
    assert data["notes"] == "handled"
    assert data["resolved_at"] is not None


def test_resolve_unknown_flag(client):
    resp = client.post("/flags/nonexistent/resolve")
    assert resp.status_code == 404


def test_delete_flag(client):
    flag = make_flag()
    flag_store.add_flag(flag)
    resp = client.delete(f"/flags/{flag.flag_id}")
    assert resp.status_code == 204
    assert flag_store.get_flag(flag.flag_id) is None


def test_delete_unknown_flag(client):
    resp = client.delete("/flags/ghost")
    assert resp.status_code == 404


def test_domain_flag_model_resolve_is_idempotent():
    flag = make_flag()
    flag.resolve(notes="first")
    first_resolved_at = flag.resolved_at
    flag.resolve(notes="second")
    assert flag.notes == "first"
    assert flag.resolved_at == first_resolved_at
