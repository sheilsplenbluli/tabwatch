from flask import Blueprint, request, jsonify
from app.models.bookmark import Bookmark
from app.services import bookmark_store

bookmark_bp = Blueprint("bookmarks", __name__, url_prefix="/bookmarks")


@bookmark_bp.get("/")
def list_bookmarks():
    user_id = request.args.get("user_id")
    domain = request.args.get("domain")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    if domain:
        results = bookmark_store.get_bookmarks_for_domain(user_id, domain)
    else:
        results = bookmark_store.get_bookmarks_for_user(user_id)
    return jsonify([b.to_dict() for b in results]), 200


@bookmark_bp.post("/")
def create_bookmark():
    data = request.get_json(silent=True) or {}
    required = {"user_id", "domain", "url", "title"}
    missing = required - data.keys()
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(sorted(missing))}"}), 400
    bookmark = Bookmark(
        user_id=data["user_id"],
        domain=data["domain"],
        url=data["url"],
        title=data["title"],
        note=data.get("note", ""),
        tags=data.get("tags", []),
    )
    bookmark_store.add_bookmark(bookmark)
    return jsonify(bookmark.to_dict()), 201


@bookmark_bp.patch("/<bookmark_id>")
def edit_bookmark(bookmark_id: str):
    bookmark = bookmark_store.get_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    if "title" in data:
        try:
            bookmark.update_title(data["title"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    if "note" in data:
        bookmark.note = data["note"]
    if "tags" in data:
        bookmark.tags = data["tags"]
    if "pinned" in data:
        bookmark.pinned = bool(data["pinned"])
    bookmark_store.update_bookmark(bookmark)
    return jsonify(bookmark.to_dict()), 200


@bookmark_bp.delete("/<bookmark_id>")
def remove_bookmark(bookmark_id: str):
    if not bookmark_store.delete_bookmark(bookmark_id):
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": bookmark_id}), 200


@bookmark_bp.post("/<bookmark_id>/pin")
def toggle_pin(bookmark_id: str):
    bookmark = bookmark_store.get_bookmark(bookmark_id)
    if not bookmark:
        return jsonify({"error": "not found"}), 404
    pinned = bookmark.toggle_pin()
    bookmark_store.update_bookmark(bookmark)
    return jsonify({"bookmark_id": bookmark_id, "pinned": pinned}), 200
