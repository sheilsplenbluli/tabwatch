from flask import Blueprint, request, jsonify
from app.models.domain_mood import DomainMood, VALID_MOODS
from app.services import domain_mood_store as store

bp = Blueprint("domain_mood", __name__, url_prefix="/moods")


@bp.route("", methods=["GET"])
def list_moods():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    domain = request.args.get("domain")
    if domain:
        moods = store.get_moods_for_domain(user_id, domain)
    else:
        moods = store.get_moods_for_user(user_id)
    return jsonify([m.to_dict() for m in moods]), 200


@bp.route("", methods=["POST"])
def create_mood():
    body = request.get_json(silent=True) or {}
    required = ["user_id", "domain", "mood"]
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400
    if body["mood"] not in VALID_MOODS:
        return jsonify({"error": f"mood must be one of {sorted(VALID_MOODS)}"}), 400
    mood = DomainMood(
        user_id=body["user_id"],
        domain=body["domain"],
        mood=body["mood"],
        note=body.get("note"),
    )
    store.add_mood(mood)
    return jsonify(mood.to_dict()), 201


@bp.route("/<mood_id>", methods=["PATCH"])
def edit_mood(mood_id: str):
    mood = store.get_mood(mood_id)
    if not mood:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    try:
        mood.update(mood=body.get("mood"), note=body.get("note"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    store.update_mood(mood)
    return jsonify(mood.to_dict()), 200


@bp.route("/<mood_id>", methods=["DELETE"])
def remove_mood(mood_id: str):
    deleted = store.delete_mood(mood_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": mood_id}), 200
