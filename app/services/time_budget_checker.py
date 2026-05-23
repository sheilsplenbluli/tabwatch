from datetime import datetime, timezone
from app.services import visit_store
from app.services import time_budget_store
from app.models.time_budget import TimeBudget


def _minutes_today_for_domain(user_id: str, domain: str) -> float:
    today = datetime.now(timezone.utc).date()
    total = 0.0
    for v in visit_store.get_visits_for_user(user_id):
        if v.domain != domain or v.duration_seconds is None:
            continue
        start = v.start_time
        if hasattr(start, "date") and start.date() == today:
            total += v.duration_seconds / 60.0
    return round(total, 2)


def check_budget_for_domain(user_id: str, domain: str) -> dict:
    budget = time_budget_store.get_budget_for_domain(user_id, domain)
    if budget is None:
        return {"has_budget": False, "domain": domain}
    minutes_used = _minutes_today_for_domain(user_id, domain)
    return {
        "has_budget": True,
        "domain": domain,
        "daily_limit_minutes": budget.daily_limit_minutes,
        "minutes_used": minutes_used,
        "percent_used": budget.percent_used(minutes_used),
        "exceeded": budget.is_exceeded(minutes_used),
        "enabled": budget.enabled,
        "label": budget.label,
    }


def check_all_budgets_for_user(user_id: str) -> list[dict]:
    budgets = time_budget_store.get_budgets_for_user(user_id)
    return [check_budget_for_domain(user_id, b.domain) for b in budgets]
