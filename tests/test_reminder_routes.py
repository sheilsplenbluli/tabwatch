import pytest
from datetime import datetime, timedelta
from flask import Flask
from app.api.reminder_routes import reminder_bp
from app.services import reminder_store


@pytest.fixture(autouse=True)
def reset_store():
    reminder_store.clear_all()
    yield
    reminder_store.clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(reminder_bp)
    app.config["TESTING"] = True
    return app.test_client()


def future_iso():
    return (datetime.utcnow() + timedelta(hours=1)).isoformat()


def test_create_reminder_success(client):
    resp = client.post("/reminders/", json={
        "user_id": "u1",
        "domain": "reddit.com",
        "message": "Stop scrolling!",
        "remind_at": future_iso(),
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "reddit.com"
    assert data["triggered"] is False


def test_create_reminder_missing_field(client):
    resp = client.post("/reminders/", json={"user_id": "u1", "domain": "x.com"})
    assert resp.status_code == 400
    assert "missing" in resp.get_json()["error"]


def test_create_reminder_bad_date(client):
    resp = client.post("/reminders/", json={
        "user_id": "u1",
        "domain": "x.com",
        "message": "hey",
        "remind_at": "not-a-date",
    })
    assert resp.status_code == 400


def test_list_reminders_for_user(client):
    client.post("/reminders/", json={
        "user_id": "u2", "domain": "news.ycombinator.com",
        "message": "limit reached", "remind_at": future_iso(),
    })
    resp = client.get("/reminders/u2")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_delete_reminder(client):
    r = client.post("/reminders/", json={
        "user_id": "u1", "domain": "fb.com",
        "message": "bye", "remind_at": future_iso(),
    }).get_json()
    resp = client.delete(f"/reminders/{r['id']}")
    assert resp.status_code == 200
    assert reminder_store.reminder_count() == 0


def test_delete_unknown_reminder_returns_404(client):
    resp = client.delete("/reminders/nonexistent")
    assert resp.status_code == 404


def test_reminders_for_domain(client):
    client.post("/reminders/", json={
        "user_id": "u3", "domain": "twitter.com",
        "message": "take a break", "remind_at": future_iso(),
    })
    resp = client.get("/reminders/domain/u3/twitter.com")
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["domain"] == "twitter.com"
