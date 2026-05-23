"""Routes for domain trend data."""
from flask import Blueprint, jsonify, request

from app.services.domain_trend import compute_trend

bp = Blueprint("domain_trend", __name__, url_prefix="/trends")


@bp.get("/<user_id>/<path:domain>")
def get_trend(user_id: str, domain: str):
    """Return trend metrics for a domain.

    Query params:
      - period_days (int, default 7): length of each comparison window
    """
    raw_period = request.args.get("period_days", "7")
    try:
        period_days = int(raw_period)
        if period_days < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "period_days must be a positive integer"}), 400

    trend = compute_trend(user_id=user_id, domain=domain, period_days=period_days)
    return jsonify(trend.to_dict()), 200
