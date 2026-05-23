import pytest
from flask import Flask
from app.api.speed_dial_routes import bp
from app.services import speed_dial_store


@pytest.fixture(autouse=True)
def reset_store():
    speed_dial_store.clear_all()
    yield
    speed_dial_store.clear_all()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_entry_success(client):
    r = client.post("/speed-dial/u1", json={"domain": "github.com", "label": "GitHub"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["domain"] == "github.com"
    assert data["label"] == "GitHub"


def test_create_entry_missing_field(client):
    r = client.post("/speed-dial/u1", json={"domain": "github.com"})
    assert r.status_code == 400


def test_list_entries_for_user(client):
    client.post("/speed-dial/u1", json={"domain": "a.com", "label": "A", "position": 1})
    client.post("/speed-dial/u1", json={"domain": "b.com", "label": "B", "position": 0})
    r = client.get("/speed-dial/u1")
    assert r.status_code == 200
    assert len(r.get_json()) == 2


def test_edit_entry_label(client):
    r = client.post("/speed-dial/u1", json={"domain": "x.com", "label": "X"})
    entry_id = r.get_json()["id"]
    r2 = client.patch(f"/speed-dial/u1/{entry_id}", json={"label": "Updated"})
    assert r2.status_code == 200
    assert r2.get_json()["label"] == "Updated"


def test_edit_entry_blank_label_returns_400(client):
    r = client.post("/speed-dial/u1", json={"domain": "x.com", "label": "X"})
    entry_id = r.get_json()["id"]
    r2 = client.patch(f"/speed-dial/u1/{entry_id}", json={"label": ""})
    assert r2.status_code == 400


def test_delete_entry(client):
    r = client.post("/speed-dial/u1", json={"domain": "y.com", "label": "Y"})
    entry_id = r.get_json()["id"]
    r2 = client.delete(f"/speed-dial/u1/{entry_id}")
    assert r2.status_code == 200
    assert speed_dial_store.entry_count() == 0


def test_touch_entry_updates_last_visited(client):
    r = client.post("/speed-dial/u1", json={"domain": "z.com", "label": "Z"})
    entry_id = r.get_json()["id"]
    r2 = client.post(f"/speed-dial/u1/{entry_id}/touch")
    assert r2.status_code == 200
    assert r2.get_json()["last_visited_at"] is not None
