from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from app.services.leaderboard_builder import build_leaderboard

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@leaderboard_bp.get("/<user_id>")
def get_leaderboard(user_id: str):
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return jsonify({"error": "'start' and 'end' query params are required"}), 400

    try:
        start = _parse_dt(start_str)
        end = _parse_dt(end_str)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": f"invalid datetime: {exc}"}), 400

    if end <= start:
        return jsonify({"error": "'end' must be after 'start'"}), 400

    try:
        limit = int(request.args.get("limit", 10))
        if limit < 1 or limit > 100:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "'limit' must be an integer between 1 and 100"}), 400

    entries = build_leaderboard(user_id, start, end, limit=limit)
    return jsonify({
        "user_id": user_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "entries": [e.to_dict() for e in entries],
    }), 200
