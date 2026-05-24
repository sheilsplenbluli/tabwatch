import pytest
from flask import Flask
from app.api.page_title_routes import page_title_bp
from app.services.page_title_store import clear_all, upsert_title


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    yield
    clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(page_title_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_record_title_success(client):
    resp = client.post("/titles", json={
        "user_id": "u1", "domain": "example.com",
        "url": "https://example.com/page", "title": "Example Page"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Example Page"
    assert data["visit_count"] == 1


def test_record_title_missing_field(client):
    resp = client.post("/titles", json={"user_id": "u1", "domain": "example.com"})
    assert resp.status_code == 400


def test_record_title_upserts_on_revisit(client):
    for _ in range(3):
        client.post("/titles", json={
            "user_id": "u1", "domain": "example.com",
            "url": "https://example.com/page", "title": "Example Page"
        })
    resp = client.post("/titles", json={
        "user_id": "u1", "domain": "example.com",
        "url": "https://example.com/page", "title": "Updated Title"
    })
    data = resp.get_json()
    assert data["visit_count"] == 4
    assert data["title"] == "Updated Title"


def test_list_titles_for_user(client):
    upsert_title("u1", "a.com", "https://a.com", "A")
    upsert_title("u1", "b.com", "https://b.com", "B")
    upsert_title("u2", "c.com", "https://c.com", "C")
    resp = client.get("/titles?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_titles_for_domain(client):
    upsert_title("u1", "a.com", "https://a.com/1", "A1")
    upsert_title("u1", "a.com", "https://a.com/2", "A2")
    upsert_title("u1", "b.com", "https://b.com", "B")
    resp = client.get("/titles?user_id=u1&domain=a.com")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_lookup_title_found(client):
    upsert_title("u1", "a.com", "https://a.com", "A")
    resp = client.get("/titles/lookup?user_id=u1&url=https://a.com")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "A"


def test_lookup_title_not_found(client):
    resp = client.get("/titles/lookup?user_id=u1&url=https://missing.com")
    assert resp.status_code == 404


def test_delete_title_success(client):
    upsert_title("u1", "a.com", "https://a.com", "A")
    resp = client.delete("/titles/delete", json={"user_id": "u1", "url": "https://a.com"})
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] is True


def test_delete_title_not_found(client):
    resp = client.delete("/titles/delete", json={"user_id": "u1", "url": "https://ghost.com"})
    assert resp.status_code == 404
