from flask import Blueprint, request, jsonify
from app.models.annotation import Annotation
from app.services import annotation_store

bp = Blueprint("annotations", __name__, url_prefix="/annotations")


@bp.get("/")
def list_annotations():
    user_id = request.args.get("user_id")
    domain = request.args.get("domain")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    if domain:
        results = annotation_store.get_annotations_for_domain(user_id, domain)
    else:
        results = annotation_store.get_annotations_for_user(user_id)
    return jsonify([a.to_dict() for a in results]), 200


@bp.post("/")
def create_annotation():
    data = request.get_json(silent=True) or {}
    required = ("user_id", "domain", "body")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {missing}"}), 400
    ann = Annotation(
        user_id=data["user_id"],
        domain=data["domain"],
        body=data["body"],
        label=data.get("label", ""),
    )
    annotation_store.add_annotation(ann)
    return jsonify(ann.to_dict()), 201


@bp.patch("/<annotation_id>")
def edit_annotation(annotation_id: str):
    data = request.get_json(silent=True) or {}
    ann = annotation_store.update_annotation(
        annotation_id,
        body=data.get("body"),
        label=data.get("label"),
    )
    if ann is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(ann.to_dict()), 200


@bp.delete("/<annotation_id>")
def remove_annotation(annotation_id: str):
    deleted = annotation_store.delete_annotation(annotation_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": annotation_id}), 200
