from flask import Blueprint, request, jsonify
from app.models.blocked_period import BlockedPeriod
from app.services import blocked_period_store as store

bp = Blueprint("blocked_periods", __name__, url_prefix="/blocked-periods")

REQUIRED = {"user_id", "label", "start_time", "end_time", "days"}
VALID_DAYS = BlockedPeriod.VALID_DAYS


@bp.get("")
def list_periods():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    periods = store.get_periods_for_user(user_id)
    return jsonify([p.to_dict() for p in periods]), 200


@bp.post("")
def create_period():
    data = request.get_json(silent=True) or {}
    missing = REQUIRED - data.keys()
    if missing:
        return jsonify({"error": f"missing fields: {sorted(missing)}"}), 400
    invalid_days = set(data["days"]) - VALID_DAYS
    if invalid_days:
        return jsonify({"error": f"invalid days: {sorted(invalid_days)}"}), 400
    period = BlockedPeriod(
        user_id=data["user_id"],
        label=data["label"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        days=data["days"],
    )
    store.add_period(period)
    return jsonify(period.to_dict()), 201


@bp.patch("/<period_id>")
def update_period(period_id: str):
    data = request.get_json(silent=True) or {}
    updated = store.update_period(period_id, data)
    if updated is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated.to_dict()), 200


@bp.delete("/<period_id>")
def delete_period(period_id: str):
    if not store.delete_period(period_id):
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": period_id}), 200


@bp.get("/check")
def check_period():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    blocked = store.is_in_blocked_period(user_id)
    return jsonify({"user_id": user_id, "in_blocked_period": blocked}), 200
