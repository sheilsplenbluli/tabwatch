from flask import Blueprint, jsonify, request
from app.services.visit_pattern_builder import build_visit_pattern, get_all_patterns_for_user

bp = Blueprint("visit_pattern", __name__, url_prefix="/patterns")


@bp.get("/")
def list_patterns():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    patterns = get_all_patterns_for_user(user_id)
    return jsonify([p.to_dict() for p in patterns]), 200


@bp.get("/domain")
def domain_pattern():
    user_id = request.args.get("user_id")
    domain = request.args.get("domain")
    if not user_id or not domain:
        return jsonify({"error": "user_id and domain required"}), 400
    pattern = build_visit_pattern(user_id, domain)
    if pattern is None:
        return jsonify({"error": "no data for domain"}), 404
    return jsonify(pattern.to_dict()), 200
