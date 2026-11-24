# The Open Slot

**Greenfield · any language (Node.js or Python suggested; Java welcome) · input: a JSON waitlist + a script of commands**

← [Back to the workshop hub](../README.md) · [Level cards](LEVELS.md) · [Agent guide](../AGENT_GUIDE.md) ·
**[Share your experience](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md)**

---

## SETUP (about 2 minutes)

**Prerequisites:** Git, Python **3.10+** (for the checker), plus the language you choose:
Node.js **18+**, Python 3.10+, or JDK 17+. See [PREREQUISITES.md](../PREREQUISITES.md). No packages to install.

```
git clone https://github.com/<you>/<your-copy>.git
cd <your-copy>/open-slot
```

**Smoke test** (checks that the checker runs on your machine):

| Windows | macOS / Linux |
|---|---|
| `python checker/check.py --compare examples/L1-01-first-accepts/expected.jsonl examples/L1-01-first-accepts/expected.jsonl` | `python3 checker/check.py --compare examples/L1-01-first-accepts/expected.jsonl examples/L1-01-first-accepts/expected.jsonl` |

Expected output: `PASS`

**Check your program against all examples** (once you have one):
```
python checker/check.py --cmd "node open_slot.js"        # or "python open_slot.py", "java Main.java", ...
```
It prints `PASS`/`FAIL` per example and the first event that differs. You can also compare by hand:
every example folder has `waitlist.json`, `script.txt` and the exact `expected.jsonl`.

### Common problems
- `python` not found: use `python3` (macOS/Linux) or `py` (Windows). If `python3` opens the Microsoft Store on Windows, use `python` or `py`.
- Quote your command: `--cmd "node open_slot.js"`.
- `java Main.java` needs JDK 17+ (single-file mode; no Maven or Gradle needed).
- Print **one JSON object per line** and nothing else on stdout (put debug output on stderr).

---

## The problem (30 seconds)

A clinic appointment slot opens up (someone cancelled). The clinic offers it to its **waitlist, one patient at a time**,
in the order they joined. If that patient declines (or does not answer in time), the next eligible patient gets the offer.
Once someone accepts, the slot is filled and nobody else is offered it.

The AI agent writes the code. You can add a UI or an API later, but your program must also run as the
command-line contract below, so the checker can verify it. **No real clocks or timers:** offers expire only when the
script says `expire`.

## Input 1: `waitlist.json`

```json
{
  "clinic": "Riverside Family Clinic",
  "patients": [
    {"id": "P1", "name": "Asha Raman", "joined_at": "2026-11-01T09:00:00Z", "appointment_type": "general", "booked": false}
  ]
}
```
- **Waitlist order** = `joined_at` ascending (the timestamps are all in this exact UTC format, so comparing them as text
  works). If two patients joined at the same time, the one that comes first **in the file** goes first.
  The file is not necessarily sorted.
- `booked: true` means the patient already has an appointment and is never offered a slot.

Seed waitlists for your own experiments are in [`waitlists/`](waitlists/).

## Input 2: `script.txt` (one command per line)

| Command | Meaning |
|---|---|
| `open_slot <slot_id> <appointment_type> <HH:MM>` | A slot opens (e.g. `open_slot S1 general 15:00`). |
| `accept <patient_id> <slot_id>` | The patient accepts the offer they hold for that slot. |
| `decline <patient_id> <slot_id>` | The patient declines the offer they hold for that slot. |
| `expire <slot_id>` | The pending offer for that slot runs out (the patient did not answer in time). |

Blank lines and lines starting with `#` are ignored. Words are separated by single spaces.

## The rules (Levels 1 and 2)

1. A patient is **eligible** for a slot when **all** of these hold:
   - their `appointment_type` equals the slot's type;
   - they are not booked (from the file, or because they accepted a slot earlier in the script);
   - they do not currently hold an active offer for **any** slot;
   - they have not already declined, or let expire, an offer **for this slot**.
2. **Offer pass.** After every command, go through the open slots in the order they were opened. For each slot that
   is not filled and has no active offer, offer it to the **first eligible patient in waitlist order** (event `offered`).
   If nobody is eligible, emit `no_eligible_patient` for that slot, but only once until the slot is offered again.
   A slot like that is not closed: it waits and is offered as soon as someone becomes eligible.
3. `accept`: the slot is **filled**, the patient is **booked**. `decline` / `expire`: the patient loses the offer and is
   never offered *that* slot again (they stay eligible for other slots).
4. The events caused by a command come first (e.g. `declined`), then the events of the offer pass that follows it.

## Output contract

```
<your command> waitlist.json script.txt
```
prints one JSON object per line to stdout, exit code 0:

```
{"event": "offered", "slot": "S1", "patient": "P1"}
{"event": "declined", "slot": "S1", "patient": "P1"}
{"event": "offered", "slot": "S1", "patient": "P3"}
{"event": "accepted", "slot": "S1", "patient": "P3"}
```

| Event | Fields |
|---|---|
| `offered`, `accepted`, `declined`, `expired` | `slot`, `patient` |
| `no_eligible_patient` | `slot` |
| *(Level 3)* `withdrawn`, `left`, `slot_cancelled`, `error` | see [LEVELS.md](LEVELS.md) |

Key order and spaces do not matter. Extra keys are allowed (for example a sequence number or timestamp at Level 4).

## Acceptance examples (all visible, no hidden tests)

| Example | What it shows |
|---|---|
| `L1-01-first-accepts` | The first eligible patient accepts. |
| `L1-02-decline-then-next` | Decline → offered to the next eligible patient (P2 is skipped: wrong type). |
| `L1-03-expire-skip-booked` | Expiry, a booked patient skipped, and nobody left: `no_eligible_patient`. |
| `L1-04-join-order-and-type` | The file is not in join order; a tie on `joined_at` is broken by file order. |
| `L1-05-one-slot-after-another` | Several slots, one at a time; a booked patient is not offered again. |
| `L2-*` | Level 2 (a second slot opens while an offer is pending). See [LEVELS.md](LEVELS.md). |
| `L3-*` | Level 3 (errors, patients leaving, cancelled slots). See [LEVELS.md](LEVELS.md). |

## Where this can go: the ladder

Nobody is expected to finish. Report the **highest level you reached**.

| Level | Goal | Done when |
|---|---|---|
| **1 Core** | Offer one slot to the waitlist one patient at a time: decline/expire → next; accept → filled. | `python checker/check.py --cmd "..." --level 1` shows 5/5 PASS. |
| **2 Extension** | *Opt-in card:* a second slot opens while the first offer is pending. See [LEVELS.md](LEVELS.md). | `--level 2` shows 3/3 PASS. |
| **3 Trustworthy** | Invariant tests (nobody holds two offers; no slot offered to two people at once; a filled slot is never offered again), errors, leaving and cancelling, an audit log. See [LEVELS.md](LEVELS.md). | `--level 3` shows 2/2 PASS, plus your own tests. |
| **4 Go further** | A small UI, an injectable clock with automatic expiry, concurrency safety, notifications. | |

## Short agent tips (full version: [AGENT_GUIDE.md](../AGENT_GUIDE.md))
- First prompt: give the agent this README and `examples/L1-02-decline-then-next`. Ask it to restate the eligibility rule and the offer pass in its own words before coding.
- Ask it to model the state explicitly (patients, slots, active offers) and to write the invariants as tests.
- Have it run `python checker/check.py --cmd "..."` itself and fix failures one example at a time.
- Trace one example by hand on paper: `L2-02` is short and full of surprises.

**When you stop:** [open an experience report](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md).
Tell us the highest level you reached and what stopped you.
