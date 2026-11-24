from datetime import datetime

import db
from services import notify, policy as policy_svc
from services.errors import NotFoundError


def calculate_payout(claim_amount, deductible, coverage_limit):
    """Business rule: payout = min(claim_amount - deductible, coverage_limit), never below 0."""
    payable = min(claim_amount, coverage_limit) - deductible
    return max(round(payable, 2), 0)


def pay_claim(claim_id):
    conn = db.get_conn()
    claim = conn.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
    if claim is None:
        raise NotFoundError(f"Claim {claim_id} not found")
    amount = claim["approved_amount"]
    conn.execute(
        "INSERT INTO payouts (claim_id, amount, paid_at) VALUES (?,?,?)",
        (claim_id, amount, datetime.utcnow().isoformat(timespec="seconds")),
    )
    conn.execute("UPDATE claims SET status = 'PAID' WHERE id = ?", (claim_id,))
    conn.commit()
    policy = policy_svc.get_policy(claim["policy_id"])
    notify.send_notification(policy, f"Claim {claim_id} paid: {amount}")
    return {"claim_id": claim_id, "amount": amount, "status": "PAID"}
