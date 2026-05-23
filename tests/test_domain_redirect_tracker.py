import pytest
from flask import Flask
from app.api.redirect_routes import redirect_bp
import app.services.domain_redirect_tracker as tracker


@pytest.fixture(autouse=True)
def reset_store():
    tracker.clear_all()
    yield
    tracker.clear_all()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(redirect_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


TS = "2024-06-01T10:00:00"


def test_record_redirect_creates_entry():
    rec = tracker.record_redirect("u1", "google.com", "maps.google.com", TS)
    assert rec.count == 1
    assert rec.from_domain == "google.com"
    assert rec.to_domain == "maps.google.com"
    assert rec.last_seen == TS


def test_record_redirect_increments_existing():
    tracker.record_redirect("u1", "google.com", "maps.google.com", TS)
    rec = tracker.record_redirect("u1", "google.com", "maps.google.com", "2024-06-01T11:00:00")
    assert rec.count == 2
    assert rec.last_seen == "2024-06-01T11:00:00"


def test_different_pairs_create_separate_records():
    tracker.record_redirect("u1", "a.com", "b.com", TS)
    tracker.record_redirect("u1", "a.com", "c.com", TS)
    records = tracker.get_redirects_for_user("u1")
    assert len(records) == 2


def test_get_redirects_filters_by_user():
    tracker.record_redirect("u1", "a.com", "b.com", TS)
    tracker.record_redirect("u2", "x.com", "y.com", TS)
    assert len(tracker.get_redirects_for_user("u1")) == 1
    assert len(tracker.get_redirects_for_user("u2")) == 1


def test_get_redirect_unknown_returns_none():
    assert tracker.get_redirect("nonexistent") is None


def test_delete_redirect_removes_entry():
    rec = tracker.record_redirect("u1", "a.com", "b.com", TS)
    assert tracker.delete_redirect(rec.redirect_id) is True
    assert tracker.get_redirect(rec.redirect_id) is None


def test_delete_unknown_returns_false():
    assert tracker.delete_redirect("ghost") is False


def test_api_track_redirect_success(client):
    resp = client.post("/redirects/", json={
        "user_id": "u1", "from_domain": "a.com",
        "to_domain": "b.com", "timestamp": TS
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["count"] == 1
    assert data["from_domain"] == "a.com"


def test_api_track_redirect_missing_field(client):
    resp = client.post("/redirects/", json={"user_id": "u1"})
    assert resp.status_code == 400


def test_api_list_redirects(client):
    client.post("/redirects/", json={"user_id": "u1", "from_domain": "a.com", "to_domain": "b.com", "timestamp": TS})
    resp = client.get("/redirects/?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_api_list_redirects_missing_user(client):
    resp = client.get("/redirects/")
    assert resp.status_code == 400


def test_api_delete_redirect(client):
    post = client.post("/redirects/", json={
        "user_id": "u1", "from_domain": "a.com",
        "to_domain": "b.com", "timestamp": TS
    })
    rid = post.get_json()["redirect_id"]
    resp = client.delete(f"/redirects/{rid}")
    assert resp.status_code == 200
    assert client.get(f"/redirects/{rid}").status_code == 404
