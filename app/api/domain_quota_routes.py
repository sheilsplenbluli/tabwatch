"""API routes for domain visit quotas."""
from flask import Blueprint, jsonify, request

from app.services.domain_quota import (
    check_quota,
    delete_quota,
    get_quotas_for_user,
    set_quota,
)

bp = Blueprint("domain_quota", __name__, url_prefix="/quota")


@bp.get("/<user_id>")
def list_quotas(user_id: str):
    quotas = get_quotas_for_user(user_id)
    return jsonify({"user_id": user_id, "quotas": quotas}), 200


@bp.put("/<user_id>/<domain>")
def upsert_quota(user_id: str, domain: str):
    body = request.get_json(silent=True) or {}
    if "daily_limit" not in body:
        return jsonify({"error": "daily_limit is required"}), 400
    try:
        limit = int(body["daily_limit"])
        set_quota(user_id, domain, limit)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"user_id": user_id, "domain": domain, "daily_limit": limit}), 200


@bp.delete("/<user_id>/<domain>")
def remove_quota(user_id: str, domain: str):
    removed = delete_quota(user_id, domain)
    if not removed:
        return jsonify({"error": "quota not found"}), 404
    return jsonify({"deleted": True}), 200


@bp.get("/<user_id>/<domain>/check")
def check(user_id: str, domain: str):
    status = check_quota(user_id, domain)
    if status is None:
        return jsonify({"error": "no quota set for this domain"}), 404
    return jsonify(status.to_dict()), 200
