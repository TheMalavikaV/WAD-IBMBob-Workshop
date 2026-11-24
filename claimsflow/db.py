import sqlite3
import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS policies (
    id TEXT PRIMARY KEY,
    holder_name TEXT NOT NULL,
    holder_email TEXT NOT NULL,
    dob TEXT NOT NULL,
    type TEXT NOT NULL,
    coverage_limit REAL NOT NULL,
    deductible REAL NOT NULL,
    premium REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id TEXT NOT NULL,
    claimant TEXT NOT NULL,
    amount REAL NOT NULL,
    incident_date TEXT NOT NULL,
    filed_date TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    approved_amount REAL,
    fraud_score INTEGER DEFAULT 0,
    fraud_reasons TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS payouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    paid_at TEXT NOT NULL
);
"""

POLICIES = [
    ("POL-1001", "Asha Raman", "asha.raman@example.com", "1990-04-12", "AUTO", 50000, 500, 1200, "2026-01-01", "2026-12-31", "ACTIVE"),
    ("POL-1002", "Ben Carter", "ben.carter@example.com", "1958-09-30", "HEALTH", 100000, 1000, 1425, "2026-03-01", "2027-02-28", "ACTIVE"),
    ("POL-1003", "Chitra Nair", "chitra.nair@example.com", "1985-07-21", "HOME", 250000, 2500, 1500, "2026-02-15", "2027-02-14", "ACTIVE"),
    ("POL-1004", "Dev Patel", "dev.patel@example.com", "2003-01-05", "AUTO", 30000, 750, 1080, "2026-06-01", "2027-05-31", "ACTIVE"),
    ("POL-1005", "Elena Rossi", "elena.rossi@example.com", "1966-11-02", "HEALTH", 75000, 500, 1125, "2025-01-01", "2025-12-31", "EXPIRED"),
    ("POL-1006", "Farid Khan", "farid.khan@example.com", "1979-02-17", "HOME", 400000, 5000, 2400, "2026-01-01", "2026-12-31", "CANCELLED"),
]

# (policy_id, claimant, amount, incident, filed, description, status, approved, fraud_score, reasons)
CLAIMS = [
    ("POL-1001", "Asha Raman", 4200, "2026-03-10", "2026-03-12", "Rear bumper collision at traffic signal", "PAID", 3700, 0, ""),
    ("POL-1002", "Ben Carter", 18000, "2026-05-02", "2026-05-05", "Knee surgery and physiotherapy", "APPROVED", 17000, 0, ""),
    ("POL-1003", "Chitra Nair", 12500, "2026-07-19", "2026-07-20", "Water damage in kitchen from burst pipe", "UNDER_REVIEW", None, 0, ""),
    ("POL-1001", "Asha Raman", 900, "2026-09-01", "2026-09-02", "Windshield crack from road debris", "SUBMITTED", None, 0, ""),
    ("POL-1004", "Dev Patel", 28000, "2026-06-05", "2026-06-06", "Total loss collision on highway", "UNDER_REVIEW", None, 70, "HIGH_AMOUNT,NEW_POLICY"),
    ("POL-1004", "Dev Patel", 27900, "2026-06-05", "2026-06-07", "Total loss collision on highway", "UNDER_REVIEW", None, 120, "HIGH_AMOUNT,NEW_POLICY,DUPLICATE"),
]


def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0] == 0:
        conn.executemany("INSERT INTO policies VALUES (?,?,?,?,?,?,?,?,?,?,?)", POLICIES)
        conn.executemany(
            "INSERT INTO claims (policy_id, claimant, amount, incident_date, filed_date, description,"
            " status, approved_amount, fraud_score, fraud_reasons) VALUES (?,?,?,?,?,?,?,?,?,?)",
            CLAIMS,
        )
        conn.execute("INSERT INTO payouts (claim_id, amount, paid_at) VALUES (1, 3700, '2026-03-20T10:00:00')")
        conn.commit()
