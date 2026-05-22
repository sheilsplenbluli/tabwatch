from flask import Blueprint, request, jsonify

from app.models.note import Note
from app.services import note_store

note_bp = Blueprint("notes", __name__, url_prefix="/notes")


@note_bp.get("/<user_id>")
def list_notes(user_id: str):
    domain = request.args.get("domain")
    if domain:
        notes = note_store.get_notes_for_domain(user_id, domain)
    else:
        notes = note_store.get_notes_for_user(user_id)
    return jsonify([n.to_dict() for n in notes]), 200


@note_bp.post("/")
def create_note():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    domain = data.get("domain")
    body = data.get("body")
    if not user_id or not domain or body is None:
        return jsonify({"error": "user_id, domain, and body are required"}), 400
    note = Note(user_id=user_id, domain=domain, body=body)
    note_store.add_note(note)
    return jsonify(note.to_dict()), 201


@note_bp.put("/<note_id>")
def edit_note(note_id: str):
    data = request.get_json(silent=True) or {}
    body = data.get("body")
    if body is None:
        return jsonify({"error": "body is required"}), 400
    note = note_store.update_note(note_id, body)
    if note is None:
        return jsonify({"error": "note not found"}), 404
    return jsonify(note.to_dict()), 200


@note_bp.delete("/<note_id>")
def remove_note(note_id: str):
    deleted = note_store.delete_note(note_id)
    if not deleted:
        return jsonify({"error": "note not found"}), 404
    return jsonify({"deleted": note_id}), 200
