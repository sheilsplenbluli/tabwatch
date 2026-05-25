from flask import Blueprint, request, jsonify
from app.models.focus_goal import FocusGoal
import app.services.focus_goal_store as store

bp = Blueprint("focus_goals", __name__, url_prefix="/focus-goals")


@bp.get("")
def list_goals():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    active_only = request.args.get("active_only", "false").lower() == "true"
    if active_only:
        goals = store.get_active_goals_for_user(user_id)
    else:
        goals = store.get_goals_for_user(user_id)
    return jsonify([g.to_dict() for g in goals])


@bp.post("")
def create_goal():
    data = request.get_json(silent=True) or {}
    required = ("user_id", "label", "target_minutes")
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400
    try:
        goal = FocusGoal(
            user_id=data["user_id"],
            label=data["label"],
            target_minutes=int(data["target_minutes"]),
            domains=data.get("domains", []),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    store.add_goal(goal)
    return jsonify(goal.to_dict()), 201


@bp.post("/<goal_id>/complete")
def complete_goal(goal_id):
    goal = store.get_goal(goal_id)
    if not goal:
        return jsonify({"error": "not found"}), 404
    goal.complete()
    store.update_goal(goal)
    return jsonify(goal.to_dict())


@bp.delete("/<goal_id>")
def remove_goal(goal_id):
    removed = store.delete_goal(goal_id)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": goal_id})
