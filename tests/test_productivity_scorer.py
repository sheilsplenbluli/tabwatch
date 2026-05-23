"""Tests for the productivity scorer service and route."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from app.api import create_app
from app.services.productivity_scorer import (
    DISTRACTING_DOMAINS,
    PRODUCTIVE_DOMAINS,
    ProductivityScore,
    compute_productivity_score,
)
from app.services.visit_store import add_visit, _store  # type: ignore[attr-defined]
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(
    user_id: str,
    domain: str,
    start: datetime,
    duration_seconds: float,
) -> DomainVisit:
    visit = DomainVisit(
        visit_id=f"{user_id}-{domain}-{start.isoformat()}",
        user_id=user_id,
        domain=domain,
        start_time=start,
    )
    visit.end_time = start + timedelta(seconds=duration_seconds)
    visit.duration_seconds = duration_seconds
    add_visit(visit)
    return visit


NOW = datetime(2024, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
START = NOW - timedelta(hours=2)
END = NOW + timedelta(minutes=1)


def test_score_all_productive():
    make_closed_visit("u1", "github.com", START, 3600)
    result = compute_productivity_score("u1", START, END)
    assert result.productive_minutes == pytest.approx(60.0)
    assert result.distracting_minutes == 0.0
    assert result.score == pytest.approx(100.0)


def test_score_all_distracting():
    make_closed_visit("u1", "reddit.com", START, 1800)
    result = compute_productivity_score("u1", START, END)
    assert result.distracting_minutes == pytest.approx(30.0)
    assert result.score == pytest.approx(0.0)


def test_score_neutral_counts_half():
    make_closed_visit("u1", "example.com", START, 3600)
    result = compute_productivity_score("u1", START, END)
    assert result.neutral_minutes == pytest.approx(60.0)
    assert result.score == pytest.approx(50.0)


def test_no_visits_returns_default_score():
    result = compute_productivity_score("u_nobody", START, END)
    assert result.score == pytest.approx(50.0)
    assert result.productive_minutes == 0.0


def test_active_visits_excluded():
    visit = DomainVisit(
        visit_id="active-1",
        user_id="u2",
        domain="github.com",
        start_time=START,
    )
    add_visit(visit)  # no end_time → active
    result = compute_productivity_score("u2", START, END)
    assert result.productive_minutes == 0.0


def test_to_dict_contains_expected_keys():
    ps = ProductivityScore(
        user_id="u3",
        productive_minutes=30.0,
        distracting_minutes=10.0,
        neutral_minutes=20.0,
        score=75.0,
    )
    d = ps.to_dict()
    assert set(d.keys()) == {
        "user_id",
        "productive_minutes",
        "distracting_minutes",
        "neutral_minutes",
        "score",
    }


def test_route_returns_200(client):
    make_closed_visit("u4", "github.com", START, 600)
    resp = client.get(
        f"/productivity/u4/score",
        query_string={"start": START.isoformat(), "end": END.isoformat()},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "score" in data
    assert data["user_id"] == "u4"


def test_route_invalid_range_returns_400(client):
    resp = client.get(
        "/productivity/u5/score",
        query_string={"start": END.isoformat(), "end": START.isoformat()},
    )
    assert resp.status_code == 400
