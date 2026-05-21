from datetime import datetime, timezone
from typing import List, Dict, Any

from app.models.domain_visit import DomainVisit
from app.services.digest_builder import get_week_start, build_digest, format_digest_text
from app.services.email_sender import send_weekly_digest_email


def collect_visits_for_user(user_id: str, storage: Dict[str, List[Dict[str, Any]]]) -> List[DomainVisit]:
    """
    Retrieve DomainVisit objects for a given user from a storage mapping.
    Storage is expected to be a dict keyed by user_id with lists of serialised visits.
    """
    raw_visits = storage.get(user_id, [])
    return [DomainVisit.from_dict(v) for v in raw_visits]


def run_weekly_digest_for_user(
    user_id: str,
    email: str,
    storage: Dict[str, List[Dict[str, Any]]],
    reference_time: datetime | None = None,
) -> bool:
    """
    Build and send the weekly digest email for a single user.
    Returns True if the email was sent successfully.
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    week_start = get_week_start(reference_time)
    visits = collect_visits_for_user(user_id, storage)
    digest = build_digest(visits, week_start)

    if not digest.top_domains:
        print(f"[digest_scheduler] No activity for user {user_id} — skipping email.")
        return False

    digest_text = format_digest_text(digest)
    success = send_weekly_digest_email(email, digest_text, week_start)

    if success:
        print(f"[digest_scheduler] Digest sent to {email} for week of {week_start.date()}.")
    return success


def run_weekly_digests(
    user_registry: Dict[str, str],
    storage: Dict[str, List[Dict[str, Any]]],
    reference_time: datetime | None = None,
) -> Dict[str, bool]:
    """
    Send weekly digests to all users in the registry.
    user_registry maps user_id -> email address.
    Returns a dict of user_id -> success status.
    """
    results: Dict[str, bool] = {}
    for user_id, email in user_registry.items():
        results[user_id] = run_weekly_digest_for_user(
            user_id, email, storage, reference_time
        )
    return results
