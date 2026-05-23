import pytest
from flask import Flask
from app.api.annotation_routes import bp
from app.services import annotation_store


@pytest.fixture(autouse=True)
def reset_store():
    annotation_store.clear_all()
    yield
    annotation_store.clear_all()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    return app.test_client()


def test_create_annotation_success(client):
    resp = client.post("/annotations/", json={
        "user_id": "u1",
        "domain": "example.com",
        "body": "great resource",
        "label": "research",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "example.com"
    assert data["label"] == "research"


def test_create_annotation_missing_field(client):
    resp = client.post("/annotations/", json={"user_id": "u1", "domain": "x.com"})
    assert resp.status_code == 400


def test_list_annotations_for_user(client):
    client.post("/annotations/", json={"user_id": "u1", "domain": "a.com", "body": "note1"})
    client.post("/annotations/", json={"user_id": "u1", "domain": "b.com", "body": "note2"})
    client.post("/annotations/", json={"user_id": "u2", "domain": "a.com", "body": "other"})
    resp = client.get("/annotations/?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_annotations_filtered_by_domain(client):
    client.post("/annotations/", json={"user_id": "u1", "domain": "a.com", "body": "note1"})
    client.post("/annotations/", json={"user_id": "u1", "domain": "b.com", "body": "note2"})
    resp = client.get("/annotations/?user_id=u1&domain=a.com")
    assert resp.status_code == 200
    items = resp.get_json()
    assert len(items) == 1
    assert items[0]["domain"] == "a.com"


def test_edit_annotation(client):
    r = client.post("/annotations/", json={"user_id": "u1", "domain": "x.com", "body": "old"})
    ann_id = r.get_json()["id"]
    resp = client.patch(f"/annotations/{ann_id}", json={"body": "new body", "label": "productive"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["body"] == "new body"
    assert data["label"] == "productive"
    assert data["updated_at"] is not None


def test_delete_annotation(client):
    r = client.post("/annotations/", json={"user_id": "u1", "domain": "x.com", "body": "bye"})
    ann_id = r.get_json()["id"]
    resp = client.delete(f"/annotations/{ann_id}")
    assert resp.status_code == 200
    assert annotation_store.get_annotation(ann_id) is None


def test_delete_unknown_annotation_returns_404(client):
    resp = client.delete("/annotations/nonexistent")
    assert resp.status_code == 404
