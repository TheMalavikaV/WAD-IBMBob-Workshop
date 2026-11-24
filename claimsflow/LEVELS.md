# ClaimsFlow: Level 2 cards

**Ready for a harder requirement?** Each track has one Level 2 card. It builds on your Level 1 work and never
asks you to throw it away. Pick yours up only when Level 1 is done (or when you are curious). It's opt-in.

Level 3 and 4 ideas for each track are in the [README](README.md#where-this-can-go-the-ladder-for-each-track).
Report the highest level you reached, not whether you "finished".

---

## A. Bug Hunt: "Follow the money"

The payments team has two complaints: **some customers were paid twice**, and **the fraud review queue is full of
perfectly ordinary claims**. Make the payment path match the *Claim lifecycle* and *Fraud scoring* rules.

Expected results (all are straight from `docs/BUSINESS_RULES.md`):

| # | Do this | Expected |
|---|---|---|
| 1 | Approve a claim, then `POST /claims/{id}/pay` **twice** | 1st call succeeds; 2nd call returns **400**; exactly **one** row in `payouts` for that claim |
| 2 | `POST /claims/{id}/pay` on a claim that is `SUBMITTED`, `UNDER_REVIEW` or `REJECTED` | **400**, no payout row |
| 3 | File one ordinary claim: policy `POL-1003`, amount `1000`, incident `2026-09-10`, filed `2026-09-12` | fraud score **0**, status `SUBMITTED` |
| 4 | Then file a second claim on the same policy and incident date, amount `1040` (within 5%) | fraud score **50**, reasons include `DUPLICATE` |
| 5 | Instead, file the second claim with amount `1100` (10% higher) | **no** duplicate points |

Rows 3-5 are easiest to test at the service level, because the API always uses today's date as the filing date:
```python
from services import claims
c = claims.file_claim({"policy_id": "POL-1003", "claimant": "Chitra Nair", "amount": 1000,
                       "incident_date": "2026-09-10", "description": "Test"}, filed_date="2026-09-12")
```
(Use a throw-away database in tests: set `config.DB_PATH` to a temp file and call `db.init_db()` in `setUp`.)

Hint without spoilers: when you fix one of these, re-run *all* of them. Fixing one bug can reveal another.

---

## B. Safety Net: "Test through the front door"

Unit tests are good; adjusters use the **API**. Add API-level tests using Flask's test client:

- Each test starts from a **fresh, seeded, throw-away database** (temp file), so tests can run in any order.
- At least one test per endpoint in `docs/API.md`, covering the happy path **and** one error (404 or 400).
- No test depends on today's date (pass dates explicitly, or test through the service layer where the API would use `date.today()`).

Done when: `python -m unittest -v` runs both your unit and API tests, and running it twice in a row gives the same result.

---

## C. Break the Monolith: "Four services, one command"

Split ClaimsFlow along these seams, each a separate process:

| Service | Port | Owns |
|---|---|---|
| claims + public API (gateway) | 5001 | `docs/API.md` endpoints, claim intake and workflow |
| policy | 5002 | policies, quotes, coverage checks |
| payments + fraud | 5003 | fraud scoring, payout calculation and payment |
| notifications | 5004 | emails (still simulated) |

- One command starts everything: `python run_all.py` (and Ctrl+C stops everything). No Docker.
- The quick tour in `docs/API.md` still works against port 5001, unchanged.

---

## D. Real Data Layer: "Migrations without data loss"

- Put the schema in versioned files: `migrations/0001_initial.sql`, `0002_...sql`, ...
- `python migrate.py` applies the pending ones in order and records them in a `schema_migrations` table.
  Running it **twice** changes nothing the second time.
- Add migration `0002` that adds a `created_at` column to `claims` (or a new `claim_events` table).
  Run it against an **existing** `claimsflow.db`: all 6 seeded claims (and their payouts) must still be there.

---

## E. Secure & Compliant: "Who did what"

Auditors want to know who changed every claim. For the workshop, the caller's role comes from an
`X-Role` request header (a stand-in for real authentication):

- `adjuster`: may file, review, approve **up to 10,000**, and reject.
- `supervisor`: may do everything an adjuster can, approve any amount, and **pay**.
- Missing or unknown role on a state-changing request → **401**; a role that is not allowed → **403**.
- Every status change writes an audit row: claim id, old status, new status, role, timestamp.
- New endpoint `GET /claims/{id}/audit` returns that history oldest-first.

Write down the API change (this card *is* the reason).

---

## F. Agent Inside: "Recommend, do not decide"

Add `GET /claims/{id}/recommendation`:

```json
{"recommendation": "approve", "reasons": ["Fraud score 0: no fraud rules matched (BUSINESS_RULES.md, Fraud scoring)"]}
```

- `approve` when the fraud score is 0 **and** the amount is at most 20% of the coverage limit; otherwise `review`.
- Every reason cites the rule it comes from.
- The endpoint **never changes the claim**. A human still calls `/approve` or `/reject`.
