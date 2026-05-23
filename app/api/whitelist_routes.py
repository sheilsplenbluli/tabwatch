from flask import Blueprint, request, jsonify
from app.models.whitelist import WhitelistEntry
from app.services import whitelist_store

bp = Blueprint("whitelist", __name__, url_prefix="/whitelist")


@bp.get("/<user_id>")
def list_entries(user_id: str):
    entries = whitelist_store.get_entries_for_user(user_id)
    return jsonify([e.to_dict() for e in entries]), 200


@bp.post("/<user_id>")
def add_entry(user_id: str):
    body = request.get_json(silent=True) or {}
    domain = body.get("domain")
    if not domain:
        return jsonify({"error": "domain is required"}), 400
    entry = WhitelistEntry(
        user_id=user_id,
        domain=domain.lower(),
        label=body.get("label"),
    )
    whitelist_store.add_entry(entry)
    return jsonify(entry.to_dict()), 201


@bp.delete("/<user_id>/<path:domain>")
def remove_entry(user_id: str, domain: str):
    removed = whitelist_store.remove_entry(user_id, domain)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"removed": domain}), 200


@bp.get("/<user_id>/check/<path:domain>")
def check_entry(user_id: str, domain: str):
    allowed = whitelist_store.is_whitelisted(user_id, domain)
    return jsonify({"domain": domain, "whitelisted": allowed}), 200
