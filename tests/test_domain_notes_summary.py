"""Tests for domain notes summary feature."""

import pytest
from datetime import datetime, timedelta

from app.api import create_app
from app.services import visit_store, note_store
from app.models.domain_visit import DomainVisit
from app.models.note import Note
from app.services.domain_notes_summary import build_domain_notes_summary


@pytest.fixture(autouse=True)
def reset_stores():
    visit_store._store.clear()
    note_store._store.clear()
    yield
    visit_store._store.clear()
    note_store._store.clear()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, minutes=10):
    now = datetime.utcnow()
    v = DomainVisit(visit_id="v-" + domain + str(minutes), user_id=user_id, domain=domain, start_time=now - timedelta(minutes=minutes))
    v.close(end_time=now)
    visit_store.add_visit(v)
    return v


def make_note(user_id, domain, body="test note"):
    n = Note(note_id="n-" + domain, user_id=user_id, domain=domain, body=body)
    note_store.add_note(n)
    return n


def test_build_summary_returns_correct_totals():
    make_closed_visit("u1", "example.com", minutes=20)
    make_note("u1", "example.com", body="interesting site")

    summary = build_domain_notes_summary("u1", "example.com")
    assert summary is not None
    assert summary.domain == "example.com"
    assert summary.total_visits == 1
    assert summary.total_minutes > 0
    assert summary.note_count == 1
    assert summary.notes[0]["body"] == "interesting site"


def test_build_summary_no_visits_returns_none():
    result = build_domain_notes_summary("u1", "ghost.com")
    assert result is None


def test_build_summary_no_notes_still_works():
    make_closed_visit("u2", "nonotes.com", minutes=5)
    summary = build_domain_notes_summary("u2", "nonotes.com")
    assert summary is not None
    assert summary.note_count == 0
    assert summary.notes == []


def test_build_summary_first_and_last_visited_set():
    make_closed_visit("u3", "sorted.com", minutes=30)
    make_closed_visit("u3", "sorted.com", minutes=5)
    summary = build_domain_notes_summary("u3", "sorted.com")
    assert summary.first_visited is not None
    assert summary.last_visited is not None
    assert summary.first_visited <= summary.last_visited


def test_route_returns_200(client):
    make_closed_visit("u4", "route.com", minutes=10)
    resp = client.get("/domain-notes-summary?user_id=u4&domain=route.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["domain"] == "route.com"


def test_route_missing_params_returns_400(client):
    resp = client.get("/domain-notes-summary?user_id=u5")
    assert resp.status_code == 400


def test_route_unknown_domain_returns_404(client):
    resp = client.get("/domain-notes-summary?user_id=u6&domain=nope.com")
    assert resp.status_code == 404
