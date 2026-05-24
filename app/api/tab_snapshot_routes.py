from flask import Blueprint, request, jsonify
from app.models.tab_snapshot import TabSnapshot
from app.services import tab_snapshot_store as store

bp = Blueprint("tab_snapshots", __name__, url_prefix="/snapshots")


@bp.route("", methods=["GET"])
def list_snapshots():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    snaps = store.get_snapshots_for_user(user_id)
    return jsonify([s.to_dict() for s in snaps]), 200


@bp.route("", methods=["POST"])
def create_snapshot():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    domains = data.get("domains")
    if not user_id or domains is None:
        return jsonify({"error": "user_id and domains required"}), 400
    if not isinstance(domains, list):
        return jsonify({"error": "domains must be a list"}), 400
    snap = TabSnapshot(
        user_id=user_id,
        domains=domains,
        label=data.get("label"),
    )
    store.add_snapshot(snap)
    return jsonify(snap.to_dict()), 201


@bp.route("/<snapshot_id>", methods=["GET"])
def get_snapshot(snapshot_id):
    snap = store.get_snapshot(snapshot_id)
    if snap is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(snap.to_dict()), 200


@bp.route("/<snapshot_id>/restore", methods=["POST"])
def restore_snapshot(snapshot_id):
    snap = store.restore_snapshot(snapshot_id)
    if snap is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(snap.to_dict()), 200


@bp.route("/<snapshot_id>", methods=["DELETE"])
def delete_snapshot(snapshot_id):
    deleted = store.delete_snapshot(snapshot_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": snapshot_id}), 200
