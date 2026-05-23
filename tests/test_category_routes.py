import pytest
from flask import Flask
from app.api.category_routes import category_bp
from app.services import category_store


@pytest.fixture(autouse=True)
def reset_store():
    category_store.clear_all()
    yield
    category_store.clear_all()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(category_bp)
    app.config["TESTING"] = True
    return app.test_client()


def test_create_category_success(client):
    r = client.post("/categories/", json={"user_id": "u1", "name": "Work"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["name"] == "Work"
    assert data["user_id"] == "u1"
    assert "category_id" in data


def test_create_category_missing_field(client):
    r = client.post("/categories/", json={"user_id": "u1"})
    assert r.status_code == 400


def test_list_categories_for_user(client):
    client.post("/categories/", json={"user_id": "u1", "name": "Work"})
    client.post("/categories/", json={"user_id": "u1", "name": "Social"})
    client.post("/categories/", json={"user_id": "u2", "name": "Other"})
    r = client.get("/categories/?user_id=u1")
    assert r.status_code == 200
    names = [c["name"] for c in r.get_json()]
    assert "Work" in names
    assert "Social" in names
    assert "Other" not in names


def test_update_category(client):
    r = client.post("/categories/", json={"user_id": "u1", "name": "Work"})
    cid = r.get_json()["category_id"]
    r2 = client.put(f"/categories/{cid}", json={"name": "Career", "color": "#00ff00"})
    assert r2.status_code == 200
    assert r2.get_json()["name"] == "Career"
    assert r2.get_json()["color"] == "#00ff00"


def test_delete_category(client):
    r = client.post("/categories/", json={"user_id": "u1", "name": "Temp"})
    cid = r.get_json()["category_id"]
    r2 = client.delete(f"/categories/{cid}")
    assert r2.status_code == 200
    r3 = client.delete(f"/categories/{cid}")
    assert r3.status_code == 404


def test_category_for_domain(client):
    r = client.post("/categories/", json={"user_id": "u1", "name": "Social", "domains": ["twitter.com"]})
    r2 = client.get("/categories/domain?user_id=u1&domain=twitter.com")
    assert r2.status_code == 200
    assert r2.get_json()["name"] == "Social"


def test_category_for_unknown_domain(client):
    r = client.get("/categories/domain?user_id=u1&domain=unknown.com")
    assert r.status_code == 200
    assert r.get_json()["category"] is None
