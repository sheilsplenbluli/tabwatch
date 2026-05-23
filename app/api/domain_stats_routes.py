from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.services.domain_stats import (
    get_stats_summary,
    get_busiest_hour,
    get_busiest_day,
    get_domain_visit_count,
    get_total_time_seconds,
)

bp = Blueprint("domain_stats", __name__, url_prefix="/stats")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


@bp.route("/<user_id>/summary", methods=["GET"])
def summary(user_id: str):
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    if not start_str or not end_str:
        return jsonify({"error": "start and end query params required"}), 400
    try:
        start = _parse_dt(start_str)
        end = _parse_dt(end_str)
    except ValueError:
        return jsonify({"error": "invalid datetime format"}), 400
    return jsonify(get_stats_summary(user_id, start, end))


@bp.route("/<user_id>/busiest-hour", methods=["GET"])
def busiest_hour(user_id: str):
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    if not start_str or not end_str:
        return jsonify({"error": "start and end query params required"}), 400
    try:
        start = _parse_dt(start_str)
        end = _parse_dt(end_str)
    except ValueError:
        return jsonify({"error": "invalid datetime format"}), 400
    hour = get_busiest_hour(user_id, start, end)
    return jsonify({"user_id": user_id, "busiest_hour": hour})


@bp.route("/<user_id>/domain-count", methods=["GET"])
def domain_count(user_id: str):
    domain = request.args.get("domain")
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    if not domain or not start_str or not end_str:
        return jsonify({"error": "domain, start, and end query params required"}), 400
    try:
        start = _parse_dt(start_str)
        end = _parse_dt(end_str)
    except ValueError:
        return jsonify({"error": "invalid datetime format"}), 400
    count = get_domain_visit_count(user_id, domain, start, end)
    return jsonify({"user_id": user_id, "domain": domain, "visit_count": count})
