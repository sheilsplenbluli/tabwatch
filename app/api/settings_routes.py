"""API routes for managing user digest settings."""

from flask import Blueprint, request, jsonify
from app.services.user_settings import (
    UserSettings,
    get_user_settings,
    save_user_settings,
    delete_user_settings,
)

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

VALID_DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


@settings_bp.route("/<user_id>", methods=["GET"])
def get_settings(user_id: str):
    settings = get_user_settings(user_id)
    if settings is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify(settings.to_dict()), 200


@settings_bp.route("/<user_id>", methods=["PUT"])
def upsert_settings(user_id: str):
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "request body required"}), 400

    email = body.get("email")
    if not email:
        return jsonify({"error": "email is required"}), 400

    digest_day = body.get("digest_day", "monday")
    if digest_day not in VALID_DAYS:
        return jsonify({"error": f"digest_day must be one of {sorted(VALID_DAYS)}"}), 400

    digest_hour = body.get("digest_hour", 8)
    if not isinstance(digest_hour, int) or not (0 <= digest_hour <= 23):
        return jsonify({"error": "digest_hour must be an integer 0-23"}), 400

    settings = UserSettings(
        user_id=user_id,
        email=email,
        digest_enabled=body.get("digest_enabled", True),
        digest_day=digest_day,
        digest_hour=digest_hour,
        top_domains_limit=body.get("top_domains_limit", 10),
        timezone=body.get("timezone", "UTC"),
        unsubscribed=body.get("unsubscribed", False),
    )
    save_user_settings(settings)
    return jsonify(settings.to_dict()), 200


@settings_bp.route("/<user_id>", methods=["DELETE"])
def remove_settings(user_id: str):
    removed = delete_user_settings(user_id)
    if not removed:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"deleted": user_id}), 200
