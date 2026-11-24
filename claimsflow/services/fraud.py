import db
from services import policy as policy_svc


def score_claim(claim_id):
    """Rules (see docs/BUSINESS_RULES.md):
      +30  amount > 80% of coverage limit
      +40  incident within 30 days of policy start
      +50  another claim on the same policy, same incident date, amount within 5%
    """
    conn = db.get_conn()
    claim = dict(conn.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone())
    policy = policy_svc.get_policy(claim["policy_id"])
    score, reasons = 0, []

    if claim["amount"] > 0.8 * policy["coverage_limit"]:
        score += 30
        reasons.append("HIGH_AMOUNT")

    days_from_start = (policy_svc.parse_date(claim["incident_date"]) - policy_svc.parse_date(policy["start_date"])).days
    if days_from_start < 30:
        score += 40
        reasons.append("NEW_POLICY")

    rows = conn.execute(
        "SELECT amount FROM claims WHERE policy_id = ? AND incident_date = ?",
        (claim["policy_id"], claim["incident_date"]),
    ).fetchall()
    if [r for r in rows if r["amount"] == claim["amount"]]:
        score += 50
        reasons.append("DUPLICATE")

    return score, reasons
