import json
import pytest
from datetime import datetime, timezone, timedelta
from app.api.routes import app, _visits
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def clear_visits():
    _visits.clear()
    yield
    _visits.clear()


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_record_visit_success(client):
    resp = client.post("/visits", json={"user_id": "u1", "domain": "example.com"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "example.com"
    assert data["user_id"] == "u1"
    assert data["end_time"] is None


def test_record_visit_missing_field(client):
    resp = client.post("/visits", json={"user_id": "u1"})
    assert resp.status_code == 400
    assert "domain" in resp.get_json()["error"]


def test_record_visit_no_body(client):
    resp = client.post("/visits", content_type="application/json", data="")
    assert resp.status_code == 400


def test_close_visit_success(client):
    client.post("/visits", json={"user_id": "u1", "domain": "news.ycombinator.com"})
    resp = client.post("/visits/u1/news.ycombinator.com/close")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["end_time"] is not None
    assert data["duration_seconds"] >= 0


def test_close_visit_not_found(client):
    resp = client.post("/visits/unknown/nope.com/close")
    assert resp.status_code == 404


def test_close_visit_already_closed(client):
    client.post("/visits", json={"user_id": "u2", "domain": "github.com"})
    client.post("/visits/u2/github.com/close")
    # Second close should 404 — no active visit left
    resp = client.post("/visits/u2/github.com/close")
    assert resp.status_code == 404


def test_digest_no_activity(client):
    resp = client.get("/digest/nobody")
    assert resp.status_code == 200
    assert "No activity" in resp.get_json()["message"]


def test_digest_with_activity(client):
    # Seed a closed visit directly into _visits
    start = datetime.now(timezone.utc) - timedelta(minutes=30)
    end = datetime.now(timezone.utc)
    visit = DomainVisit(domain="python.org", user_id="u3", start_time=start)
    visit.close(end_time=end)
    _visits["u3"] = [visit.to_dict()]

    resp = client.get("/digest/u3")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_domains"] == 1
    assert data["top_domains"][0]["domain"] == "python.org"
