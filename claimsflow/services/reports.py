import db


def summary():
    conn = db.get_conn()
    total_premium = conn.execute("SELECT SUM(premium) FROM policies WHERE status = 'ACTIVE'").fetchone()[0]
    total_paid = conn.execute("SELECT SUM(amount) FROM payouts").fetchone()[0] or 0
    total_claimed = conn.execute("SELECT SUM(amount) FROM claims").fetchone()[0] or 0
    by_status = {r["status"]: r["n"] for r in conn.execute("SELECT status, COUNT(*) AS n FROM claims GROUP BY status")}
    return {
        "claims_by_status": by_status,
        "total_claimed": total_claimed,
        "total_paid": total_paid,
        "loss_ratio": round(total_paid / total_premium * 100, 2),
    }
