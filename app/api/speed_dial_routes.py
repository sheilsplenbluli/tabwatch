from flask import Blueprint, request, jsonify
from app.models.speed_dial import SpeedDial
from app.services import speed_dial_store

bp = Blueprint("speed_dial", __name__, url_prefix="/speed-dial")


@bp.get("/<user_id>")
def list_entries(user_id: str):
    entries = speed_dial_store.get_entries_for_user(user_id)
    return jsonify([e.to_dict() for e in entries]), 200


@bp.post("/<user_id>")
def create_entry(user_id: str):
    body = request.get_json(silent=True) or {}
    domain = body.get("domain", "").strip()
    label = body.get("label", "").strip()
    if not domain or not label:
        return jsonify({"error": "domain and label are required"}), 400
    position = body.get("position", 0)
    entry = SpeedDial(user_id=user_id, domain=domain, label=label, position=position)
    speed_dial_store.add_entry(entry)
    return jsonify(entry.to_dict()), 201


@bp.patch("/<user_id>/<entry_id>")
def edit_entry(user_id: str, entry_id: str):
    entry = speed_dial_store.get_entry(entry_id)
    if not entry or entry.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    if "label" in body:
        try:
            entry.update_label(body["label"])
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    if "position" in body:
        try:
            entry.move_to(int(body["position"]))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    if "pinned" in body:
        if entry.pinned != bool(body["pinned"]):
            entry.toggle_pin()
    speed_dial_store.update_entry(entry)
    return jsonify(entry.to_dict()), 200


@bp.delete("/<user_id>/<entry_id>")
def remove_entry(user_id: str, entry_id: str):
    entry = speed_dial_store.get_entry(entry_id)
    if not entry or entry.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    speed_dial_store.delete_entry(entry_id)
    return jsonify({"deleted": entry_id}), 200


@bp.post("/<user_id>/<entry_id>/touch")
def touch_entry(user_id: str, entry_id: str):
    entry = speed_dial_store.get_entry(entry_id)
    if not entry or entry.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    entry.touch()
    speed_dial_store.update_entry(entry)
    return jsonify(entry.to_dict()), 200
