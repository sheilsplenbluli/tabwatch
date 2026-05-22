from datetime import datetime, timezone
from typing import List, Optional

from app.models.export import ExportBundle, ExportRecord
from app.models.domain_visit import DomainVisit
from app.services.visit_store import get_visits_for_user
from app.services.tag_tagger import get_tags_for_domain
from app.services.tag_store import get_tags_for_user


def _iso(dt: Optional[datetime]) -> str:
    if dt is None:
        return ""
    return dt.isoformat()


def build_export(
    user_id: str,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> ExportBundle:
    visits: List[DomainVisit] = get_visits_for_user(user_id)
    user_tags = get_tags_for_user(user_id)
    records = []

    for v in visits:
        if not v.end_time:
            continue
        if since and v.start_time < since:
            continue
        if until and v.start_time > until:
            continue

        tags = [
            t.name
            for t in get_tags_for_domain(v.domain, user_tags)
        ]

        records.append(
            ExportRecord(
                user_id=user_id,
                domain=v.domain,
                start_time=_iso(v.start_time),
                end_time=_iso(v.end_time),
                duration_seconds=v.duration_seconds or 0.0,
                tags=tags,
            )
        )

    records.sort(key=lambda r: r.start_time)

    return ExportBundle(
        user_id=user_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        records=records,
    )


def export_to_csv(bundle: ExportBundle) -> str:
    lines = ["user_id,domain,start_time,end_time,duration_seconds,tags"]
    for r in bundle.records:
        tag_str = "|".join(r.tags)
        lines.append(
            f"{r.user_id},{r.domain},{r.start_time},{r.end_time},{r.duration_seconds:.2f},{tag_str}"
        )
    return "\n".join(lines)
