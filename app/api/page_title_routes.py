from flask import Blueprint, request, jsonify
from app.services.page_title_store import (
    upsert_title,
    get_title,
    get_titles_for_user,
    get_titles_for_domain,
    delete_title,
)

page_title_bp = Blueprint("page_title", __name__, url_prefix="/titles")


@page_title_bp.route("", methods=["POST"])
def record_title():
    body = request.get_json(silent=True) or {}
    required = ("user_id", "domain", "url", "title")
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400
    entry = upsert_title(
        user_id=body["user_id"],
        domain=body["domain"],
        url=body["url"],
        title=body["title"],
    )
    return jsonify(entry.to_dict()), 201


@page_title_bp.route("", methods=["GET"])
def list_titles():
    user_id = request.args.get("user_id")
    domain = request.args.get("domain")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    if domain:
        entries = get_titles_for_domain(user_id, domain)
    else:
        entries = get_titles_for_user(user_id)
    return jsonify([e.to_dict() for e in entries]), 200


@page_title_bp.route("/lookup", methods=["GET"])
def lookup_title():
    user_id = request.args.get("user_id")
    url = request.args.get("url")
    if not user_id or not url:
        return jsonify({"error": "user_id and url required"}), 400
    entry = get_title(user_id, url)
    if entry is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(entry.to_dict()), 200


@page_title_bp.route("/delete", methods=["DELETE"])
def remove_title():
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id")
    url = body.get("url")
    if not user_id or not url:
        return jsonify({"error": "user_id and url required"}), 400
    removed = delete_title(user_id, url)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": True}), 200
