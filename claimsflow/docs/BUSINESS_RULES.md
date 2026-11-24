# ClaimsFlow Business Rules (source of truth)

## Policies
- Types: `AUTO`, `HEALTH`, `HOME`. Status: `ACTIVE`, `EXPIRED`, `CANCELLED`.
- A policy covers an incident if it is **not cancelled** and the incident date is within
  `[start_date, end_date]` - **both ends inclusive**.
- List endpoints are paginated with **1-based** pages.

## Premium quote
`premium = base_rate x (coverage_limit / 1000) x age_factor`, then x 0.95 if deductible >= 1000, rounded to 2 decimals.

| Policy type | base rate per 1,000 of coverage |
|-------------|-------------------------------|
| AUTO | 24 |
| HEALTH | 15 |
| HOME | 6 |

Age factor, using the holder's **exact age in whole years** on the quote date:
under 25 -> 1.5; 25 to 59 -> 1.0; **60 and over -> 1.3**.

## Filing a claim
- Required: policy, claimant, amount, incident date, description.
- Amount must be **greater than zero**.
- Incident date must be inside the policy coverage period and **not in the future** (relative to the filing date).
- A claim must be filed **within 30 days (inclusive)** of the incident.
- Every new claim is fraud-scored. Score >= 70 -> `UNDER_REVIEW`, otherwise `SUBMITTED`.

## Fraud scoring (additive)
| Rule | Points |
|------|--------|
| Claim amount > 80% of coverage limit | +30 |
| Incident less than 30 days after policy start | +40 |
| **Another** claim on the same policy, same incident date, amount within 5% | +50 |

## Payout
`payout = max(0, min(claim_amount - deductible, coverage_limit))`

## Claim lifecycle
```
SUBMITTED --> UNDER_REVIEW --> APPROVED --> PAID
    |              |
    +--> REJECTED <+
```
- Only `SUBMITTED` / `UNDER_REVIEW` claims can be approved or rejected.
- Approved amount can never exceed the claimed amount.
- Only `APPROVED` claims can be paid, and **a claim can be paid at most once**.

## Notifications
- Claim received / paid -> email to the policy holder and the adjuster mailbox - **never to other customers**.

## Reporting
- Loss ratio = total paid / total premium of ACTIVE policies x 100 (0 when there is no premium).

## Non-functional expectations
- No secrets in source control. No stack traces or internal details in API responses.
- All SQL must be parameterised.
