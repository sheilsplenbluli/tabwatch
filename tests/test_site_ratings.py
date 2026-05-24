import pytest
from app.api import create_app
import app.services.site_rating_store as store
from app.models.site_rating import SiteRating


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_rating_success(client):
    resp = client.post("/ratings/user1", json={"domain": "example.com", "rating": 4})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "example.com"
    assert data["rating"] == 4


def test_create_rating_missing_field(client):
    resp = client.post("/ratings/user1", json={"domain": "example.com"})
    assert resp.status_code == 400


def test_create_rating_invalid_value(client):
    resp = client.post("/ratings/user1", json={"domain": "example.com", "rating": 99})
    assert resp.status_code == 400


def test_create_rating_upserts_existing(client):
    client.post("/ratings/user1", json={"domain": "example.com", "rating": 3})
    resp = client.post("/ratings/user1", json={"domain": "example.com", "rating": 5})
    assert resp.status_code == 200
    assert resp.get_json()["rating"] == 5
    assert store.rating_count() == 1


def test_list_ratings_for_user(client):
    client.post("/ratings/user1", json={"domain": "a.com", "rating": 2})
    client.post("/ratings/user1", json={"domain": "b.com", "rating": 5})
    client.post("/ratings/user2", json={"domain": "c.com", "rating": 1})
    resp = client.get("/ratings/user1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_for_domain_found(client):
    client.post("/ratings/user1", json={"domain": "example.com", "rating": 3})
    resp = client.get("/ratings/user1/domain/example.com")
    assert resp.status_code == 200
    assert resp.get_json()["domain"] == "example.com"


def test_get_for_domain_not_found(client):
    resp = client.get("/ratings/user1/domain/unknown.com")
    assert resp.status_code == 404


def test_delete_rating(client):
    resp = client.post("/ratings/user1", json={"domain": "example.com", "rating": 4})
    rid = resp.get_json()["id"]
    del_resp = client.delete(f"/ratings/user1/{rid}")
    assert del_resp.status_code == 200
    assert store.rating_count() == 0


def test_delete_wrong_user_returns_404(client):
    resp = client.post("/ratings/user1", json={"domain": "example.com", "rating": 4})
    rid = resp.get_json()["id"]
    del_resp = client.delete(f"/ratings/user2/{rid}")
    assert del_resp.status_code == 404


def test_site_rating_invalid_score_raises():
    with pytest.raises(ValueError):
        SiteRating(user_id="u", domain="x.com", rating=0)
