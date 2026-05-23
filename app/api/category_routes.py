from flask import Blueprint, request, jsonify
from app.models.category import Category
from app.services import category_store

category_bp = Blueprint("categories", __name__, url_prefix="/categories")


@category_bp.get("/")
def list_categories():
    user_id = request.args.get("user_id", "")
    cats = category_store.get_categories_for_user(user_id)
    return jsonify([c.to_dict() for c in cats])


@category_bp.post("/")
def create_category():
    data = request.get_json(silent=True) or {}
    if not data.get("user_id") or not data.get("name"):
        return jsonify({"error": "user_id and name are required"}), 400
    cat = Category(
        user_id=data["user_id"],
        name=data["name"],
        color=data.get("color", "#6366f1"),
        domains=data.get("domains", []),
    )
    category_store.create_category(cat)
    return jsonify(cat.to_dict()), 201


@category_bp.put("/<category_id>")
def update_category(category_id: str):
    cat = category_store.get_category(category_id)
    if cat is None:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    if "name" in data:
        cat.name = data["name"]
    if "color" in data:
        cat.color = data["color"]
    if "domains" in data:
        cat.domains = data["domains"]
    category_store.update_category(cat)
    return jsonify(cat.to_dict())


@category_bp.delete("/<category_id>")
def delete_category(category_id: str):
    removed = category_store.delete_category(category_id)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": category_id})


@category_bp.get("/domain")
def category_for_domain():
    user_id = request.args.get("user_id", "")
    domain = request.args.get("domain", "")
    cat = category_store.get_category_for_domain(user_id, domain)
    if cat is None:
        return jsonify({"category": None})
    return jsonify(cat.to_dict())
