from flask import Blueprint, request, jsonify
from app.services import tag_store

tag_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tag_bp.get("/<user_id>")
def list_tags(user_id: str):
    tags = tag_store.get_tags_for_user(user_id)
    return jsonify([t.to_dict() for t in tags]), 200


@tag_bp.post("/<user_id>")
def create_tag(user_id: str):
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400
    tag = tag_store.create_tag(
        user_id=user_id,
        name=name,
        domains=body.get("domains", []),
        color=body.get("color"),
    )
    return jsonify(tag.to_dict()), 201


@tag_bp.patch("/<tag_id>")
def update_tag(tag_id: str):
    body = request.get_json(silent=True) or {}
    tag = tag_store.update_tag(
        tag_id=tag_id,
        name=body.get("name"),
        domains=body.get("domains"),
        color=body.get("color"),
    )
    if tag is None:
        return jsonify({"error": "tag not found"}), 404
    return jsonify(tag.to_dict()), 200


@tag_bp.delete("/<tag_id>")
def delete_tag(tag_id: str):
    removed = tag_store.delete_tag(tag_id)
    if not removed:
        return jsonify({"error": "tag not found"}), 404
    return "", 204


@tag_bp.get("/<user_id>/domain/<domain>")
def tags_for_domain(user_id: str, domain: str):
    tags = tag_store.get_tags_for_domain(user_id, domain)
    return jsonify([t.to_dict() for t in tags]), 200
