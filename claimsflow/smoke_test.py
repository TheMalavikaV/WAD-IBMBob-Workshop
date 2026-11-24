"""One-command smoke test: checks that ClaimsFlow starts and answers requests.

Run from the claimsflow folder:   python smoke_test.py
It uses a throw-away database, so it never touches claimsflow.db.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config  # noqa: E402

fd, tmp_db = tempfile.mkstemp(suffix=".db")
os.close(fd)
config.DB_PATH = tmp_db

try:
    from app import app  # noqa: E402  (importing app creates and seeds the temp database)

    client = app.test_client()
    health = client.get("/health").get_json()
    claims = client.get("/claims").get_json()
    assert health == {"status": "ok"}, health
    assert len(claims) == 6, len(claims)
    print(f"SMOKE TEST OK - /health returned {health['status']}, /claims returned {len(claims)} claims")
finally:
    try:
        os.remove(tmp_db)
    except OSError:
        pass
