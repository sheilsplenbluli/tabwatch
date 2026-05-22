import pytest
from app.api import create_app
from app.services.bookmark_store import clear_all


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    yield
    clear_all()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_bookmark_success(client):
    resp = client.post("/bookmarks/", json={
        "user_id": "u1", "domain": "example.com",
        "url": "https://example.com", "title": "Example"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "example.com"
    assert data["pinned"] is False


def test_create_bookmark_missing_field(client):
    resp = client.post("/bookmarks/", json={"user_id": "u1", "domain": "x.com"})
    assert resp.status_code == 400
    assert "missing fields" in resp.get_json()["error"]


def test_list_bookmarks_for_user(client):
    client.post("/bookmarks/", json={"user_id": "u1", "domain": "a.com", "url": "https://a.com", "title": "A"})
    client.post("/bookmarks/", json={"user_id": "u1", "domain": "b.com", "url": "https://b.com", "title": "B"})
    client.post("/bookmarks/", json={"user_id": "u2", "domain": "c.com", "url": "https://c.com", "title": "C"})
    resp = client.get("/bookmarks/?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_bookmarks_by_domain(client):
    client.post("/bookmarks/", json={"user_id": "u1", "domain": "a.com", "url": "https://a.com", "title": "A"})
    client.post("/bookmarks/", json={"user_id": "u1", "domain": "b.com", "url": "https://b.com", "title": "B"})
    resp = client.get("/bookmarks/?user_id=u1&domain=a.com")
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1 and results[0]["domain"] == "a.com"


def test_edit_bookmark_title(client):
    r = client.post("/bookmarks/", json={"user_id": "u1", "domain": "x.com", "url": "https://x.com", "title": "Old"})
    bid = r.get_json()["bookmark_id"]
    resp = client.patch(f"/bookmarks/{bid}", json={"title": "New Title"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "New Title"


def test_toggle_pin(client):
    r = client.post("/bookmarks/", json={"user_id": "u1", "domain": "x.com", "url": "https://x.com", "title": "X"})
    bid = r.get_json()["bookmark_id"]
    resp = client.post(f"/bookmarks/{bid}/pin")
    assert resp.status_code == 200
    assert resp.get_json()["pinned"] is True


def test_delete_bookmark(client):
    r = client.post("/bookmarks/", json={"user_id": "u1", "domain": "x.com", "url": "https://x.com", "title": "X"})
    bid = r.get_json()["bookmark_id"]
    resp = client.delete(f"/bookmarks/{bid}")
    assert resp.status_code == 200
    assert client.delete(f"/bookmarks/{bid}").status_code == 404
