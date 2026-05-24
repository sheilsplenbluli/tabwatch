from flask import Blueprint, request, jsonify
from app.services.domain_decay import compute_decay_scores, get_decay_score_for_domain

domain_decay_bp = Blueprint("domain_decay", __name__, url_prefix="/decay")


@domain_decay_bp.route("", methods=["GET"])
def list_decay_scores():
    """GET /decay?user_id=<id>&limit=<n>"""
    user_id = request.args.get("user_id", "")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    limit = request.args.get("limit", type=int)
    scores = compute_decay_scores(user_id)
    if limit and limit > 0:
        scores = scores[:limit]

    return jsonify([s.to_dict() for s in scores]), 200


@domain_decay_bp.route("/<path:domain>", methods=["GET"])
def single_domain_score(domain: str):
    """GET /decay/<domain>?user_id=<id>"""
    user_id = request.args.get("user_id", "")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    result = get_decay_score_for_domain(user_id, domain)
    if result is None:
        return jsonify({"error": "domain not found"}), 404

    return jsonify(result.to_dict()), 200
