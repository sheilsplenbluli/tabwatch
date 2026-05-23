"""API routes for productivity scoring."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.services.productivity_scorer import compute_productivity_score

productivity_bp = Blueprint("productivity", __name__, url_prefix="/productivity")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


@productivity_bp.get("/<user_id>/score")
def get_score(user_id: str):
    """Return a productivity score for the given user and optional time range."""
    start_raw = request.args.get("start")
    end_raw = request.args.get("end")

    now = datetime.now(tz=timezone.utc)

    # Default: last 7 days
    start = _parse_dt(start_raw) or datetime(
        now.year, now.month, now.day, tzinfo=timezone.utc
    ).replace(day=now.day - 6) if now.day > 6 else datetime(
        now.year, now.month, 1, tzinfo=timezone.utc
    )
    end = _parse_dt(end_raw) or now

    if start >= end:
        return jsonify({"error": "start must be before end"}), 400

    score = compute_productivity_score(user_id, start, end)
    return jsonify(score.to_dict()), 200
