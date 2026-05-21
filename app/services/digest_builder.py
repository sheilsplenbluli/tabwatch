from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.models.domain_visit import DomainVisit
from app.models.weekly_digest import WeeklyDigest


def get_week_start(ref: Optional[datetime] = None) -> datetime:
    """Return the most recent Monday 00:00 UTC relative to ref (or now)."""
    ref = ref or datetime.now(timezone.utc)
    # weekday(): Monday=0, Sunday=6
    days_since_monday = ref.weekday()
    monday = ref - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def build_digest(
    user_id: str,
    visits: List[DomainVisit],
    week_start: Optional[datetime] = None,
) -> WeeklyDigest:
    """
    Build a WeeklyDigest for the given user and list of visits.
    If week_start is not provided, defaults to the most recent Monday.
    """
    if week_start is None:
        week_start = get_week_start()

    return WeeklyDigest.from_visits(
        user_id=user_id,
        visits=visits,
        week_start=week_start,
    )


def format_digest_text(digest: WeeklyDigest, top_n: int = 5) -> str:
    """Render a plain-text summary suitable for email body."""
    lines = [
        f"Weekly Digest for {digest.user_id}",
        f"Period: {digest.week_start.strftime('%Y-%m-%d')} — {digest.week_end.strftime('%Y-%m-%d')}",
        f"Total tracked time: {digest.total_tracked_seconds() / 3600:.2f} hours",
        "",
        f"Top {top_n} domains:",
    ]

    for i, summary in enumerate(digest.top_domains(top_n), start=1):
        lines.append(
            f"  {i}. {summary.domain} — {summary.total_minutes} min ({summary.visit_count} visits)"
        )

    if not digest.summaries:
        lines.append("  No activity recorded this week.")

    return "\n".join(lines)
