from datetime import datetime, timezone
from typing import List, Tuple

from app.models.alert_rule import AlertRule
from app.models.domain_visit import DomainVisit
from app.services.alert_store import get_rules_for_user


def _minutes_today(visits: List[DomainVisit], domain: str) -> float:
    """Sum closed visit durations for a domain within today (UTC)."""
    today = datetime.now(timezone.utc).date()
    total = 0.0
    for v in visits:
        if v.domain != domain:
            continue
        if v.end_time is None:
            continue
        if v.start_time.date() != today:
            continue
        total += v.duration_seconds or 0.0
    return total / 60.0


def check_alerts_for_user(
    user_id: str, visits: List[DomainVisit]
) -> List[Tuple[AlertRule, float]]:
    """
    Check all alert rules for a user against today's visit data.
    Returns a list of (rule, minutes_spent) for each triggered rule.
    """
    triggered: List[Tuple[AlertRule, float]] = []
    rules = get_rules_for_user(user_id)
    for rule in rules:
        minutes = _minutes_today(visits, rule.domain)
        if rule.is_triggered(minutes):
            triggered.append((rule, minutes))
    return triggered


def format_alert_message(rule: AlertRule, minutes_spent: float) -> str:
    percent = int((minutes_spent / rule.daily_limit_minutes) * 100)
    return (
        f"Alert: You've spent {minutes_spent:.1f} min on {rule.domain} today "
        f"({percent}% of your {rule.daily_limit_minutes}-min daily limit)."
    )
