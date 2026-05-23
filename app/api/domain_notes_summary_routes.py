"""Routes for domain notes summary endpoint."""

from flask import Blueprint, jsonify, request

from app.services.domain_notes_summary import build_domain_notes_summary

bp = Blueprint("domain_notes_summary", __name__, url_prefix="/domain-notes-summary")


@bp.get("")
def get_summary():
    user_id = request.args.get("user_id", "").strip()
    domain = request.args.get("domain", "").strip()

    if not user_id or not domain:
        return jsonify({"error": "user_id and domain are required"}), 400

    summary = build_domain_notes_summary(user_id, domain)
    if summary is None:
        return jsonify({"error": f"no data found for domain '{domain}'"}), 404

    return jsonify(summary.to_dict()), 200
