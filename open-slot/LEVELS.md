# The Open Slot: level cards

Report the highest level you reached, not whether you "finished". The cards are **opt-in**: pick one up when you are ready.
Each one adds to the rules in the README. Nothing from the level before it changes.

---

## Level 2 card: "Two slots, one patient"

**Ready for a harder requirement?**

Monday morning: two people cancel within minutes of each other. A second slot opens **while the first offer is still
pending**. The clinic wants **both slots filled**, and **nobody may ever hold two active offers at once** (patients find
that confusing and it blocks the waitlist).

The rules in the README already cover this, so read them again with several open slots in mind:
- "does not currently hold an active offer for **any** slot" means the second slot skips whoever holds the first offer;
- the offer pass goes through **all** open slots in the order they were opened, after **every** command;
- a slot with nobody eligible **waits** (`no_eligible_patient`) and is offered as soon as a patient becomes free
  (for example after declining a *different* slot).

Examples:

| Example | What it shows |
|---|---|
| `L2-01-second-slot-while-pending` | S2 skips P1 (who holds the S1 offer) and goes to P3. After P1 declines S1, S1 skips P3 (now booked) and goes to P5. |
| `L2-02-freed-patient-takes-waiting-slot` | Three slots, two patients. Q1 declines S1 and is immediately offered the waiting S3. Trace it by hand! |
| `L2-03-busy-morning` | Two appointment types, overlapping offers, a slot that ends up waiting. |

**Done when:** `python checker/check.py --cmd "..." --level 2` shows 3/3 PASS **and** your own test checks, after every
command, that no patient holds two active offers and no slot has two.

---

## Level 3 card: "Trustworthy"

New commands:

| Command | Effect | Events (in this order) |
|---|---|---|
| `cancel_slot <slot_id>` | The clinic withdraws a slot that is **not filled**. A pending offer on it is withdrawn. The slot is never offered again. | `withdrawn` (slot, patient) if there was an offer, then `slot_cancelled` (slot) |
| `leave <patient_id>` | The patient leaves the waitlist and is never offered anything again. A pending offer they hold is withdrawn (then the offer pass re-offers that slot). | `withdrawn` (slot, patient) if they held an offer, then `left` (patient) |

**Errors.** A command that cannot be applied changes nothing and produces
`{"event": "error", "line": <line number in script.txt, counting from 1, including comments and blank lines>, "reason": "<reason>"}`.
The program keeps going with the next line. Check in this order and report the first reason that applies:

| Reason | When |
|---|---|
| `unknown_command` | the first word is not a known command |
| `bad_arguments` | wrong number of words, or `open_slot` time not in `HH:MM` form (two digits, colon, two digits) |
| `duplicate_slot` | `open_slot` with a slot id that was already used |
| `unknown_slot` | `accept`/`decline`/`expire`/`cancel_slot` for a slot that was never opened |
| `unknown_patient` | `accept`/`decline`/`leave` for a patient not in the waitlist |
| `no_active_offer` | `accept`/`decline` by a patient who does not hold the active offer for that slot; `expire` on a slot with no active offer |
| `slot_not_open` | `cancel_slot` on a slot that is filled or already cancelled |
| `patient_not_waiting` | `leave` for a patient who already left |

(For `accept`/`decline`, check `unknown_slot` before `unknown_patient`.)

Examples: `L3-01-errors`, `L3-02-leave-and-cancel`.

Also at this level:
- **Invariant tests** that run after every command: nobody holds two active offers; no slot has more than one;
  a filled or cancelled slot has no offer; a booked or departed patient holds no offer.
- **Audit log:** the event stream *is* an audit log. Make it useful: add a sequence number to each event (extra keys are
  allowed by the checker), or write it to a file as well.
- A missing or unreadable input file → a clear message on stderr and a non-zero exit code.
- A README explaining how to run your program and your tests.

**Done when:** `--level 3` shows 2/2 PASS and your invariant tests are green.

---

## Level 4 ideas: "Go further"
- **Injectable clock:** instead of `expire`, add `advance <minutes>` and an offer lifetime (e.g. 30 minutes) passed in
  on the command line. Offers expire automatically when simulated time passes them. Still no real timers.
- **A small UI or HTTP API** for the front desk: open a slot, see who holds which offer, accept/decline on a patient's behalf.
- **Concurrency safety:** two receptionists press "open slot" at the same moment. Prove nobody gets two offers.
- **Notifications:** print (or log) the SMS a patient would get for each offer, with a reply-by time.
- **Priority rules:** urgent patients first, then join order. Write down the rule before you code it.
