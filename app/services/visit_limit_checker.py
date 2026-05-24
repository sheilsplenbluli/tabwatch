from datetime import datetime, timezone
from app.services.visit_limit_store import get_limit, get_limits_for_user
from app.services.visit_store import get_visits_for_user


def _visits_today_for_domain(user_id: str, domain: str) -> int:
    today = datetime.now(timezone.utc).date()
    count = 0
    for v in get_visits_for_user(user_id):
        if v.domain != domain:
            continue
        visit_date = v.start_time
        if hasattr(visit_date, "date"):
            if visit_date.date() == today:
                count += 1
        else:
            count += 1
    return count


def check_limit_for_domain(user_id: str, domain: str) -> dict:
    limit = get_limit(user_id, domain)
    if limit is None:
        return {"domain": domain, "limited": False, "limit": None}
    count = _visits_today_for_domain(user_id, domain)
    return {
        "domain": domain,
        "limited": True,
        "enabled": limit.enabled,
        "max_visits_per_day": limit.max_visits_per_day,
        "visits_today": count,
        "exceeded": limit.is_exceeded(count),
        "percent_used": limit.percent_used(count),
    }


def check_all_limits_for_user(user_id: str) -> list[dict]:
    limits = get_limits_for_user(user_id)
    return [check_limit_for_domain(user_id, lim.domain) for lim in limits]
