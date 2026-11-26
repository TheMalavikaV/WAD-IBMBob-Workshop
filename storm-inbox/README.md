# The Storm Inbox (beginner track)

**Brownfield · beginner-friendly · Node.js 22+ · no dependencies · about 150 lines of app code**

← [Back to the workshop hub](../README.md) · [Level cards](LEVELS.md) · [Agent guide](../AGENT_GUIDE.md) ·
**[Share your experience](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md)**

New to coding agents? Start here. The app is small, the story is concrete, and every step has a suggested prompt
(at the bottom of this page).

---

## SETUP (about 2 minutes)

**Prerequisites:** Git and Node.js **22 or newer** (see [PREREQUISITES.md](../PREREQUISITES.md)). There is nothing to
`npm install`: the starter uses only Node's standard library.

```
git clone https://github.com/<you>/<your-copy>.git
cd <your-copy>/storm-inbox
```

The commands are the same on Windows, macOS and Linux:

| What | Command | Expected |
|---|---|---|
| Smoke test (the 5 baseline tests) | `npm test` | `# pass 5`, `# fail 0` |
| Start the app | `npm start` | `Storm Inbox at http://127.0.0.1:7991` |

Then open **http://127.0.0.1:7991** in a browser: that is Divya's claims register. Stop the app with **Ctrl+C**.

### Common problems
- **`node --version` is below v22:** install the current LTS (see PREREQUISITES.md; on Linux use `nvm install --lts`).
- **`npm.ps1 cannot be loaded`** (Windows PowerShell): run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use `npm.cmd test` / `npm.cmd start`.
- **Port 7991 in use:** stop the other program, or pick another port. macOS/Linux: `PORT=3000 npm start`.
  Windows PowerShell: `$env:PORT=3000; npm start`. Windows cmd: `set PORT=3000 && npm start`.
- **The page says "Unable to load claims":** the server is not running (or runs on another port). Start it with `npm start`.

---

## The story (30 seconds)

At 9:15 on a rainy Bengaluru morning, Divya has twelve property damage claims on her screen and two field adjusters
available. A family in JP Nagar reported a leaking bedroom roof at 8:10. Their claim is missing a photo. Another family
in Koramangala reported roof damage at 9:00 and has already sent everything Divya needs.

> "I can send someone to Koramangala now. But when the JP Nagar photo comes in, I need to remember that family called
> first. Right now the only place I track that is my spreadsheet."

You're an engineer at **MonsoonSure Insurance**. Divya supervises the claims desk. The family filing a claim is the
**claimant**. The **assigned adjuster** is the employee who investigates the damage and follows up with the family.
**Your assignment is to add dispatch to the existing claims register** so Divya can see which claim comes next, give it
to someone with room, and respond when the morning changes.

## Look at the desk Divya starts with

| What you see | What it means |
| --- | --- |
| Meera Rao and Ravi Kumar each show **1 of 2 active claims** | Each adjuster is already handling one family's claim and can take one more. |
| **Assigned** shows 2 claims | Open CLM-006 to see Meera listed as the assigned adjuster. Ravi is handling CLM-005. |
| **Awaiting documents** shows 3 claims | Open CLM-003. The family filed at 08:10 and the roof photo is still missing. |
| **Unassigned** shows 7 claims | These families have supplied all required documents. Their claims are waiting for an adjuster. |

**What is missing today?** Select **Unassigned**. The first row is CLM-001, a Standard claim for water damage to a floor.
Farther down are two High claims, CLM-008 and CLM-009. Divya can inspect all three, but the register leaves her to work
out which family should get the next available slot. Once she decides, there's no action to record the assignment. If
a photo arrives or an adjuster becomes unavailable, she has to revise her spreadsheet again.

Extend this dashboard. **Keep the existing register, status filter and clickable claim details working.**

## Level 1: show Divya which claim comes next

Build a **Ready** queue for claims with no assigned adjuster and every required document received. Show incomplete,
unassigned claims under **Waiting for documents** and list each missing item. A claim with an assigned adjuster stays
with that person.

Order Ready claims by severity (**High**, **Standard**, **Low**), then by original filing time (oldest first), then by
claim ID (ascending). Display the severity and filing time beside the ID so Divya can explain her decision.

**Expected on the original desk** (all visible, no hidden tests):

| List | Expected |
|---|---|
| Ready, in order | **CLM-008**, CLM-009, CLM-001, CLM-004, CLM-010, CLM-007, CLM-012 (7 claims) |
| Waiting for documents | CLM-002 (Roof photo, Repair estimate), CLM-003 (Roof photo), CLM-011 (Damage photo) |
| Assigned | CLM-005 (Ravi), CLM-006 (Meera) |

CLM-008 leads: CLM-009 has the same severity and 09:00 filing time, so the smaller ID decides. CLM-003 is older than
both and stays in Waiting until its roof photo arrives.

## Where this can go: the ladder

Nobody is expected to finish. Report the **highest level you reached**.

| Level | Goal | Done when |
|---|---|---|
| **1 Core** | The **Ready** queue and **Waiting for documents** list above. | The UI shows the expected lists in the expected order; a test checks the order, including the 09:00 tie; the 5 original tests still pass. |
| **2 Extension** | *Opt-in card:* assign a Ready claim to an adjuster, with the server checking capacity. See [LEVELS.md](LEVELS.md). | The checks on the card pass, including "two requests for the last slot: exactly one succeeds". |
| **3 Trustworthy** | *Card:* handle the mid-morning storm update; refresh and replay change nothing; a test for every rule. See [LEVELS.md](LEVELS.md). | The full demonstration on the card works from two browser tabs; `npm test` is green. |
| **4 Go further** | Undo an assignment, an activity log, a "why is this next?" explanation, automatic suggestions. See [LEVELS.md](LEVELS.md). | |

A GitHub Actions workflow (`.github/workflows/storm-inbox-tests.yml`) runs `npm test` on every push.

## Where to look

| File | What you'll find |
| --- | --- |
| `data/desk.json` | Starting claims, documents, adjusters and workloads inferred from assignments |
| `public/claims.js` | Existing rules for missing documents, status and filtering |
| `public/app.js` | The roster, selectable claim rows and details panel |
| `public/index.html` and `public/styles.css` | The dashboard layout and styles |
| `server.mjs` | The local server and its read-only starting API |
| `fixtures/storm-update.json` | The document arrival and Meera's availability change (Level 3) |
| `test/desk.test.js` | The five baseline tests |

## Suggested prompts (paste one at a time)

If you're new to coding agents, paste **one prompt at a time** into the same conversation. Check the result in the app
or tests before moving on. (General tips: [AGENT_GUIDE.md](../AGENT_GUIDE.md).)

**1. Understand Divya's desk** *(before Level 1)*
```text
Read this README and run the baseline tests. Trace CLM-003 from data/desk.json to its document list on screen. Explain what "1 of 2 active claims" means for Meera and show me where the existing app decides a claim's status. Stop before editing.
```

**2. Plan the change** *(before Level 1)*
```text
Plan the Level 1 change in this README using the existing dashboard. Identify what we can reuse and which new function decides the Ready order. Give me a short implementation and test plan to review. Do not edit yet.
```

**3. Build and check the queue** *(Level 1)*
```text
Implement Level 1. Preserve claim selection, details and filters. Add tests for missing documents, severity, original filing time and the 09:00 tie. Run the tests and tell me where to look in the UI to verify why CLM-008 leads and CLM-003 waits.
```

**4. Add assignment and capacity checks** *(Level 2: read LEVELS.md first)*
```text
Read the Level 2 card in LEVELS.md and implement it from the dashboard through the server. Test a successful assignment and rejected requests for an incomplete claim, an already assigned claim, an unavailable adjuster and a full adjuster. Send two competing requests for Ravi's last slot and verify only one succeeds. Run the tests and show me how to inspect the resulting workload.
```

**5. Apply the storm update** *(Level 3)*
```text
Read the Level 3 card in LEVELS.md and the supplied events, then implement them. Test CLM-003 moving into Ready at its original filing time and Meera keeping CLM-006 when she becomes unavailable. Cover a request from an older tab and replay after assigning CLM-003 to Ravi. Run the tests and explain how I can verify the result after refreshing.
```

**6. Rehearse the demonstration** *(Level 3)*
```text
Review our changes against the demonstration in LEVELS.md. Run the full test suite. Identify and fix any missed requirement, then give me a short two-tab demo checklist starting from the original twelve claims. Ask me to explain why CLM-003 moved and why CLM-006 stayed with Meera.
```

**When you stop:** [open an experience report](https://github.com/YOUR-ORG/YOUR-REPO/issues/new?template=experience-report.md).
Tell us the highest level you reached and what stopped you.
