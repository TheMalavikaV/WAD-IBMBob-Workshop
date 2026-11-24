# Architecture (as-is)

```
browser / curl ──► server.js ──► src/app.js (routes, plain node:http)
                                    │
                                    ├─► src/store.js       in-memory list of raw events, seeded from data/seed-events.json
                                    ├─► src/format.js      Rs. formatting, dates
                                    └─► src/http-utils.js  sendJson / sendHtml / readJsonBody / escapeHtml
```

- **No dependencies, no build step, no database.** Data lives in memory; every restart reloads the seed.
- **Routes today:** `GET /health`, `GET /transactions` (raw events, arrival order), `GET /` (HTML list, one row per raw event).
- **`readJsonBody`** is already there for when you add a `POST` route.
- `createApp({ store })` takes an optional store, so tests can start the app with their own data
  (see `tests/helpers.js`: `startServer()` listens on a free port).

## Event schema (one raw event from the card network)

| Field | Type | Example | Notes |
|---|---|---|---|
| `event_id` | string | `EVT-0002` | unique per event. The network may send the same event again |
| `auth_id` | string | `AUTH-1001` | **same auth_id = same purchase** |
| `type` | string | `AUTHORISED` \| `CAPTURED` \| `REFUNDED` | a hold, the settlement, a refund |
| `merchant` | string | `Pizza Palace` | |
| `amount_paise` | integer | `79900` | 1 rupee = 100 paise, so this is Rs.799.00. Never a float |
| `event_time` | string | `2026-11-03T19:02:11Z` | when it happened (UTC) |
| `ingested_at` | string | `2026-11-03T19:02:12Z` | when the bank received it. Can be much later than `event_time` |

## Lifecycle of a card purchase (why the customer sees two lines)
1. **AUTHORISED**: the merchant puts a hold on the money (you pay at the counter).
2. **CAPTURED**: a day or two later the merchant settles the hold. Same `auth_id`, same amount.
3. *(sometimes)* **REFUNDED**: money goes back. Same `auth_id`.

The app today shows every raw event as its own line, so one pizza = two Rs.799 lines.
