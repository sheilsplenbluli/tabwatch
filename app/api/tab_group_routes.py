from flask import Blueprint, request, jsonify
from app.models.tab_group import TabGroup
from app.services import tab_group_store

tab_group_bp = Blueprint("tab_groups", __name__, url_prefix="/tab-groups")


@tab_group_bp.get("")
def list_groups():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    groups = tab_group_store.get_groups_for_user(user_id)
    return jsonify([g.to_dict() for g in groups]), 200


@tab_group_bp.post("")
def create_group():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    name = data.get("name")
    if not user_id or not name:
        return jsonify({"error": "user_id and name required"}), 400
    group = TabGroup(
        user_id=user_id,
        name=name,
        domains=data.get("domains", []),
        color=data.get("color"),
    )
    tab_group_store.create_group(group)
    return jsonify(group.to_dict()), 201


@tab_group_bp.put("/<group_id>")
def update_group(group_id: str):
    group = tab_group_store.get_group(group_id)
    if not group:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    if "name" in data:
        try:
            group.rename(data["name"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    if "color" in data:
        group.color = data["color"]
    if "domains" in data:
        group.domains = list(data["domains"])
    tab_group_store.update_group(group)
    return jsonify(group.to_dict()), 200


@tab_group_bp.delete("/<group_id>")
def delete_group(group_id: str):
    removed = tab_group_store.delete_group(group_id)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": group_id}), 200


@tab_group_bp.get("/domain")
def group_for_domain():
    user_id = request.args.get("user_id")
    domain = request.args.get("domain")
    if not user_id or not domain:
        return jsonify({"error": "user_id and domain required"}), 400
    group = tab_group_store.get_group_for_domain(user_id, domain)
    if not group:
        return jsonify({"group": None}), 200
    return jsonify(group.to_dict()), 200
