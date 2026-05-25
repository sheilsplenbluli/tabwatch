from flask import Blueprint, request, jsonify
from app.models.custom_report import CustomReport
from app.services import custom_report_store as store
from app.services import visit_store
from datetime import datetime

bp = Blueprint("custom_reports", __name__, url_prefix="/reports")


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


@bp.get("/")
def list_reports():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    reports = store.get_reports_for_user(user_id)
    return jsonify([r.to_dict() for r in reports]), 200


@bp.post("/")
def create_report():
    body = request.get_json(silent=True) or {}
    required = ["user_id", "name", "domains", "start_iso", "end_iso"]
    for field in required:
        if field not in body:
            return jsonify({"error": f"{field} is required"}), 400
    try:
        report = CustomReport(
            user_id=body["user_id"],
            name=body["name"],
            domains=body["domains"],
            start_iso=body["start_iso"],
            end_iso=body["end_iso"],
            description=body.get("description"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    store.add_report(report)
    return jsonify(report.to_dict()), 201


@bp.put("/<report_id>")
def edit_report(report_id: str):
    report = store.get_report(report_id)
    if not report:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    if "name" in body:
        try:
            report.update_name(body["name"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    if "description" in body:
        report.description = body["description"]
    if "domains" in body:
        report.domains = body["domains"]
    store.update_report(report)
    return jsonify(report.to_dict()), 200


@bp.delete("/<report_id>")
def remove_report(report_id: str):
    deleted = store.delete_report(report_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": report_id}), 200
