# Architecture (as-is)

```
Client --> Flask app.py (routes + error handler)
              |
              +--> services/policy.py   (lookup, pagination, coverage, premium)
              +--> services/claims.py   (filing, search, review/approve/reject)
              +--> services/fraud.py    (scoring)
              +--> services/payout.py   (payout calc + payment)
              +--> services/notify.py   (email - simulated, synchronous)
              +--> services/reports.py  (KPIs)
                         |
                      db.py --> claimsflow.db (SQLite file, created on first start)
```

## Things the previous team told us (unverified!)
- "It mostly works." 
- "Notifications are slow, a claim submission takes a second or two."
- "We never wrote tests, we tested by clicking around."
- "The DB is just SQLite for now - we always meant to move to something real."
- "Everything lives in one process; we deploy by copying the folder to a VM."
- "Adjusters keep telling us numbers look off."
