"""Tests for focus mode service and routes."""

import pytest
from app.api import create_app
from app.services.focus_mode import (
    start_focus,
    stop_focus,
    is_blocked,
    get_focus_status,
    clear_all_focus_sessions,
)


@pytest.fixture(autouse=True)
def reset():
    clear_all_focus_sessions()
    yield
    clear_all_focus_sessions()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# --- Service unit tests ---

def test_start_focus_blocks_domain():
    start_focus("u1", ["reddit.com"], 30)
    assert is_blocked("u1", "reddit.com") is True


def test_unblocked_domain_returns_false():
    assert is_blocked("u1", "github.com") is False


def test_stop_focus_unblocks_all():
    start_focus("u1", ["reddit.com", "twitter.com"], 60)
    count = stop_focus("u1")
    assert count == 2
    assert is_blocked("u1", "reddit.com") is False


def test_stop_focus_single_domain():
    start_focus("u1", ["reddit.com", "twitter.com"], 60)
    count = stop_focus("u1", "reddit.com")
    assert count == 1
    assert is_blocked("u1", "reddit.com") is False
    assert is_blocked("u1", "twitter.com") is True


def test_get_focus_status_shows_active():
    start_focus("u2", ["youtube.com"], 45)
    status = get_focus_status("u2")
    assert "youtube.com" in status["blocked"]


def test_start_focus_invalid_duration_raises():
    with pytest.raises(ValueError):
        start_focus("u1", ["reddit.com"], 0)


def test_start_focus_empty_domains_raises():
    with pytest.raises(ValueError):
        start_focus("u1", [], 30)


# --- Route integration tests ---

def test_route_start_focus(client):
    resp = client.post("/focus/u3/start", json={"blocked_domains": ["reddit.com"], "duration_minutes": 25})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user_id"] == "u3"
    assert "reddit.com" in data["blocked_domains"]


def test_route_start_focus_missing_field(client):
    resp = client.post("/focus/u3/start", json={"blocked_domains": ["reddit.com"]})
    assert resp.status_code == 400


def test_route_check_blocked(client):
    client.post("/focus/u4/start", json={"blocked_domains": ["news.ycombinator.com"], "duration_minutes": 10})
    resp = client.get("/focus/u4/check?domain=news.ycombinator.com")
    assert resp.status_code == 200
    assert resp.get_json()["blocked"] is True


def test_route_stop_focus(client):
    client.post("/focus/u5/start", json={"blocked_domains": ["twitter.com"], "duration_minutes": 20})
    resp = client.post("/focus/u5/stop", json={})
    assert resp.status_code == 200
    assert resp.get_json()["unblocked_count"] == 1
