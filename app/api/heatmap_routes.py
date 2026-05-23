from flask import Blueprint, jsonify, request
from app.services.visit_store import get_visits_for_user
from app.services.heatmap_builder import get_heatmap_summary, build_daily_heatmap, build_hourly_heatmap

heatmap_bp = Blueprint("heatmap", __name__, url_prefix="/heatmap")


@heatmap_bp.route("/<user_id>", methods=["GET"])
def summary(user_id: str):
    """Return full heatmap summary (daily + hourly) for a user."""
    domain = request.args.get("domain")
    days = request.args.get("days", 30, type=int)
    if days < 1 or days > 365:
        return jsonify({"error": "days must be between 1 and 365"}), 400

    visits = get_visits_for_user(user_id)
    data = get_heatmap_summary(visits, domain=domain, days=days)
    return jsonify(data), 200


@heatmap_bp.route("/<user_id>/daily", methods=["GET"])
def daily(user_id: str):
    """Return daily heatmap (date -> minutes) for a user."""
    domain = request.args.get("domain")
    days = request.args.get("days", 30, type=int)
    if days < 1 or days > 365:
        return jsonify({"error": "days must be between 1 and 365"}), 400

    visits = get_visits_for_user(user_id)
    data = build_daily_heatmap(visits, domain=domain, days=days)
    return jsonify({"daily": data}), 200


@heatmap_bp.route("/<user_id>/hourly", methods=["GET"])
def hourly(user_id: str):
    """Return hourly heatmap (hour -> minutes) for a user."""
    domain = request.args.get("domain")

    visits = get_visits_for_user(user_id)
    data = build_hourly_heatmap(visits, domain=domain)
    return jsonify({"hourly": data}), 200
