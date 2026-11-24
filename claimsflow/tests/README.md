# tests/

Empty on purpose: the previous team never wrote tests. Track A and Track B start here.

- Name files `test_*.py`. Run them from the `claimsflow` folder with `python -m unittest -v`
  (or `python -m pytest` if you install pytest).
- Use a throw-away database per test: set `config.DB_PATH` to a temp file, then call `db.init_db()`.
  See `smoke_test.py` for the pattern.
- `time.sleep` in `services/notify.py` makes notifications slow; patching it in tests
  (`unittest.mock.patch("time.sleep")`) keeps the suite fast.
