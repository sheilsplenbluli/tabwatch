import pytest
from flask import Flask
from app.api.reading_list_routes import reading_list_bp
import app.services.reading_list_store as store
from app.models.reading_list import ReadingListEntry


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(reading_list_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_entry(user_id="u1", domain="example.com", title="Test") -> ReadingListEntry:
    e = ReadingListEntry(user_id=user_id, url=f"https://{domain}/page", domain=domain, title=title)
    store.add_entry(e)
    return e


def test_create_entry_success(client):
    resp = client.post("/reading-list/", json={
        "user_id": "u1", "url": "https://news.com/article",
        "domain": "news.com", "title": "Big News"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "news.com"
    assert data["read_at"] is None
    assert store.entry_count() == 1


def test_create_entry_missing_field(client):
    resp = client.post("/reading-list/", json={"user_id": "u1", "url": "https://x.com"})
    assert resp.status_code == 400


def test_list_entries_for_user(client):
    make_entry(user_id="u1")
    make_entry(user_id="u1")
    make_entry(user_id="u2")
    resp = client.get("/reading-list/u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_entries_excludes_archived_by_default(client):
    e = make_entry(user_id="u1")
    e.archive()
    store.update_entry(e)
    resp = client.get("/reading-list/u1")
    assert len(resp.get_json()) == 0


def test_list_entries_includes_archived_when_requested(client):
    e = make_entry(user_id="u1")
    e.archive()
    store.update_entry(e)
    resp = client.get("/reading-list/u1?archived=true")
    assert len(resp.get_json()) == 1


def test_mark_read_sets_read_at(client):
    e = make_entry()
    resp = client.post(f"/reading-list/{e.entry_id}/read")
    assert resp.status_code == 200
    assert resp.get_json()["read_at"] is not None


def test_mark_read_unknown_returns_404(client):
    resp = client.post("/reading-list/nonexistent/read")
    assert resp.status_code == 404


def test_archive_entry(client):
    e = make_entry()
    resp = client.post(f"/reading-list/{e.entry_id}/archive")
    assert resp.status_code == 200
    assert resp.get_json()["archived"] is True


def test_delete_entry(client):
    e = make_entry()
    resp = client.delete(f"/reading-list/{e.entry_id}")
    assert resp.status_code == 200
    assert store.get_entry(e.entry_id) is None


def test_delete_unknown_returns_404(client):
    resp = client.delete("/reading-list/ghost-id")
    assert resp.status_code == 404
