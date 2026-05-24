from flask import Blueprint, jsonify, request
from app.services.domain_clustering import compute_clusters, get_cluster_for_domain

bp = Blueprint("domain_clustering", __name__, url_prefix="/clustering")


@bp.get("/")
def list_clusters():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    clusters = compute_clusters(user_id)
    return jsonify([c.to_dict() for c in clusters])


@bp.get("/domain")
def cluster_for_domain():
    user_id = request.args.get("user_id")
    domain = request.args.get("domain")
    if not user_id or not domain:
        return jsonify({"error": "user_id and domain required"}), 400
    cluster = get_cluster_for_domain(user_id, domain)
    if cluster is None:
        return jsonify({"error": "no cluster found for domain"}), 404
    return jsonify(cluster.to_dict())
