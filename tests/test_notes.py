import pytest
from flask import Flask

from app.api.note_routes import note_bp
from app.services.note_store import clear_all_notes, add_note, note_count
from app.models.note import Note


@pytest.fixture(autouse=True)
def reset_store():
    clear_all_notes()
    yield
    clear_all_notes()


@pytest.fixture()
def client():
    app = Flask(__name__)
    app.register_blueprint(note_bp)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_note(user_id="u1", domain="example.com", body="great site") -> Note:
    n = Note(user_id=user_id, domain=domain, body=body)
    return add_note(n)


def test_create_note_success(client):
    resp = client.post("/notes/", json={"user_id": "u1", "domain": "news.com", "body": "my note"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["body"] == "my note"
    assert data["domain"] == "news.com"
    assert data["note_id"] != ""


def test_create_note_missing_field(client):
    resp = client.post("/notes/", json={"user_id": "u1", "domain": "news.com"})
    assert resp.status_code == 400


def test_list_notes_for_user(client):
    make_note(user_id="u1", domain="a.com")
    make_note(user_id="u1", domain="b.com")
    make_note(user_id="u2", domain="a.com")
    resp = client.get("/notes/u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_list_notes_filtered_by_domain(client):
    make_note(user_id="u1", domain="a.com")
    make_note(user_id="u1", domain="b.com")
    resp = client.get("/notes/u1?domain=a.com")
    assert resp.status_code == 200
    notes = resp.get_json()
    assert len(notes) == 1
    assert notes[0]["domain"] == "a.com"


def test_edit_note_updates_body(client):
    note = make_note(body="old body")
    resp = client.put(f"/notes/{note.note_id}", json={"body": "new body"})
    assert resp.status_code == 200
    assert resp.get_json()["body"] == "new body"


def test_edit_note_not_found(client):
    resp = client.put("/notes/nonexistent", json={"body": "x"})
    assert resp.status_code == 404


def test_delete_note_success(client):
    note = make_note()
    resp = client.delete(f"/notes/{note.note_id}")
    assert resp.status_code == 200
    assert note_count() == 0


def test_delete_note_not_found(client):
    resp = client.delete("/notes/ghost")
    assert resp.status_code == 404


def test_note_roundtrip_dict():
    n = Note(user_id="u1", domain="foo.io", body="hello")
    d = n.to_dict()
    restored = Note.from_dict(d)
    assert restored.user_id == n.user_id
    assert restored.domain == n.domain
    assert restored.body == n.body
