from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from app.services.digest_scheduler import (
    collect_visits_for_user,
    run_weekly_digest_for_user,
    run_weekly_digests,
)


WEEK_START = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)  # Monday


def make_raw_visit(domain: str, minutes: int, offset_hours: int = 1) -> dict:
    start = WEEK_START + timedelta(hours=offset_hours)
    end = start + timedelta(minutes=minutes)
    return {
        "domain": domain,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "duration_seconds": minutes * 60,
    }


STORAGE = {
    "user1": [
        make_raw_visit("github.com", 30),
        make_raw_visit("stackoverflow.com", 15),
    ],
    "user2": [],
}


def test_collect_visits_returns_domain_visits():
    visits = collect_visits_for_user("user1", STORAGE)
    assert len(visits) == 2
    assert visits[0].domain == "github.com"


def test_collect_visits_unknown_user_returns_empty():
    visits = collect_visits_for_user("unknown", STORAGE)
    assert visits == []


@patch("app.services.digest_scheduler.send_weekly_digest_email", return_value=True)
def test_run_weekly_digest_sends_email_for_active_user(mock_send):
    ref = WEEK_START + timedelta(days=3)
    result = run_weekly_digest_for_user("user1", "user1@example.com", STORAGE, ref)
    assert result is True
    mock_send.assert_called_once()
    _, kwargs = mock_send.call_args
    # positional: recipient, digest_text, week_start
    call_args = mock_send.call_args[0]
    assert call_args[0] == "user1@example.com"


@patch("app.services.digest_scheduler.send_weekly_digest_email", return_value=True)
def test_run_weekly_digest_skips_user_with_no_activity(mock_send):
    ref = WEEK_START + timedelta(days=3)
    result = run_weekly_digest_for_user("user2", "user2@example.com", STORAGE, ref)
    assert result is False
    mock_send.assert_not_called()


@patch("app.services.digest_scheduler.send_weekly_digest_email", return_value=True)
def test_run_weekly_digests_returns_results_for_all_users(mock_send):
    registry = {"user1": "user1@example.com", "user2": "user2@example.com"}
    ref = WEEK_START + timedelta(days=3)
    results = run_weekly_digests(registry, STORAGE, ref)
    assert results["user1"] is True
    assert results["user2"] is False
    assert mock_send.call_count == 1


@patch("app.services.digest_scheduler.send_weekly_digest_email", return_value=False)
def test_run_weekly_digest_propagates_send_failure(mock_send):
    ref = WEEK_START + timedelta(days=3)
    result = run_weekly_digest_for_user("user1", "user1@example.com", STORAGE, ref)
    assert result is False
