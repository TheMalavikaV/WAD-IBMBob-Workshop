# One Purchase, One Line

**Brownfield · Node.js 18+ · no dependencies, no build step · about 170 lines of app code**

← [Back to the workshop hub](../README.md) · [Level cards](LEVELS.md) · [Agent guide](../AGENT_GUIDE.md) ·
**[Share your experience](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md)**

---

## SETUP (about 2 minutes)

**Prerequisites:** Git, Node.js **18+** (see [PREREQUISITES.md](../PREREQUISITES.md)). There is nothing to `npm install`:
the project has zero dependencies.

```
git clone https://github.com/<you>/<your-copy>.git
cd <your-copy>/one-purchase-one-line
```

The commands are the same on Windows, macOS and Linux:

| What | Command | Expected |
|---|---|---|
| Smoke test | `npm run smoke` | `SMOKE TEST OK - /health returned ok, /transactions returned 10 events` |
| Run the tests | `npm test` | `# pass 5`, `# fail 0` |
| Start the app | `npm start` | `Banking simulator listening on http://localhost:5001` |
| Acceptance checks | `npm run check` (or `npm run check -- L1`) | `0/4 checks passed` today. Your job is to change that |

Then open **http://localhost:5001** in a browser: that is the customer's transaction list. Count the pizzas.

### Common problems
- **`node` / `npm` not found:** reopen the terminal after installing Node.js. On Linux install a current Node with `nvm` (see PREREQUISITES.md).
- **`npm` in PowerShell says "running scripts is disabled"** (`npm.ps1 cannot be loaded`): run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use `npm.cmd test` / `npm.cmd start`.
- **Port 5001 in use:** stop the other program, or choose another port. macOS/Linux: `PORT=3000 npm start`. Windows PowerShell: `$env:PORT=3000; npm start`. Windows cmd: `set PORT=3000 && npm start`.
  (`npm test`, `npm run smoke` and `npm run check` pick free ports themselves.)
- **`curl` in PowerShell:** use `curl.exe` or `Invoke-RestMethod http://localhost:5001/transactions`, or a browser.
- **Node 18 prints an `ExperimentalWarning`:** harmless.

---

## The story (30 seconds)

A customer bought **one pizza**. Their banking app shows **two Rs.799 entries**: Pizza Palace, Pizza Palace.
They call support, convinced they were charged twice. They were not: the card network sends a **hold**
(`AUTHORISED`) and later a **settlement** (`CAPTURED`) for the same purchase, and the app lists every raw event.

Extend this small banking simulator so the app shows **one line per purchase**.

**The rule:** events with the **same `auth_id` are the same purchase**. Different `auth_id`s are different
purchases, **even when the amount and merchant are the same** (the customer really did buy two movie tickets).

Start with [ARCHITECTURE.md](ARCHITECTURE.md) (one page: the files, the event schema and the purchase lifecycle).

| What | Where |
|---|---|
| Routes | `src/app.js`: `GET /health`, `GET /transactions`, `GET /` |
| In-memory data | `src/store.js`, seeded from `data/seed-events.json` (10 events) |
| Tests | `tests/` (`node --test`, built in) |
| Acceptance checks | `scripts/check.js` + `expected/*.json` |
| Level 2 data | `data/batch-1.json`; Level 3 data: `data/batch-edge-cases.json` |

## Level 1 rules: `GET /timeline`

Add `GET /timeline` that returns **one entry per `auth_id`**:

```json
{
  "purchases": [
    {
      "auth_id": "AUTH-1001",
      "merchant": "Pizza Palace",
      "amount_paise": 79900,
      "status": "Completed",
      "steps": [
        {"type": "AUTHORISED", "event_time": "2026-11-03T19:02:11Z", "amount_paise": 79900, "event_id": "EVT-0001"},
        {"type": "CAPTURED",   "event_time": "2026-11-05T02:00:00Z", "amount_paise": 79900, "event_id": "EVT-0002"}
      ]
    }
  ]
}
```

1. **Steps** are the purchase's events in `event_time` order (oldest first; ties: `event_id` A to Z).
2. **Status:** `Refunded` if any step is `REFUNDED`; otherwise `Completed` if any step is `CAPTURED`; otherwise `Pending`.
3. **merchant** = the merchant of the first step. **amount_paise** = the amount of the `AUTHORISED` step (or of the first step if there is none).
4. **Purchases** are ordered **newest first** by the `event_time` of their first step (ties: `auth_id` A to Z).
5. Amounts stay integers in paise. Extra keys are fine (e.g. a display string).

The seed has five purchases, so the expected timeline has five entries:

| Seed case | auth_id | Expected |
|---|---|---|
| The pizza (hold, then settlement) | AUTH-1001 | **1** entry, `Completed`, 2 steps |
| Two separate Rs.799 movie tickets | AUTH-1002, AUTH-1003 | **2** entries, both `Completed` |
| Shoes, refunded | AUTH-1004 | 1 entry, `Refunded`, 3 steps |
| Fuel, hold only | AUTH-1005 | 1 entry, `Pending` |

The exact expected response is in [`expected/timeline-seed.json`](expected/timeline-seed.json).
`npm run check -- L1` compares your `/timeline` with it.

## Where this can go: the ladder

Nobody is expected to finish. Report the **highest level you reached**.

| Level | Goal | Done when |
|---|---|---|
| **1 Core** | `GET /timeline`: one entry per purchase with status and steps in time order. Optional: make `GET /` show it. | `npm run check -- L1` passes; your own test for the pizza case. |
| **2 Extension** | *Opt-in card:* importing the same batch twice must not create duplicates, and late events must land in the right place. See [LEVELS.md](LEVELS.md). | `npm run check -- L2` passes (2 checks). |
| **3 Trustworthy** | Edge cases: refund before the capture arrives, partial refund, unknown `auth_id`, invalid events; a test proving import is idempotent. See [LEVELS.md](LEVELS.md). | `npm run check -- L3` passes; `npm test` green with your new tests. |
| **4 Go further** | A plain-language explanation per purchase ("This is one purchase: a hold on 3 Nov, settled on 5 Nov"), a nicer UI, anomaly hints. | A non-developer understands the screen. |

A GitHub Actions workflow (`.github/workflows/one-purchase-tests.yml`) runs `npm test` on every push.

## Short agent tips (full version: [AGENT_GUIDE.md](../AGENT_GUIDE.md))
- First prompt: point the agent at this README, `ARCHITECTURE.md` and `expected/timeline-seed.json`. Ask it to restate the
  grouping and status rules and to list its questions before coding.
- Ask for a failing test first ("the pizza is one purchase"), then the code.
- Tell it the commands: `npm test` and `npm run check -- L1`. Let it run them.
- Keep it small: no frameworks, no database, no new dependencies needed.
- Verify by eye: open http://localhost:5001 and count the pizzas.

**When you stop:** [open an experience report](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md).
Tell us the highest level you reached and what stopped you.
