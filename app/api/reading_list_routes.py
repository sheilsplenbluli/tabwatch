from flask import Blueprint, request, jsonify
from app.models.reading_list import ReadingListEntry
import app.services.reading_list_store as store

reading_list_bp = Blueprint("reading_list", __name__, url_prefix="/reading-list")


@reading_list_bp.get("/<user_id>")
def list_entries(user_id: str):
    include_archived = request.args.get("archived", "false").lower() == "true"
    entries = store.get_entries_for_user(user_id, include_archived=include_archived)
    return jsonify([e.to_dict() for e in entries]), 200


@reading_list_bp.post("/")
def create_entry():
    data = request.get_json(silent=True) or {}
    required = ["user_id", "url", "domain", "title"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400
    entry = ReadingListEntry(
        user_id=data["user_id"],
        url=data["url"],
        domain=data["domain"],
        title=data["title"],
        notes=data.get("notes", ""),
    )
    store.add_entry(entry)
    return jsonify(entry.to_dict()), 201


@reading_list_bp.post("/<entry_id>/read")
def mark_read(entry_id: str):
    entry = store.get_entry(entry_id)
    if not entry:
        return jsonify({"error": "not found"}), 404
    entry.mark_read()
    store.update_entry(entry)
    return jsonify(entry.to_dict()), 200


@reading_list_bp.post("/<entry_id>/archive")
def archive_entry(entry_id: str):
    entry = store.get_entry(entry_id)
    if not entry:
        return jsonify({"error": "not found"}), 404
    entry.archive()
    store.update_entry(entry)
    return jsonify(entry.to_dict()), 200


@reading_list_bp.delete("/<entry_id>")
def remove_entry(entry_id: str):
    removed = store.delete_entry(entry_id)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": entry_id}), 200
