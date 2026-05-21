"""Tests for user settings service and API routes."""

import pytest
from flask import Flask
from app.api.settings_routes import settings_bp
from app.services.user_settings import (
    UserSettings,
    _settings_store,
    save_user_settings,
)


@pytest.fixture(autouse=True)
def clear_store():
    _settings_store.clear()
    yield
    _settings_store.clear()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(settings_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# --- UserSettings unit tests ---

def test_is_eligible_defaults_true():
    s = UserSettings(user_id="u1", email="a@b.com")
    assert s.is_eligible_for_digest() is True


def test_is_eligible_false_when_unsubscribed():
    s = UserSettings(user_id="u1", email="a@b.com", unsubscribed=True)
    assert s.is_eligible_for_digest() is False


def test_is_eligible_false_when_digest_disabled():
    s = UserSettings(user_id="u1", email="a@b.com", digest_enabled=False)
    assert s.is_eligible_for_digest() is False


def test_roundtrip_to_from_dict():
    s = UserSettings(user_id="u2", email="x@y.com", digest_day="friday", digest_hour=9)
    assert UserSettings.from_dict(s.to_dict()).to_dict() == s.to_dict()


# --- API route tests ---

def test_get_settings_not_found(client):
    resp = client.get("/settings/nobody")
    assert resp.status_code == 404


def test_upsert_and_get_settings(client):
    payload = {"email": "user@example.com", "digest_day": "wednesday", "digest_hour": 7}
    resp = client.put("/settings/u42", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["email"] == "user@example.com"
    assert data["digest_day"] == "wednesday"

    get_resp = client.get("/settings/u42")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["digest_hour"] == 7


def test_upsert_missing_email(client):
    resp = client.put("/settings/u1", json={"digest_day": "monday"})
    assert resp.status_code == 400


def test_upsert_invalid_day(client):
    resp = client.put("/settings/u1", json={"email": "a@b.com", "digest_day": "funday"})
    assert resp.status_code == 400


def test_upsert_invalid_hour(client):
    resp = client.put("/settings/u1", json={"email": "a@b.com", "digest_hour": 25})
    assert resp.status_code == 400


def test_delete_settings(client):
    save_user_settings(UserSettings(user_id="u99", email="del@me.com"))
    resp = client.delete("/settings/u99")
    assert resp.status_code == 200
    assert client.get("/settings/u99").status_code == 404


def test_delete_nonexistent(client):
    resp = client.delete("/settings/ghost")
    assert resp.status_code == 404
