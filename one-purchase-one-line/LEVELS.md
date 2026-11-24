# One Purchase, One Line: level cards

Report the highest level you reached, not whether you "finished". The cards are **opt-in**: pick one up when you are ready.
Each one builds on the Level 1 timeline. Nothing in Level 1 changes.

---

## Level 2 card: "The network sends things twice, and late"

**Ready for a harder requirement?**

The card network delivers events in **batches**. Two facts of life:
- **Batches get re-sent.** If a batch is imported twice, the customer must not see anything twice.
  Two events with the same `event_id` are the same event; keep only the first one you received.
- **Events arrive out of order.** A settlement can arrive before its hold. Always order steps by `event_time`,
  never by arrival (`ingested_at`). (Your Level 1 rule already says this. Now it matters.)

Build `POST /import`. The body is a JSON array of events (same schema as the seed). The response:

```json
{"received": 6, "added": 4, "duplicates": 2}
```
- `received`: number of events in the body; `added`: newly stored; `duplicates`: skipped because the `event_id`
  was already stored (by the seed, an earlier import, or earlier in the same batch).
- The imported events also appear in `GET /transactions` (raw, arrival order).

`data/batch-1.json` contains: a capture for the pending fuel purchase, a refund of **one** of the two movie tickets,
a new grocery purchase whose capture arrives **before** its authorisation, an event repeated in the same batch,
and a re-sent copy of the pizza capture.

| Check (`npm run check -- L2`) | Expected |
|---|---|
| Import once | response = `expected/import-batch-1-first.json`; `/timeline` = `expected/timeline-after-batch-1.json` (6 purchases; still **one** pizza with 2 steps) |
| Import the same batch again | response = `expected/import-batch-1-second.json` (`added: 0`); `/timeline` and `/transactions` unchanged |

With the simulator running you can also try it by hand: `npm run import -- data/batch-1.json` (twice!).

---

## Level 3 card: "Trustworthy"

Import `data/batch-edge-cases.json` on top of the seed (`npm run check -- L3`). New rules:

1. **Validation.** An event is **rejected** (not stored, counted in a new `rejected` field of the import response) unless:
   `event_id`, `auth_id` and `merchant` are non-empty strings; `type` is `AUTHORISED`, `CAPTURED` or `REFUNDED`;
   `amount_paise` is a whole number greater than 0; `event_time` and `ingested_at` look like `YYYY-MM-DDTHH:MM:SSZ`.
   Check validity before duplicates. A body that is not a JSON array → HTTP **400**.
2. **Refund before the capture arrives.** Already handled if you order by `event_time`: QuickMart's capture arrives
   an hour after its refund but happened the night before it.
3. **Partial refund.** Add `refunded_paise` (sum of `REFUNDED` amounts) to every purchase. Status becomes
   `Partially refunded` when `0 < refunded_paise < captured total`; `Refunded` when `refunded_paise >= captured total`
   (or there is no capture). Every Level 1 status stays the same.
4. **Unknown `auth_id`.** A purchase with no `AUTHORISED` step (we never saw the hold) gets `"flags": ["NO_AUTHORISATION"]`.
   Every purchase has a `flags` list (empty when there is nothing to flag).

Expected: `expected/import-edge-cases.json` (`received 10, added 7, duplicates 0, rejected 3`) and
`expected/timeline-after-edge-cases.json`.

Also at this level:
- **A test proving import is idempotent:** import a batch, snapshot `/transactions` and `/timeline`, import again, compare.
- Tests for every status and for the ordering rules (unit tests on the grouping function are cheap and fast).
- Tidy structure (for example the timeline logic in its own module) and a README section on how it works.

---

## Level 4 ideas: "Go further"
- **Plain-language explanation** per purchase: *"This is one purchase of Rs.799.00 at Pizza Palace: a hold on 3 Nov,
  settled on 5 Nov."* For refunds: *"...refunded in full on 6 Nov."* (Format amounts with `src/format.js`.)
- **A UI** that shows one line per purchase, with the steps when you expand it. Make `GET /` show the timeline.
- **Anomaly hints:** a hold older than 7 days that was never captured; a capture amount different from the hold;
  two purchases at the same merchant with the same amount within a minute ("did you mean to buy two?").
- **Persistence:** save imports to a JSON file so a restart keeps them (still no database).
