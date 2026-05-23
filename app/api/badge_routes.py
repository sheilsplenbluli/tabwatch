from flask import Blueprint, jsonify, request
from app.services.badge_engine import (
    evaluate_badges,
    get_badges_for_user,
    get_unseen_badges,
    mark_badges_seen,
)

badge_bp = Blueprint("badges", __name__, url_prefix="/badges")


@badge_bp.get("/<user_id>")
def list_badges(user_id: str):
    """Return all badges (earned and unearned) for a user."""
    badges = get_badges_for_user(user_id)
    return jsonify([b.to_dict() for b in badges]), 200


@badge_bp.post("/<user_id>/evaluate")
def evaluate(user_id: str):
    """Trigger badge evaluation and return any newly earned badges."""
    newly_earned = evaluate_badges(user_id)
    return jsonify({
        "newly_earned": [b.to_dict() for b in newly_earned],
        "count": len(newly_earned),
    }), 200


@badge_bp.get("/<user_id>/unseen")
def unseen(user_id: str):
    """Return earned but unseen badges for a user."""
    badges = get_unseen_badges(user_id)
    return jsonify([b.to_dict() for b in badges]), 200


@badge_bp.post("/<user_id>/seen")
def mark_seen(user_id: str):
    """Mark all earned badges as seen."""
    mark_badges_seen(user_id)
    return jsonify({"status": "ok"}), 200
