from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, Response

from app.services.export_builder import build_export, export_to_csv

export_bp = Blueprint("export", __name__)


def _parse_dt(value: str) -> datetime:
    """Parse ISO datetime string; raise ValueError on bad input."""
    return datetime.fromisoformat(value)


@export_bp.route("/export/<user_id>/json", methods=["GET"])
def export_json(user_id: str):
    since = request.args.get("since")
    until = request.args.get("until")

    try:
        since_dt = _parse_dt(since) if since else None
        until_dt = _parse_dt(until) if until else None
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    bundle = build_export(user_id, since=since_dt, until=until_dt)
    return jsonify(bundle.to_dict()), 200


@export_bp.route("/export/<user_id>/csv", methods=["GET"])
def export_csv(user_id: str):
    since = request.args.get("since")
    until = request.args.get("until")

    try:
        since_dt = _parse_dt(since) if since else None
        until_dt = _parse_dt(until) if until else None
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    bundle = build_export(user_id, since=since_dt, until=until_dt)
    csv_text = export_to_csv(bundle)

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=tabwatch_{user_id}.csv"
        },
    )
