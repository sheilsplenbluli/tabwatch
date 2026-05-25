import pytest
from flask import Flask
from app.api.domain_mood_routes import bp
from app.services import domain_mood_store as store
from app.models.domain_mood import DomainMood


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_mood(**kwargs) -> DomainMood:
    defaults = {"user_id": "u1", "domain": "example.com", "mood": "good"}
    defaults.update(kwargs)
    return DomainMood(**defaults)


def test_create_mood_success(client):
    resp = client.post("/moods", json={"user_id": "u1", "domain": "example.com", "mood": "great"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["mood"] == "great"
    assert data["domain"] == "example.com"


def test_create_mood_missing_field(client):
    resp = client.post("/moods", json={"user_id": "u1", "domain": "example.com"})
    assert resp.status_code == 400


def test_create_mood_invalid_mood(client):
    resp = client.post("/moods", json={"user_id": "u1", "domain": "x.com", "mood": "meh"})
    assert resp.status_code == 400
    assert "mood" in resp.get_json()["error"]


def test_list_moods_for_user(client):
    store.add_mood(make_mood(user_id="u1", domain="a.com"))
    store.add_mood(make_mood(user_id="u1", domain="b.com"))
    store.add_mood(make_mood(user_id="u2", domain="c.com"))
    resp = client.get("/moods?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_moods_for_domain(client):
    store.add_mood(make_mood(user_id="u1", domain="a.com"))
    store.add_mood(make_mood(user_id="u1", domain="b.com"))
    resp = client.get("/moods?user_id=u1&domain=a.com")
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["domain"] == "a.com"


def test_edit_mood_updates_fields(client):
    m = make_mood(mood="good", note=None)
    store.add_mood(m)
    resp = client.patch(f"/moods/{m.mood_id}", json={"mood": "terrible", "note": "ugh"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["mood"] == "terrible"
    assert data["note"] == "ugh"


def test_edit_mood_invalid_mood_returns_400(client):
    m = make_mood()
    store.add_mood(m)
    resp = client.patch(f"/moods/{m.mood_id}", json={"mood": "awesome"})
    assert resp.status_code == 400


def test_delete_mood_success(client):
    m = make_mood()
    store.add_mood(m)
    resp = client.delete(f"/moods/{m.mood_id}")
    assert resp.status_code == 200
    assert store.get_mood(m.mood_id) is None


def test_delete_mood_unknown_returns_404(client):
    resp = client.delete("/moods/nonexistent")
    assert resp.status_code == 404


def test_domain_mood_invalid_on_init():
    with pytest.raises(ValueError):
        DomainMood(user_id="u1", domain="x.com", mood="vibes")
