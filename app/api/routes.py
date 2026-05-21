from flask import Flask, request, jsonify
from datetime import datetime, timezone
from app.models.domain_visit import DomainVisit
from app.services.digest_builder import build_digest, format_digest_text
from app.services.digest_scheduler import collect_visits_for_user

app = Flask(__name__)

# In-memory store keyed by user_id; replace with DB in production
_visits: dict[str, list[dict]] = {}


@app.route("/visits", methods=["POST"])
def record_visit():
    """Record a new domain visit for a user."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    required = {"user_id", "domain"}
    missing = required - data.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(sorted(missing))}"}), 400

    visit = DomainVisit(
        domain=data["domain"],
        user_id=data["user_id"],
        start_time=datetime.now(timezone.utc),
    )
    raw = visit.to_dict()
    _visits.setdefault(data["user_id"], []).append(raw)
    return jsonify(raw), 201


@app.route("/visits/<user_id>/<domain>/close", methods=["POST"])
def close_visit(user_id: str, domain: str):
    """Close the most recent active visit for a user/domain pair."""
    user_visits = _visits.get(user_id, [])
    # Find last active visit for this domain
    target = None
    for raw in reversed(user_visits):
        v = DomainVisit.from_dict(raw)
        if v.domain == domain and v.is_active():
            target = (raw, v)
            break

    if target is None:
        return jsonify({"error": "No active visit found"}), 404

    raw, visit = target
    visit.close()
    updated = visit.to_dict()
    raw.update(updated)
    return jsonify(updated), 200


@app.route("/digest/<user_id>", methods=["GET"])
def get_digest(user_id: str):
    """Return the weekly digest summary for a user."""
    visits = collect_visits_for_user(user_id, _visits.get(user_id, []))
    if not visits:
        return jsonify({"message": "No activity found"}), 200

    digest = build_digest(user_id, visits)
    return jsonify({
        "user_id": user_id,
        "week_start": digest.week_start.isoformat(),
        "total_domains": len(digest.domain_summaries),
        "top_domains": [s.to_dict() for s in digest.top_domains(10)],
        "text_summary": format_digest_text(digest),
    }), 200
