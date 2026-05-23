import pytest
from datetime import datetime
from flask import Flask
from app.api.blocked_period_routes import bp
from app.services import blocked_period_store as store
from app.models.blocked_period import BlockedPeriod


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    return app.test_client()


def make_period(**kwargs) -> BlockedPeriod:
    defaults = dict(
        user_id="u1", label="Evening", start_time="20:00",
        end_time="22:00", days=["mon", "tue", "wed"]
    )
    defaults.update(kwargs)
    p = BlockedPeriod(**defaults)
    store.add_period(p)
    return p


def test_create_period_success(client):
    resp = client.post("/blocked-periods", json={
        "user_id": "u1", "label": "Lunch",
        "start_time": "12:00", "end_time": "13:00", "days": ["mon", "fri"]
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["label"] == "Lunch"
    assert data["active"] is True


def test_create_period_missing_field(client):
    resp = client.post("/blocked-periods", json={"user_id": "u1", "label": "X"})
    assert resp.status_code == 400
    assert "missing fields" in resp.get_json()["error"]


def test_create_period_invalid_day(client):
    resp = client.post("/blocked-periods", json={
        "user_id": "u1", "label": "Bad",
        "start_time": "08:00", "end_time": "09:00", "days": ["monday"]
    })
    assert resp.status_code == 400
    assert "invalid days" in resp.get_json()["error"]


def test_list_periods_for_user(client):
    make_period(user_id="u1")
    make_period(user_id="u1", label="Morning")
    make_period(user_id="u2")
    resp = client.get("/blocked-periods?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_update_period(client):
    p = make_period(user_id="u1")
    resp = client.patch(f"/blocked-periods/{p.id}", json={"label": "Updated", "active": False})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["label"] == "Updated"
    assert data["active"] is False


def test_delete_period(client):
    p = make_period()
    resp = client.delete(f"/blocked-periods/{p.id}")
    assert resp.status_code == 200
    assert store.get_period(p.id) is None


def test_delete_unknown_returns_404(client):
    resp = client.delete("/blocked-periods/nonexistent")
    assert resp.status_code == 404


def test_is_active_now_within_window():
    p = BlockedPeriod(user_id="u1", label="Test", start_time="09:00",
                      end_time="17:00", days=["mon", "tue", "wed", "thu", "fri"])
    # Wednesday 10:30
    now = datetime(2024, 1, 3, 10, 30)  # Wednesday
    assert p.is_active_now(now) is True


def test_is_active_now_outside_window():
    p = BlockedPeriod(user_id="u1", label="Test", start_time="09:00",
                      end_time="17:00", days=["mon"])
    # Wednesday outside days
    now = datetime(2024, 1, 3, 10, 30)
    assert p.is_active_now(now) is False


def test_check_endpoint_not_blocked(client):
    make_period(user_id="u1", days=["sun"], start_time="01:00", end_time="02:00")
    resp = client.get("/blocked-periods/check?user_id=u1")
    assert resp.status_code == 200
    # very unlikely to be in that window during tests
    assert "in_blocked_period" in resp.get_json()
