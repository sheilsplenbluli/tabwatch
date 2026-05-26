from flask import Blueprint, request, jsonify
from app.models.domain_flag import DomainFlag
import app.services.domain_flag_store as flag_store

bp = Blueprint("domain_flags", __name__, url_prefix="/flags")


@bp.get("")
def list_flags():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    domain = request.args.get("domain")
    if domain:
        flags = flag_store.get_flags_for_domain(user_id, domain)
    else:
        flags = flag_store.get_flags_for_user(user_id)
    return jsonify([f.to_dict() for f in flags]), 200


@bp.post("")
def create_flag():
    data = request.get_json(silent=True) or {}
    required = ("user_id", "domain", "reason")
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400
    try:
        flag = DomainFlag(
            user_id=data["user_id"],
            domain=data["domain"],
            reason=data["reason"],
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    flag_store.add_flag(flag)
    return jsonify(flag.to_dict()), 201


@bp.post("/<flag_id>/resolve")
def resolve_flag(flag_id: str):
    data = request.get_json(silent=True) or {}
    flag = flag_store.resolve_flag(flag_id, notes=data.get("notes", ""))
    if flag is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(flag.to_dict()), 200


@bp.delete("/<flag_id>")
def remove_flag(flag_id: str):
    deleted = flag_store.delete_flag(flag_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return "", 204
