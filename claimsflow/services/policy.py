from datetime import date, datetime

import db

BASE_RATE_PER_1000 = {"AUTO": 24.0, "HEALTH": 15.0, "HOME": 6.0}


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_policy(policy_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM policies WHERE id = ?", (policy_id,)).fetchone()
    return dict(row) if row else None


def list_policies(status=None, page=1, page_size=10):
    conn = db.get_conn()
    offset = page * page_size
    sql = "SELECT * FROM policies"
    params = []
    if status:
        sql += " WHERE status = ?"
        params.append(status)
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params += [page_size, offset]
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def is_covered_on(policy, on_date):
    """A policy covers an incident if it is not cancelled and the incident date
    falls within [start_date, end_date] (both inclusive)."""
    if policy["status"] == "CANCELLED":
        return False
    start = parse_date(policy["start_date"])
    end = parse_date(policy["end_date"])
    return start <= parse_date(on_date) < end


def age_on(dob, on_date=None):
    on_date = parse_date(on_date) if on_date else date.today()
    return (on_date - parse_date(dob)).days // 365


def age_factor(age):
    if age < 25:
        return 1.5
    if age > 60:
        return 1.3
    return 1.0


def calculate_premium(policy_type, dob, coverage_limit, deductible, on_date=None):
    rate = BASE_RATE_PER_1000[policy_type]
    premium = rate * (coverage_limit / 1000) * age_factor(age_on(dob, on_date))
    if deductible >= 1000:
        premium *= 0.95
    return round(premium, 2)
