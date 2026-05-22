"""Tests for app/services/session_summarizer.py"""

from datetime import datetime, timedelta

import pytest

from app.models.domain_visit import DomainVisit
from app.services.session_summarizer import (
    build_sessions,
    longest_session,
    SESSION_GAP_MINUTES,
)


def make_visit(domain: str, start: datetime, duration_seconds: float) -> DomainVisit:
    end = start + timedelta(seconds=duration_seconds)
    v = DomainVisit(visit_id="v1", user_id="u1", domain=domain, start_time=start)
    v.close(end_time=end)
    return v


BASE = datetime(2024, 3, 11, 9, 0, 0)


def test_empty_visits_returns_no_sessions():
    assert build_sessions("u1", []) == []


def test_active_visits_are_excluded():
    active = DomainVisit(visit_id="v1", user_id="u1", domain="example.com", start_time=BASE)
    sessions = build_sessions("u1", [active])
    assert sessions == []


def test_single_visit_creates_one_session():
    v = make_visit("example.com", BASE, 300)
    sessions = build_sessions("u1", [v])
    assert len(sessions) == 1
    s = sessions[0]
    assert s.domains == ["example.com"]
    assert abs(s.total_minutes - 5.0) < 0.01


def test_visits_within_gap_merged_into_one_session():
    v1 = make_visit("a.com", BASE, 600)
    v2 = make_visit("b.com", BASE + timedelta(minutes=10), 300)
    sessions = build_sessions("u1", [v1, v2])
    assert len(sessions) == 1
    assert set(sessions[0].domains) == {"a.com", "b.com"}


def test_visits_beyond_gap_create_separate_sessions():
    v1 = make_visit("a.com", BASE, 60)
    v2 = make_visit("b.com", BASE + timedelta(minutes=SESSION_GAP_MINUTES + 5), 60)
    sessions = build_sessions("u1", [v1, v2])
    assert len(sessions) == 2
    assert sessions[0].domains == ["a.com"]
    assert sessions[1].domains == ["b.com"]


def test_duplicate_domain_in_session_not_repeated():
    v1 = make_visit("a.com", BASE, 120)
    v2 = make_visit("a.com", BASE + timedelta(minutes=2), 120)
    sessions = build_sessions("u1", [v1, v2])
    assert len(sessions) == 1
    assert sessions[0].domains.count("a.com") == 1


def test_session_end_time_is_latest_visit_end():
    v1 = make_visit("a.com", BASE, 60)
    v2 = make_visit("b.com", BASE + timedelta(minutes=5), 300)
    sessions = build_sessions("u1", [v1, v2])
    expected_end = BASE + timedelta(minutes=5) + timedelta(seconds=300)
    assert sessions[0].end_time == expected_end


def test_longest_session_returns_correct_one():
    v1 = make_visit("a.com", BASE, 60)
    v2 = make_visit("b.com", BASE + timedelta(hours=2), 3600)
    sessions = build_sessions("u1", [v1, v2])
    best = longest_session(sessions)
    assert best is not None
    assert "b.com" in best.domains


def test_longest_session_empty_returns_none():
    assert longest_session([]) is None


def test_to_dict_contains_expected_keys():
    v = make_visit("x.com", BASE, 120)
    sessions = build_sessions("u1", [v])
    d = sessions[0].to_dict()
    assert {"user_id", "start_time", "end_time", "domains", "total_minutes"} <= d.keys()
    assert d["user_id"] == "u1"
