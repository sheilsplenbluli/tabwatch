"""API routes for user activity streaks."""

from datetime import date
from flask import Blueprint, jsonify, request
from app.services.streak_tracker import get_streak_summary

streak_bp = Blueprint("streaks", __name__, url_prefix="/streaks")


@streak_bp.route("/<user_id>", methods=["GET"])
def streak(user_id: str):
    """GET /streaks/<user_id> — return current and longest streak.

    Optional query param: ?today=YYYY-MM-DD to override today's date (useful for testing).
    """
    today_param = request.args.get("today")
    today = None
    if today_param:
        try:
            today = date.fromisoformat(today_param)
        except ValueError:
            return jsonify({"error": "invalid date format, expected YYYY-MM-DD"}), 400

    summary = get_streak_summary(user_id, today=today)
    return jsonify(summary), 200
