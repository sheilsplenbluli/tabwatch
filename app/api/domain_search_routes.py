from flask import Blueprint, request, jsonify
from app.services.domain_search import search_domains

bp = Blueprint("domain_search", __name__, url_prefix="/search")


@bp.get("/domains")
def search():
    user_id = request.args.get("user_id", "").strip()
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    query = request.args.get("q", "")
    tag_filter = request.args.get("tag") or None
    min_minutes_raw = request.args.get("min_minutes", "0")
    limit_raw = request.args.get("limit", "20")

    try:
        min_minutes = float(min_minutes_raw)
    except ValueError:
        return jsonify({"error": "min_minutes must be a number"}), 400

    try:
        limit = int(limit_raw)
        if limit < 1 or limit > 100:
            raise ValueError
    except ValueError:
        return jsonify({"error": "limit must be an integer between 1 and 100"}), 400

    results = search_domains(
        user_id=user_id,
        query=query,
        tag_filter=tag_filter,
        min_minutes=min_minutes,
        limit=limit,
    )
    return jsonify({"results": [r.to_dict() for r in results], "count": len(results)}), 200
