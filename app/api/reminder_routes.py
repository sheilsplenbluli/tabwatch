from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models.reminder import Reminder
from app.services import reminder_store

reminder_bp = Blueprint("reminders", __name__, url_prefix="/reminders")


@reminder_bp.get("/<user_id>")
def list_reminders(user_id: str):
    reminders = reminder_store.get_reminders_for_user(user_id)
    return jsonify([r.to_dict() for r in reminders]), 200


@reminder_bp.post("/")
def create_reminder():
    body = request.get_json(silent=True) or {}
    required = ("user_id", "domain", "message", "remind_at")
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400

    try:
        remind_at = datetime.fromisoformat(body["remind_at"])
    except ValueError:
        return jsonify({"error": "invalid remind_at format, use ISO 8601"}), 400

    reminder = Reminder(
        user_id=body["user_id"],
        domain=body["domain"],
        message=body["message"],
        remind_at=remind_at,
    )
    reminder_store.add_reminder(reminder)
    return jsonify(reminder.to_dict()), 201


@reminder_bp.delete("/<reminder_id>")
def remove_reminder(reminder_id: str):
    deleted = reminder_store.delete_reminder(reminder_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": reminder_id}), 200


@reminder_bp.get("/domain/<user_id>/<domain>")
def reminders_for_domain(user_id: str, domain: str):
    reminders = reminder_store.get_reminders_for_domain(user_id, domain)
    return jsonify([r.to_dict() for r in reminders]), 200
