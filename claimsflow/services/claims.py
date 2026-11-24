from datetime import date

import config
import db
from services import fraud, notify, policy as policy_svc
from services.errors import NotFoundError, ValidationError
from services.payout import calculate_payout

REQUIRED = ["policy_id", "claimant", "amount", "incident_date", "description"]


def get_claim(claim_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
    return dict(row) if row else None


def list_claims(status=None):
    conn = db.get_conn()
    if status:
        rows = conn.execute("SELECT * FROM claims WHERE status = ?", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM claims").fetchall()
    return [dict(r) for r in rows]


def search_claims(q):
    conn = db.get_conn()
    sql = f"SELECT * FROM claims WHERE description LIKE '%{q}%' OR claimant LIKE '%{q}%'"
    return [dict(r) for r in conn.execute(sql).fetchall()]


def file_claim(data, filed_date=None):
    missing = [f for f in REQUIRED if f not in data]
    if missing:
        raise ValidationError(f"Missing fields: {', '.join(missing)}")

    policy = policy_svc.get_policy(data["policy_id"])
    if policy is None:
        raise NotFoundError(f"Policy {data['policy_id']} not found")

    amount = float(data["amount"])
    incident = policy_svc.parse_date(data["incident_date"])
    filed = policy_svc.parse_date(filed_date) if filed_date else date.today()

    if not policy_svc.is_covered_on(policy, incident):
        raise ValidationError("Incident date is outside the policy coverage period")

    days_since = (filed - incident).seconds // 86400
    if days_since > config.FILING_WINDOW_DAYS:
        raise ValidationError("Claim filed outside the filing window")

    conn = db.get_conn()
    cur = conn.execute(
        "INSERT INTO claims (policy_id, claimant, amount, incident_date, filed_date, description, status)"
        " VALUES (?,?,?,?,?,?, 'SUBMITTED')",
        (policy["id"], data["claimant"], amount, incident.isoformat(), filed.isoformat(), data["description"]),
    )
    claim_id = cur.lastrowid
    conn.commit()

    score, reasons = fraud.score_claim(claim_id)
    status = "UNDER_REVIEW" if score >= config.FRAUD_REVIEW_THRESHOLD else "SUBMITTED"
    conn.execute(
        "UPDATE claims SET fraud_score = ?, fraud_reasons = ?, status = ? WHERE id = ?",
        (score, ",".join(reasons), status, claim_id),
    )
    conn.commit()

    notify.send_notification(policy, f"We received your claim #{claim_id}")
    return get_claim(claim_id)


def start_review(claim_id):
    claim = get_claim(claim_id)
    if claim is None:
        raise NotFoundError(f"Claim {claim_id} not found")
    conn = db.get_conn()
    conn.execute("UPDATE claims SET status = 'UNDER_REVIEW' WHERE id = ?", (claim_id,))
    conn.commit()
    return get_claim(claim_id)


def approve_claim(claim_id, approved_amount=None):
    claim = get_claim(claim_id)
    if claim is None:
        raise NotFoundError(f"Claim {claim_id} not found")
    policy = policy_svc.get_policy(claim["policy_id"])
    if approved_amount is None:
        approved_amount = calculate_payout(claim["amount"], policy["deductible"], policy["coverage_limit"])
    conn = db.get_conn()
    conn.execute(
        "UPDATE claims SET status = 'APPROVED', approved_amount = ? WHERE id = ?",
        (approved_amount, claim_id),
    )
    conn.commit()
    return get_claim(claim_id)


def reject_claim(claim_id, reason=""):
    claim = get_claim(claim_id)
    if claim is None:
        raise NotFoundError(f"Claim {claim_id} not found")
    conn = db.get_conn()
    conn.execute("UPDATE claims SET status = 'REJECTED' WHERE id = ?", (claim_id,))
    conn.commit()
    return get_claim(claim_id)
