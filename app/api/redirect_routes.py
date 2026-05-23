from flask import Blueprint, request, jsonify
from app.services.domain_redirect_tracker import (
    record_redirect,
    get_redirects_for_user,
    get_redirect,
    delete_redirect,
)

redirect_bp = Blueprint("redirects", __name__, url_prefix="/redirects")


@redirect_bp.route("/", methods=["POST"])
def track_redirect():
    body = request.get_json(silent=True) or {}
    required = ("user_id", "from_domain", "to_domain", "timestamp")
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400

    rec = record_redirect(
        user_id=body["user_id"],
        from_domain=body["from_domain"],
        to_domain=body["to_domain"],
        timestamp=body["timestamp"],
    )
    return jsonify(rec.to_dict()), 201


@redirect_bp.route("/", methods=["GET"])
def list_redirects():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    records = get_redirects_for_user(user_id)
    return jsonify([r.to_dict() for r in records]), 200


@redirect_bp.route("/<redirect_id>", methods=["GET"])
def get_one(redirect_id: str):
    rec = get_redirect(redirect_id)
    if rec is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(rec.to_dict()), 200


@redirect_bp.route("/<redirect_id>", methods=["DELETE"])
def remove_redirect(redirect_id: str):
    deleted = delete_redirect(redirect_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": redirect_id}), 200
