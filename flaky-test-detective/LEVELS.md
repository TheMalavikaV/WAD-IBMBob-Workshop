# Flaky Test Detective: level cards

Report the highest level you reached, not whether you "finished". Level 2 is **opt-in**: pick it up when Level 1 passes
(or when you are curious). It extends Level 1; your Level 1 output on Level 1 data does not change.

---

## Level 2 card: "The retry that hides everything"

**Ready for a harder requirement?**

The platform team switched on **automatic retries**: when a test fails, CI runs it once more in the same run.
If the retry passes, the pipeline is green and nobody notices. Those are **hidden flakes**, and they cost CI time
every day. Run your Level 1 tool on `data/runs_retries.csv` and you will see the numbers go strange: a retry
looks like a second run of the same commit.

New rules (everything from Level 1 still holds unless changed here):

1. An **execution** is all valid PASS/FAIL rows with the same `run_id` and `test_name`: attempt `0` and, if the
   first attempt failed, attempt `1`. You may assume there is at most one row per `run_id` + `test_name` + `retry_attempt`.
2. The execution's **final status** is the status of its highest `retry_attempt`.
3. A **hidden flake** is an execution whose attempt `0` is `FAIL` and attempt `1` is `PASS`.
4. **Visible flakiness and regressions** use the Level 1 rules, with **one final status per execution** as the run.
   (So a run that failed and then passed counts as one `PASS` run.) Commit order: earliest timestamp of any row on that commit.
5. List every test that is not a regression and has `flaky_commits >= 1` **or** `hidden_flakes >= 1`, with
   `kind` = `"visible"` (only visible), `"hidden"` (only hidden) or `"both"`.
6. Sort by `flaky_commits + hidden_flakes` (highest first), then `test_name` (A to Z).

Run it as `<your command> --retries runs.csv`. Output:

```json
{
  "summary": {"rows_total": 10, "rows_malformed": 0, "rows_skipped": 0,
              "retries": 2,          // valid PASS/FAIL rows with retry_attempt 1
              "runs": 8,             // executions
              "tests": 2, "commits": 2},
  "flaky_tests": [
    {"test_name": "net.test_fails_twice", "kind": "visible", "flaky_commits": 1, "eligible_commits": 2,
     "flake_rate": 0.5, "hidden_flakes": 0, "runs": 4, "hidden_flake_rate": 0.0},
    {"test_name": "net.test_retry_hides_it", "kind": "hidden", "flaky_commits": 0, "eligible_commits": 2,
     "flake_rate": 0.0, "hidden_flakes": 1, "runs": 4, "hidden_flake_rate": 0.25}
  ],
  "regressions": []
}
```
- `runs` per test = number of executions of that test; `hidden_flake_rate = hidden_flakes / runs`.
- `flake_rate` is `0` when a test has no eligible commits. Rates are rounded to 4 decimals.

**Done when:** `python checker/check.py --cmd "..." --level 2` shows 2/2 PASS (`L2-01-hidden` is small enough to check by hand).

---

## Level 3 ideas: "Trustworthy"
- Automated tests in your language, built from the example folders (the agent can generate them).
- Tests for the tricky bits: a commit with one run, a test that fails only on the last 2 commits, SKIP-only tests, blank lines, `\r\n` line endings.
- Missing file or wrong header → a clear message on stderr and a non-zero exit code (no stack trace).
- `--format md`: the same report as a Markdown table a human would paste into a chat.
- Performance: time your tool on `data/runs.csv` (about 50k rows). Under 5 seconds is a good target.
- A README that explains how to run it and what the numbers mean.

## Level 4 ideas: "Go further"
- **Likely-cause hints** per flaky test: fails only on one `runner` → environment problem; failures have much larger
  `duration_ms` than passes → timeout; fails across all runners at random → test-order or concurrency issue.
- **Quarantine list** ranked by wasted CI time (sum of `duration_ms` of failed attempts and re-runs).
- **Trend:** is a test getting flakier over time (by week or by 100 commits)?
- **Output for humans:** an HTML report, or a pull-request comment ("3 tests in this PR are known flakes").
