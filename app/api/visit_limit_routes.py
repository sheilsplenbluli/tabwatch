from flask import Blueprint, request, jsonify
from app.models.visit_limit import VisitLimit
from app.services.visit_limit_store import (
    set_limit, get_limit, get_limits_for_user, delete_limit
)
from app.services.visit_limit_checker import check_limit_for_domain, check_all_limits_for_user

bp = Blueprint("visit_limits", __name__, url_prefix="/visit-limits")


@bp.get("/<user_id>")
def list_limits(user_id: str):
    return jsonify([l.to_dict() for l in get_limits_for_user(user_id)])


@bp.put("/<user_id>/<domain>")
def upsert_limit(user_id: str, domain: str):
    body = request.get_json(silent=True) or {}
    if "max_visits_per_day" not in body:
        return jsonify({"error": "max_visits_per_day is required"}), 400
    try:
        existing = get_limit(user_id, domain)
        if existing:
            existing.max_visits_per_day = int(body["max_visits_per_day"])
            existing.enabled = body.get("enabled", existing.enabled)
            result = set_limit(existing)
        else:
            limit = VisitLimit(
                user_id=user_id,
                domain=domain,
                max_visits_per_day=int(body["max_visits_per_day"]),
                enabled=body.get("enabled", True),
            )
            result = set_limit(limit)
        return jsonify(result.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.delete("/<user_id>/<domain>")
def remove_limit(user_id: str, domain: str):
    deleted = delete_limit(user_id, domain)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": True}), 200


@bp.get("/<user_id>/check/all")
def check_all(user_id: str):
    return jsonify(check_all_limits_for_user(user_id))


@bp.get("/<user_id>/check/<domain>")
def check_one(user_id: str, domain: str):
    return jsonify(check_limit_for_domain(user_id, domain))
