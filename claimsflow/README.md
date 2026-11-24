# ClaimsFlow: take over an insurance claims app with an AI agent

**Brownfield · Python 3.10+ · Flask + SQLite · about 580 lines · no tests**

← [Back to the workshop hub](../README.md) · [Level cards](LEVELS.md) · [Agent guide](../AGENT_GUIDE.md) ·
**[Share your experience](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md)**

---

## SETUP (do this first, about 3 minutes)

**Prerequisites:** Git, Python **3.10+** (see [PREREQUISITES.md](../PREREQUISITES.md)). No database to install.

```
git clone https://github.com/<you>/<your-copy>.git
cd <your-copy>/claimsflow
```

Create a virtual environment, install Flask, and run the smoke test:

| | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| 1. Create venv | `python -m venv .venv` | `python3 -m venv .venv` |
| 2. Activate | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| 3. Install | `python -m pip install -r requirements.txt` | `python -m pip install -r requirements.txt` |
| 4. Smoke test | `python smoke_test.py` | `python smoke_test.py` |
| 5. Run the app | `python app.py` | `python app.py` |

(After activating the venv, `python` works on every OS.)

**Expected smoke-test output:**
```
SMOKE TEST OK - /health returned ok, /claims returned 6 claims
```
The app listens on **http://localhost:5001**. Open http://localhost:5001/claims in a browser to see the seeded claims.

**Run the tests:** `python -m unittest -v` (or `python -m pytest` if you install pytest).
Today it prints `NO TESTS RAN`: there are none yet, which is part of the problem.

### Common problems
- **`python` not found / opens the Microsoft Store:** on macOS/Linux use `python3` to create the venv; on Windows try `py -m venv .venv`.
- **`Activate.ps1 cannot be loaded`** (Windows): run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.
  In `cmd.exe` use `.venv\Scripts\activate.bat` instead.
- **`externally-managed-environment`** from pip (macOS Homebrew, newer Ubuntu/Debian): you skipped the venv. Activate it and retry.
- **`ensurepip is not available`** (Ubuntu/Debian): `sudo apt install python3-venv`, delete `.venv`, create it again.
- **Port 5001 in use:** stop the other program, or change `port=5001` at the bottom of `app.py`. Never use 5000 on a Mac (AirPlay).
- **`curl` examples fail in PowerShell:** in PowerShell, `curl` is an alias for something else. Use `curl.exe`, or
  `Invoke-RestMethod http://localhost:5001/health`, or just open GET URLs in a browser.
- **Want a clean database?** Stop the app and delete `claimsflow.db`. It is re-created and re-seeded on the next start.

---

## The story (30 seconds)

ClaimsFlow processes auto, health and home insurance claims. It was built by two people for a
200-claims-a-month pilot and nobody has touched it for a year. Now a large insurer is taking it to
**100x the volume**. Auditors are asking questions, and adjusters report **wrong payouts, duplicate
payments and strange fraud flags**. The authors have left and there are **no tests**.

Your team takes it over, with an AI agent doing the typing.

**The one rule that matters:** [`docs/BUSINESS_RULES.md`](docs/BUSINESS_RULES.md) is the source of truth.
When the code and the rules disagree, **the rules win**. Keep the HTTP contract in [`docs/API.md`](docs/API.md)
working (or write down why you changed it).

| Area | Where |
|---|---|
| REST API | `app.py` |
| Business logic | `services/` (`policy`, `claims`, `fraud`, `payout`, `notify`, `reports`) |
| Persistence | `db.py` (SQLite file `claimsflow.db`, seeded on first start) |
| Config | `config.py` |
| Docs | `docs/BUSINESS_RULES.md`, `docs/API.md`, `docs/ARCHITECTURE.md` |
| Your tests | `tests/` (empty) |

## Pick ONE track

For 1.5 hours we recommend **A. Bug Hunt**: it gives the fastest feedback loop with the agent.

| Track | Mission in one line |
|---|---|
| **A. Bug Hunt** *(recommended)* | Find code that breaks the business rules, prove it with a failing test, fix it. |
| **B. Safety Net** | Build the test suite the project never had, so future changes are safe. |
| **C. Break the Monolith** | Split one capability into its own service without breaking the API. |
| **D. Real Data Layer** | Put all database access behind one layer with repeatable migrations. |
| **E. Secure & Compliant** | Make it audit-ready: no secrets in code, safe SQL, no leaked internals. |
| **F. Agent Inside** *(stretch)* | Add a claims-triage helper that explains fraud scores in plain language. |

## Where this can go: the ladder for each track

Nobody is expected to finish. Report the **highest level you reached**.
Level 2 is an opt-in card in [LEVELS.md](LEVELS.md): pick it up when you are ready.

### A. Bug Hunt (recommended)
| Level | Goal | Done when |
|---|---|---|
| **1 Core** | Find and fix **3** places where the code breaks `BUSINESS_RULES.md`. | For each: a test in `tests/` that **failed before** the fix and **passes after**, plus one line in `CHANGES.md` (rule broken → fix). |
| **2 Extension** | *"Follow the money"* card in [LEVELS.md](LEVELS.md). | The checks on the card pass. |
| **3 Trustworthy** | Every section of `BUSINESS_RULES.md` has at least one test; fixes are minimal and explained. | `python -m unittest` is green; `CHANGES.md` lists each fix with its test name. |
| **4 Go further** | Hunt the security and privacy defects (see the Non-functional rules), find a bug that only shows up after another is fixed. | Each has a test or a written reproduction. |

### B. Safety Net
| Level | Goal | Done when |
|---|---|---|
| **1 Core** | Unit tests for the payout formula and the premium table (all three policy types, all three age bands). | Tests run with `python -m unittest`; at least one boundary value per rule. |
| **2 Extension** | *"Test through the front door"* card. | API-level tests on a throw-away database. |
| **3 Trustworthy** | Tests that **disagree with the current code** are kept and marked (`@unittest.expectedFailure`, with the rule quoted) instead of deleted. | A reader can list today's known defects just by reading test names. |
| **4 Go further** | Coverage report (`pip install coverage`), aim for 80%+ of `services/`; try a hand-made mutation (change a `>=` to `>`) and check a test catches it. | |

### C. Break the Monolith (no Docker needed)
| Level | Goal | Done when |
|---|---|---|
| **1 Core** | Move **notifications** into a separate small HTTP service (port 5004) that the main app calls. | Both processes run; filing a claim still works; `docs/API.md` unchanged. |
| **2 Extension** | *"Four services, one command"* card. | |
| **3 Trustworthy** | Contract tests for `docs/API.md` against the new setup; sensible behaviour when one service is down. | |
| **4 Go further** | Events / a queue instead of synchronous calls; a database per service; a short design note on the seams you chose. | |

### D. Real Data Layer
| Level | Goal | Done when |
|---|---|---|
| **1 Core** | All SQL lives in one data-access module (a repository layer); connections are closed; services no longer write SQL. | The API behaves exactly as before (characterise it with a few tests first). |
| **2 Extension** | *"Migrations without data loss"* card. | |
| **3 Trustworthy** | Config (DB path, secrets) from environment variables with safe defaults; tests run against a temporary database. | |
| **4 Go further** | If you already have PostgreSQL installed, run the same repository layer against it. Money as integer cents. | |

### E. Secure & Compliant
| Level | Goal | Done when |
|---|---|---|
| **1 Core** | Secrets out of `config.py` (environment variables + `.env.example`), and every SQL query parameterised. | `git grep -i password` finds no real values; a search for `' OR 1=1 --` returns nothing it shouldn't. |
| **2 Extension** | *"Who did what"* card (roles + audit trail). | |
| **3 Trustworthy** | API errors never include stack traces or internal details; logs contain no customer emails; tests for each. | |
| **4 Go further** | A one-page threat model; rate limiting; review notification recipients for privacy leaks. | |

### F. Agent Inside (stretch)
| Level | Goal | Done when |
|---|---|---|
| **1 Core** | `GET /claims/{id}/explain` returns a plain-language explanation of the fraud score, citing the rule for every point. **No AI model needed**, a template is fine. | Works for every seeded claim. |
| **2 Extension** | *"Recommend, do not decide"* card. | |
| **3 Trustworthy** | Tests; the recommendation can never change a claim's status by itself. | |
| **4 Go further** | If you have an LLM API key, add a model-written summary behind a flag, with the rule-based explanation as the fallback. | |

## Short agent tips (full version: [AGENT_GUIDE.md](../AGENT_GUIDE.md))
- First prompt: point the agent at `docs/BUSINESS_RULES.md` and this README, tell it your track and level, and ask it to **plan and ask questions first**.
- "Write a test that fails on the current code, show me it failing, then fix." Red before green.
- Tell it the test command (`python -m unittest -v`) and let it run it.
- Check one number yourself: e.g. compute a payout by hand from the formula in `BUSINESS_RULES.md`.
- Keep a note of prompts and coin counts for the experience report.

## Ground rules
1. The rules in `docs/BUSINESS_RULES.md` win over existing behaviour.
2. Do not change the public HTTP contract in `docs/API.md` without writing down why.
3. Commit small and often. It helps you (and the agent) undo mistakes.
4. Optional: keep your best prompts in `agent-log/` and a short `CHANGES.md` of what you changed. Both make the debrief easier.

A GitHub Actions workflow (`.github/workflows/claimsflow-tests.yml`) runs the smoke test and everything in `tests/` on every push.
It is green while `tests/` is empty and starts doing real work as soon as you add tests.

**When you stop:** [open an experience report](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md).
Tell us the track, the highest level you reached and what stopped you.
