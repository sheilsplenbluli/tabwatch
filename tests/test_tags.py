import pytest
from app.api import create_app
from app.services.tag_store import clear_all_tags


@pytest.fixture(autouse=True)
def reset_store():
    clear_all_tags()
    yield
    clear_all_tags()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_tag_success(client):
    resp = client.post("/tags/user1", json={"name": "Work", "domains": ["github.com"], "color": "#ff0000"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Work"
    assert "github.com" in data["domains"]
    assert data["color"] == "#ff0000"


def test_create_tag_missing_name(client):
    resp = client.post("/tags/user1", json={"domains": ["example.com"]})
    assert resp.status_code == 400


def test_list_tags_for_user(client):
    client.post("/tags/user1", json={"name": "Work"})
    client.post("/tags/user1", json={"name": "Social"})
    client.post("/tags/user2", json={"name": "Other"})
    resp = client.get("/tags/user1")
    assert resp.status_code == 200
    names = [t["name"] for t in resp.get_json()]
    assert "Work" in names
    assert "Social" in names
    assert "Other" not in names


def test_update_tag(client):
    create_resp = client.post("/tags/user1", json={"name": "Draft"})
    tag_id = create_resp.get_json()["tag_id"]
    resp = client.patch(f"/tags/{tag_id}", json={"name": "Final", "color": "#00ff00"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Final"
    assert data["color"] == "#00ff00"


def test_update_unknown_tag(client):
    resp = client.patch("/tags/nonexistent", json={"name": "X"})
    assert resp.status_code == 404


def test_delete_tag(client):
    create_resp = client.post("/tags/user1", json={"name": "Temp"})
    tag_id = create_resp.get_json()["tag_id"]
    resp = client.delete(f"/tags/{tag_id}")
    assert resp.status_code == 204
    list_resp = client.get("/tags/user1")
    assert all(t["tag_id"] != tag_id for t in list_resp.get_json())


def test_delete_unknown_tag(client):
    resp = client.delete("/tags/ghost")
    assert resp.status_code == 404


def test_tags_for_domain(client):
    client.post("/tags/user1", json={"name": "Dev", "domains": ["github.com", "stackoverflow.com"]})
    client.post("/tags/user1", json={"name": "Social", "domains": ["twitter.com"]})
    resp = client.get("/tags/user1/domain/github.com")
    assert resp.status_code == 200
    names = [t["name"] for t in resp.get_json()]
    assert "Dev" in names
    assert "Social" not in names
