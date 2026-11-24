# API Contract

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/policies?status=&page=&page_size=` | List policies (1-based pages) |
| GET | `/policies/{id}` | Policy detail |
| POST | `/quotes` | Body: `policy_type, dob, coverage_limit, deductible` -> `{premium}` |
| GET | `/claims?status=` / `?q=text` | List or search claims (claimant / description) |
| POST | `/claims` | Body: `policy_id, claimant, amount, incident_date, description` -> 201 claim |
| GET | `/claims/{id}` | Claim detail |
| POST | `/claims/{id}/review` | Move claim to UNDER_REVIEW |
| POST | `/claims/{id}/approve` | Optional body `approved_amount` |
| POST | `/claims/{id}/reject` | Optional body `reason` |
| POST | `/claims/{id}/pay` | Pay an approved claim |
| GET | `/reports/summary` | KPIs: claims by status, totals, loss ratio |

Dates are ISO `YYYY-MM-DD`. Errors: `400` validation/conflict, `404` not found, `500` unexpected.

## Quick tour

macOS/Linux shell shown. In Windows PowerShell use `curl.exe` instead of `curl` (or `Invoke-RestMethod`),
and put the JSON body in a file (`-d @body.json`) to avoid quoting problems. GET URLs also work in a browser.

The API uses **today** as the filing date, so pick an `incident_date` within the last 30 days
and inside the policy's coverage period (POL-1001 covers 2026-01-01 to 2026-12-31).

```bash
curl localhost:5001/policies?page=1\&page_size=3
curl -X POST localhost:5001/quotes -H 'content-type: application/json' \
  -d '{"policy_type":"AUTO","dob":"1990-01-01","coverage_limit":50000,"deductible":500}'
curl -X POST localhost:5001/claims -H 'content-type: application/json' \
  -d '{"policy_id":"POL-1001","claimant":"Asha Raman","amount":1500,"incident_date":"2026-11-10","description":"Parking lot scrape"}'
curl localhost:5001/reports/summary
```
