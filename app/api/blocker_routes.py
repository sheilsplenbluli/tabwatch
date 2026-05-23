from flask import Blueprint, jsonify, request
from app.services.domain_blocker import (
    block_domain,
    unblock_domain,
    is_blocked,
    get_blocked_domains,
)

blocker_bp = Blueprint("blocker", __name__, url_prefix="/blocklist")


@blocker_bp.get("/<user_id>")
def list_blocked(user_id: str):
    entries = get_blocked_domains(user_id)
    return jsonify([e.to_dict() for e in entries]), 200


@blocker_bp.post("/<user_id>")
def add_blocked(user_id: str):
    body = request.get_json(silent=True) or {}
    domain = body.get("domain")
    if not domain:
        return jsonify({"error": "domain is required"}), 400
    reason = body.get("reason")
    entry = block_domain(user_id, domain, reason)
    return jsonify(entry.to_dict()), 201


@blocker_bp.delete("/<user_id>/<domain>")
def remove_blocked(user_id: str, domain: str):
    removed = unblock_domain(user_id, domain)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"removed": domain}), 200


@blocker_bp.get("/<user_id>/check/<domain>")
def check_blocked(user_id: str, domain: str):
    blocked = is_blocked(user_id, domain)
    return jsonify({"user_id": user_id, "domain": domain, "blocked": blocked}), 200
