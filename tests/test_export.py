import json
import pytest
from datetime import datetime, timezone, timedelta
from flask import Flask

from app.api.export_routes import export_bp
from app.services import visit_store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    visit_store._store.clear()
    visit_store._counter = 0
    yield
    visit_store._store.clear()
    visit_store._counter = 0


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(export_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, start, duration=120):
    end = start + timedelta(seconds=duration)
    v = DomainVisit(visit_id="v1", user_id=user_id, domain=domain, start_time=start)
    v.end_time = end
    v.duration_seconds = float(duration)
    visit_store.add_visit(v)
    return v


BASE = datetime(2024, 6, 3, 10, 0, 0, tzinfo=timezone.utc)


def test_export_json_returns_records(client):
    make_closed_visit("u1", "example.com", BASE)
    resp = client.get("/export/u1/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user_id"] == "u1"
    assert data["record_count"] == 1
    assert data["records"][0]["domain"] == "example.com"


def test_export_json_excludes_active_visits(client):
    v = DomainVisit(visit_id="v2", user_id="u2", domain="open.io", start_time=BASE)
    visit_store.add_visit(v)
    resp = client.get("/export/u2/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["record_count"] == 0


def test_export_json_since_filter(client):
    make_closed_visit("u3", "old.com", BASE - timedelta(days=5))
    make_closed_visit("u3", "new.com", BASE)
    since = (BASE - timedelta(days=1)).isoformat()
    resp = client.get(f"/export/u3/json?since={since}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["record_count"] == 1
    assert data["records"][0]["domain"] == "new.com"


def test_export_csv_content_type(client):
    make_closed_visit("u4", "site.net", BASE)
    resp = client.get("/export/u4/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.content_type
    text = resp.data.decode()
    assert "site.net" in text
    assert "user_id,domain" in text


def test_export_bad_since_returns_400(client):
    resp = client.get("/export/u5/json?since=not-a-date")
    assert resp.status_code == 400


def test_export_empty_user_returns_empty_bundle(client):
    resp = client.get("/export/nobody/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["record_count"] == 0
    assert data["records"] == []
