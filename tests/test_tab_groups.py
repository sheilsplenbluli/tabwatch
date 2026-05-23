import pytest
from flask import Flask
from app.api.tab_group_routes import tab_group_bp
from app.services import tab_group_store


@pytest.fixture(autouse=True)
def reset_store():
    tab_group_store.clear_all()
    yield
    tab_group_store.clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(tab_group_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_group_success(client):
    resp = client.post("/tab-groups", json={"user_id": "u1", "name": "Work", "domains": ["github.com"]})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Work"
    assert "github.com" in data["domains"]
    assert "group_id" in data


def test_create_group_missing_field(client):
    resp = client.post("/tab-groups", json={"user_id": "u1"})
    assert resp.status_code == 400


def test_list_groups_for_user(client):
    client.post("/tab-groups", json={"user_id": "u1", "name": "Work"})
    client.post("/tab-groups", json={"user_id": "u1", "name": "Social"})
    client.post("/tab-groups", json={"user_id": "u2", "name": "Other"})
    resp = client.get("/tab-groups?user_id=u1")
    assert resp.status_code == 200
    groups = resp.get_json()
    assert len(groups) == 2


def test_update_group_name(client):
    resp = client.post("/tab-groups", json={"user_id": "u1", "name": "Old"})
    gid = resp.get_json()["group_id"]
    resp2 = client.put(f"/tab-groups/{gid}", json={"name": "New"})
    assert resp2.status_code == 200
    assert resp2.get_json()["name"] == "New"


def test_update_group_blank_name_returns_400(client):
    resp = client.post("/tab-groups", json={"user_id": "u1", "name": "Work"})
    gid = resp.get_json()["group_id"]
    resp2 = client.put(f"/tab-groups/{gid}", json={"name": "   "})
    assert resp2.status_code == 400


def test_delete_group(client):
    resp = client.post("/tab-groups", json={"user_id": "u1", "name": "Temp"})
    gid = resp.get_json()["group_id"]
    del_resp = client.delete(f"/tab-groups/{gid}")
    assert del_resp.status_code == 200
    assert del_resp.get_json()["deleted"] == gid


def test_delete_unknown_group_returns_404(client):
    resp = client.delete("/tab-groups/nonexistent")
    assert resp.status_code == 404


def test_group_for_domain_found(client):
    client.post("/tab-groups", json={"user_id": "u1", "name": "Dev", "domains": ["stackoverflow.com"]})
    resp = client.get("/tab-groups/domain?user_id=u1&domain=stackoverflow.com")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Dev"


def test_group_for_domain_not_found_returns_null(client):
    resp = client.get("/tab-groups/domain?user_id=u1&domain=unknown.com")
    assert resp.status_code == 200
    assert resp.get_json()["group"] is None
