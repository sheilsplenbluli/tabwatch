from flask import Blueprint, request, jsonify
from app.models.time_budget import TimeBudget
from app.services import time_budget_store
from app.services.time_budget_checker import check_budget_for_domain, check_all_budgets_for_user

bp = Blueprint("time_budget", __name__, url_prefix="/budgets")


@bp.get("/<user_id>")
def list_budgets(user_id: str):
    budgets = time_budget_store.get_budgets_for_user(user_id)
    return jsonify([b.to_dict() for b in budgets])


@bp.post("/<user_id>")
def create_budget(user_id: str):
    data = request.get_json(silent=True) or {}
    domain = data.get("domain")
    limit = data.get("daily_limit_minutes")
    if not domain or limit is None:
        return jsonify({"error": "domain and daily_limit_minutes required"}), 400
    if not isinstance(limit, int) or limit <= 0:
        return jsonify({"error": "daily_limit_minutes must be a positive integer"}), 400
    budget = TimeBudget(
        user_id=user_id,
        domain=domain,
        daily_limit_minutes=limit,
        label=data.get("label"),
        enabled=data.get("enabled", True),
    )
    time_budget_store.add_budget(budget)
    return jsonify(budget.to_dict()), 201


@bp.put("/<user_id>/<budget_id>")
def update_budget(user_id: str, budget_id: str):
    budget = time_budget_store.get_budget(budget_id)
    if budget is None or budget.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    if "daily_limit_minutes" in data:
        budget.daily_limit_minutes = data["daily_limit_minutes"]
    if "label" in data:
        budget.label = data["label"]
    if "enabled" in data:
        budget.enabled = bool(data["enabled"])
    time_budget_store.update_budget(budget)
    return jsonify(budget.to_dict())


@bp.delete("/<user_id>/<budget_id>")
def delete_budget(user_id: str, budget_id: str):
    budget = time_budget_store.get_budget(budget_id)
    if budget is None or budget.user_id != user_id:
        return jsonify({"error": "not found"}), 404
    time_budget_store.delete_budget(budget_id)
    return jsonify({"deleted": budget_id})


@bp.get("/<user_id>/check")
def check_all(user_id: str):
    return jsonify(check_all_budgets_for_user(user_id))


@bp.get("/<user_id>/check/<path:domain>")
def check_one(user_id: str, domain: str):
    return jsonify(check_budget_for_domain(user_id, domain))
