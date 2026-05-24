from flask import Blueprint, request, jsonify
from app.models.site_rating import SiteRating, VALID_RATINGS
import app.services.site_rating_store as store

bp = Blueprint("site_ratings", __name__, url_prefix="/ratings")


@bp.get("/<user_id>")
def list_ratings(user_id: str):
    ratings = store.get_ratings_for_user(user_id)
    return jsonify([r.to_dict() for r in ratings]), 200


@bp.post("/<user_id>")
def create_rating(user_id: str):
    body = request.get_json(silent=True) or {}
    domain = body.get("domain")
    rating_val = body.get("rating")
    if not domain or rating_val is None:
        return jsonify({"error": "domain and rating are required"}), 400
    if rating_val not in VALID_RATINGS:
        return jsonify({"error": f"rating must be one of {sorted(VALID_RATINGS)}"}), 400
    existing = store.get_rating_for_domain(user_id, domain)
    if existing:
        existing.update(rating=rating_val, note=body.get("note"))
        store.update_rating(existing)
        return jsonify(existing.to_dict()), 200
    r = SiteRating(
        user_id=user_id,
        domain=domain,
        rating=rating_val,
        note=body.get("note", ""),
    )
    store.add_rating(r)
    return jsonify(r.to_dict()), 201


@bp.get("/<user_id>/domain/<path:domain>")
def get_for_domain(user_id: str, domain: str):
    r = store.get_rating_for_domain(user_id, domain)
    if r is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(r.to_dict()), 200


@bp.delete("/<user_id>/<rating_id>")
def remove_rating(user_id: str, rating_id: str):
    r = store.get_rating(rating_id)
    if r is None or r.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    store.delete_rating(rating_id)
    return jsonify({"deleted": rating_id}), 200
