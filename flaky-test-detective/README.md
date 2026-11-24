# Flaky Test Detective

**Greenfield · any language (Node.js or Python suggested; Java welcome) · input: a CSV of CI history**

← [Back to the workshop hub](../README.md) · [Level cards](LEVELS.md) · [Agent guide](../AGENT_GUIDE.md) ·
**[Share your experience](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md)**

---

## SETUP (about 2 minutes)

**Prerequisites:** Git, Python **3.10+** (for the checker), plus the language you choose:
Node.js **18+**, Python 3.10+, or JDK 17+. See [PREREQUISITES.md](../PREREQUISITES.md). No packages to install.

```
git clone https://github.com/<you>/<your-copy>.git
cd <your-copy>/flaky-test-detective
```

**Smoke test** (checks that the checker runs on your machine):

| Windows | macOS / Linux |
|---|---|
| `python checker/check.py --compare examples/L1-01-basic/expected.json examples/L1-01-basic/expected.json` | `python3 checker/check.py --compare examples/L1-01-basic/expected.json examples/L1-01-basic/expected.json` |

Expected output: `PASS`

**Check your tool against all examples** (once you have one):
```
python checker/check.py --cmd "node detective.js"        # or "python detective.py", "java Main.java", ...
```
The checker prints `PASS`/`FAIL` per example and the first difference it found. You can also diff by hand:
every example folder has `runs.csv` and the exact `expected.json`.

### Common problems
- `python` not found: use `python3` (macOS/Linux) or `py` (Windows). If `python3` opens the Microsoft Store on Windows, use `python` or `py`.
- Quote your command: `--cmd "node detective.js"`. Paths with spaces need quotes too.
- `java Main.java` needs JDK 17+ (single-file mode; no Maven or Gradle needed).
- On Windows, if your output has odd characters, make sure you print plain UTF-8 / ASCII JSON.

---

## The problem (30 seconds)

CI keeps failing and developers keep pressing "re-run" without knowing why. Build a tool that reads CI history
and tells the team **which tests are flaky, how bad each one is**, and which failures are **real regressions**
(really broken, re-running will not help).

The AI agent writes the code. The form is open (CLI, API, web page), but your tool must also be runnable as the
command-line contract below, so the checker can verify it.

## Input: `runs.csv`

| Column | Example | Meaning |
|---|---|---|
| `run_id` | `r00042` | one CI pipeline run |
| `commit_sha` | `5e4e7c0` | the commit that was tested |
| `test_name` | `checkout.test_apply_coupon` | |
| `status` | `PASS`, `FAIL` or `SKIP` | |
| `duration_ms` | `412` | |
| `timestamp` | `2026-10-01T08:00:01Z` | when the test finished (UTC) |
| `runner` | `linux-1`, `windows-2`, ... | the CI machine |
| `retry_attempt` | `0` or `1` | always `0` in Level 1 data; used in Level 2 |

- The first line is always exactly this header: `run_id,commit_sha,test_name,status,duration_ms,timestamp,runner,retry_attempt`
- Fields never contain commas or quotes, so a plain split on `,` is correct. Lines end with `\n` (accept `\r\n` too).

| File | Rows | Use |
|---|---|---|
| `examples/*/runs.csv` | 8 to 520 | acceptance examples, each with its `expected.json` |
| `data/runs.csv` | 49,570 (4 MB) | the real thing: run your finished tool on it. No expected file: tell us what you found! |
| `data/runs_retries.csv` | 21,369 | Level 2 data (with retries) |

**Tip:** do not let the agent read `data/runs.csv` into its context. Point it at an example instead.

## The rules (Level 1)

1. **Valid rows.** A data row is *valid* when it has exactly 8 fields; `run_id`, `commit_sha`, `test_name` and
   `runner` are not empty; `status` is exactly `PASS`, `FAIL` or `SKIP` (upper case); `duration_ms` is digits only;
   `timestamp` looks exactly like `YYYY-MM-DDTHH:MM:SSZ`; `retry_attempt` is `0` or `1`.
   Every other row is **malformed**: count it and ignore it. Completely blank lines are ignored and not counted at all.
2. **SKIP rows** are valid but ignored by every rule below. A **run** is a valid `PASS` or `FAIL` row.
3. **Flaky on a commit.** A test is *flaky on a commit* if it has at least one `PASS` **and** at least one `FAIL` run
   on that same commit.
4. **Flake rate.** A test's *eligible commits* are the commits where it has **at least 2 runs**.
   `flake_rate = flaky commits / eligible commits`.
5. **Commit order.** Commits are ordered by the earliest `timestamp` of any run on that commit (ties: `commit_sha`
   alphabetically). Do **not** rely on the order of lines in the file.
6. **Real regression.** Take the commits on which the test has runs, in commit order. If the last **3 or more** of them
   contain only `FAIL` runs, and the test has at least one `PASS` run on an earlier commit, the test is a
   **real regression**. `broken_since` is the first commit of that all-FAIL stretch.
   A real regression is **never** listed as flaky.
7. **Report.** `flaky_tests` lists every test that is not a regression and has at least one flaky commit,
   sorted by `flake_rate` (highest first), then `flaky_commits` (highest first), then `test_name` (A to Z).
   `regressions` is sorted by `test_name`. Healthy tests are not listed.

## Output contract

```
<your command> runs.csv            -> prints the Level 1 report (JSON) to stdout, exit code 0
<your command> --retries runs.csv  -> prints the Level 2 report (see LEVELS.md)
```

```json
{
  "summary": {
    "rows_total": 10,        // data rows, excluding the header and blank lines
    "rows_malformed": 0,
    "rows_skipped": 0,       // valid SKIP rows
    "runs": 10,              // valid PASS/FAIL rows
    "tests": 2,              // distinct test names that have runs
    "commits": 3             // distinct commits that have runs
  },
  "flaky_tests": [
    {"test_name": "app.test_a", "flaky_commits": 1, "eligible_commits": 2, "flake_rate": 0.5}
  ],
  "regressions": [
    {"test_name": "svc.test_x", "broken_since": "e02d5c3"}
  ]
}
```
(The `//` comments are for you to read; real JSON has none.)
- `flake_rate` is rounded to **4 decimal places**; the checker accepts a difference of up to 0.0001.
- Key order and whitespace do not matter. Extra keys are allowed (handy for Level 4 hints).

## Acceptance examples (all visible, no hidden tests)

| Example | What it shows |
|---|---|
| `L1-01-basic` | One flaky commit; a commit with a single run is not eligible. |
| `L1-02-regression` | A real regression (3 all-FAIL commits); a test failing only on the last 2 commits (neither flaky nor a regression); lines in the file are not in commit order. |
| `L1-03-malformed` | Malformed rows, SKIP rows, a blank line. |
| `L1-04-sample` | 522 generated rows: the full set of rules together, including ties in the ranking. |
| `L2-*` | Level 2 (retries). See [LEVELS.md](LEVELS.md). |

## Where this can go: the ladder

Nobody is expected to finish. Report the **highest level you reached**.

| Level | Goal | Done when |
|---|---|---|
| **1 Core** | Parse the CSV and output the ranked list of flaky tests with flake rates, plus real regressions. | `python checker/check.py --cmd "..." --level 1` shows 4/4 PASS. |
| **2 Extension** | *Opt-in card:* CI now auto-retries failed tests. Find the **hidden** flakes. See [LEVELS.md](LEVELS.md). | `--level 2` shows 2/2 PASS. |
| **3 Trustworthy** | Your own automated tests (start from the examples); clear errors for a missing file or a wrong header (non-zero exit code); `--format md` Markdown output; full `data/runs.csv` in under 5 seconds; a README. | Tests green; `data/runs.csv` timed. |
| **4 Go further** | Likely-cause hints (fails only on one runner → environment; fails when slow → timeout); a quarantine list ranked by wasted CI time; trend over time; an HTML report or a PR comment. | Your hints on `data/runs.csv` make sense to a human. |

## Short agent tips (full version: [AGENT_GUIDE.md](../AGENT_GUIDE.md))
- First prompt: give the agent this README (rules + output contract) and **one** small example. Ask it to restate rules 3-6 in its own words before coding.
- Ask it to turn every `examples/*` folder into a test, and to run `python checker/check.py --cmd "..."` itself.
- Verify one number by hand: open `examples/L1-01-basic/runs.csv` and work out `app.test_a`'s flake rate yourself.
- Never paste `data/runs.csv` into the chat. Tell the agent its size and columns.

**When you stop:** [open an experience report](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md).
Tell us the highest level you reached and what stopped you.
