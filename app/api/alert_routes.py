from flask import Blueprint, request, jsonify
from app.models.alert_rule import AlertRule
from app.services.alert_store import (
    add_rule, get_rule, get_rules_for_user, delete_rule, update_rule
)

alert_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alert_bp.route("/<user_id>", methods=["GET"])
def list_rules(user_id: str):
    rules = get_rules_for_user(user_id)
    return jsonify([r.to_dict() for r in rules]), 200


@alert_bp.route("/<user_id>", methods=["POST"])
def create_rule(user_id: str):
    body = request.get_json(silent=True) or {}
    required = {"domain", "daily_limit_minutes"}
    if not required.issubset(body.keys()):
        return jsonify({"error": "domain and daily_limit_minutes are required"}), 400
    body["user_id"] = user_id
    try:
        rule = AlertRule.from_dict(body)
    except (KeyError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    add_rule(rule)
    return jsonify(rule.to_dict()), 201


@alert_bp.route("/<user_id>/<rule_id>", methods=["PUT"])
def update_rule_route(user_id: str, rule_id: str):
    existing = get_rule(user_id, rule_id)
    if existing is None:
        return jsonify({"error": "rule not found"}), 404
    body = request.get_json(silent=True) or {}
    body["user_id"] = user_id
    body["rule_id"] = rule_id
    body.setdefault("domain", existing.domain)
    body.setdefault("daily_limit_minutes", existing.daily_limit_minutes)
    updated = AlertRule.from_dict(body)
    update_rule(updated)
    return jsonify(updated.to_dict()), 200


@alert_bp.route("/<user_id>/<rule_id>", methods=["DELETE"])
def delete_rule_route(user_id: str, rule_id: str):
    removed = delete_rule(user_id, rule_id)
    if not removed:
        return jsonify({"error": "rule not found"}), 404
    return jsonify({"deleted": rule_id}), 200
