import pytest
from app.api import create_app
from app.services import tab_snapshot_store as store


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_snapshot_success(client):
    resp = client.post("/snapshots", json={
        "user_id": "u1",
        "domains": ["github.com", "news.ycombinator.com"],
        "label": "work tabs",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user_id"] == "u1"
    assert data["tab_count"] == 2
    assert data["label"] == "work tabs"
    assert data["is_restored"] is False


def test_create_snapshot_missing_field(client):
    resp = client.post("/snapshots", json={"user_id": "u1"})
    assert resp.status_code == 400


def test_create_snapshot_domains_not_list(client):
    resp = client.post("/snapshots", json={"user_id": "u1", "domains": "bad"})
    assert resp.status_code == 400


def test_list_snapshots_for_user(client):
    client.post("/snapshots", json={"user_id": "u1", "domains": ["a.com"]})
    client.post("/snapshots", json={"user_id": "u1", "domains": ["b.com"]})
    client.post("/snapshots", json={"user_id": "u2", "domains": ["c.com"]})
    resp = client.get("/snapshots?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_snapshots_missing_user_id(client):
    resp = client.get("/snapshots")
    assert resp.status_code == 400


def test_get_snapshot_by_id(client):
    r = client.post("/snapshots", json={"user_id": "u1", "domains": ["x.com"]})
    snap_id = r.get_json()["snapshot_id"]
    resp = client.get(f"/snapshots/{snap_id}")
    assert resp.status_code == 200
    assert resp.get_json()["snapshot_id"] == snap_id


def test_get_snapshot_unknown_returns_404(client):
    resp = client.get("/snapshots/doesnotexist")
    assert resp.status_code == 404


def test_restore_snapshot(client):
    r = client.post("/snapshots", json={"user_id": "u1", "domains": ["y.com"]})
    snap_id = r.get_json()["snapshot_id"]
    resp = client.post(f"/snapshots/{snap_id}/restore")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["is_restored"] is True
    assert data["restored_at"] is not None


def test_delete_snapshot(client):
    r = client.post("/snapshots", json={"user_id": "u1", "domains": ["z.com"]})
    snap_id = r.get_json()["snapshot_id"]
    resp = client.delete(f"/snapshots/{snap_id}")
    assert resp.status_code == 200
    assert store.snapshot_count() == 0


def test_delete_snapshot_unknown_returns_404(client):
    resp = client.delete("/snapshots/ghost")
    assert resp.status_code == 404
