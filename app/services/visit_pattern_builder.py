from typing import List, Optional
from app.models.visit_pattern import VisitPattern, HourlyPattern
from app.models.domain_visit import DomainVisit
from app.services.visit_store import get_visits_for_user


def _closed_visits_for_domain(user_id: str, domain: str) -> List[DomainVisit]:
    return [
        v for v in get_visits_for_user(user_id)
        if v.domain == domain and not v.is_active()
    ]


def build_visit_pattern(user_id: str, domain: str) -> Optional[VisitPattern]:
    visits = _closed_visits_for_domain(user_id, domain)
    if not visits:
        return None

    pattern = VisitPattern(user_id=user_id, domain=domain)
    hourly_map = {h.hour: h for h in pattern.hourly}

    total_minutes = 0.0
    for visit in visits:
        hour = visit.start_time.hour
        slot = hourly_map[hour]
        slot.visit_count += 1
        duration = visit.duration_seconds / 60.0 if visit.duration_seconds else 0.0
        slot.total_minutes += duration
        total_minutes += duration

    pattern.total_visits = len(visits)
    pattern.peak_hour = pattern.compute_peak()
    pattern.avg_session_minutes = total_minutes / len(visits) if visits else 0.0
    return pattern


def get_all_patterns_for_user(user_id: str) -> List[VisitPattern]:
    visits = get_visits_for_user(user_id)
    domains = {v.domain for v in visits if not v.is_active()}
    results = []
    for domain in sorted(domains):
        p = build_visit_pattern(user_id, domain)
        if p:
            results.append(p)
    return results
