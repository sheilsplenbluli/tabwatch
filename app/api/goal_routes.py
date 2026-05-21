from flask import Blueprint, request, jsonify
from app.services.goal_tracker import (
    set_goal,
    get_goals_for_user,
    get_goal,
    delete_goal,
    check_goal_progress,
)

goal_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goal_bp.get("/<user_id>")
def list_goals(user_id: str):
    return jsonify(get_goals_for_user(user_id)), 200


@goal_bp.put("/<user_id>/<domain>")
def upsert_goal(user_id: str, domain: str):
    body = request.get_json(silent=True) or {}
    limit = body.get("daily_limit_minutes")
    if limit is None:
        return jsonify({"error": "daily_limit_minutes is required"}), 400
    if not isinstance(limit, int) or limit <= 0:
        return jsonify({"error": "daily_limit_minutes must be a positive integer"}), 400
    goal = set_goal(user_id, domain, limit)
    return jsonify(goal), 200


@goal_bp.delete("/<user_id>/<domain>")
def remove_goal(user_id: str, domain: str):
    removed = delete_goal(user_id, domain)
    if not removed:
        return jsonify({"error": "goal not found"}), 404
    return jsonify({"deleted": True}), 200


@goal_bp.get("/<user_id>/<domain>/progress")
def progress(user_id: str, domain: str):
    result = check_goal_progress(user_id, domain)
    if result is None:
        return jsonify({"error": "no goal set for this domain"}), 404
    return jsonify(result), 200
