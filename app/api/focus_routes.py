"""API routes for focus mode."""

from flask import Blueprint, request, jsonify
from app.services.focus_mode import (
    start_focus,
    stop_focus,
    is_blocked,
    get_focus_status,
)

focus_bp = Blueprint("focus", __name__, url_prefix="/focus")


@focus_bp.route("/<user_id>/start", methods=["POST"])
def start(user_id: str):
    body = request.get_json(silent=True) or {}
    domains = body.get("blocked_domains")
    duration = body.get("duration_minutes")

    if not domains or not isinstance(domains, list):
        return jsonify({"error": "blocked_domains must be a non-empty list"}), 400
    if duration is None:
        return jsonify({"error": "duration_minutes is required"}), 400

    try:
        result = start_focus(user_id, domains, int(duration))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result), 201


@focus_bp.route("/<user_id>/stop", methods=["POST"])
def stop(user_id: str):
    body = request.get_json(silent=True) or {}
    domain = body.get("domain")  # optional
    count = stop_focus(user_id, domain)
    return jsonify({"unblocked_count": count}), 200


@focus_bp.route("/<user_id>/status", methods=["GET"])
def status(user_id: str):
    return jsonify(get_focus_status(user_id)), 200


@focus_bp.route("/<user_id>/check", methods=["GET"])
def check(user_id: str):
    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "domain query param required"}), 400
    blocked = is_blocked(user_id, domain)
    return jsonify({"domain": domain, "blocked": blocked}), 200
