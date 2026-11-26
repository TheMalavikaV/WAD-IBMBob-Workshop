# Build It With an Agent: a hands-on AI coding-agent workshop

> **1.5 hours · work in teams · about 50 agent coins per team · pick ONE problem**

This is a **workshop, not a competition**. Nobody is scored or judged. Your team picks one problem
and uses an AI coding agent as the **builder**. You steer, review and verify. At the end you share what
worked, where the agent went wrong, and how you knew the result was right.

The software you build does not need any AI inside it. The agent is your tool, not your product.

---

## Before the workshop (10 minutes, please do this at home)

1. Install the tools in **[PREREQUISITES.md](PREREQUISITES.md)** (Git, Python 3.10+, Node.js 18+).
2. Clone this repo and run the setup checker:
   ```
   git clone https://github.com/YOUR-ORG/YOUR-REPO.git
   cd YOUR-REPO
   python check-setup/check_setup.py
   ```
   On macOS/Linux use `python3` if `python` is not found. On Windows try `py` if `python` is not found.
   You should see `ALL GOOD` at the end.
3. Read **[AGENT_GUIDE.md](AGENT_GUIDE.md)** (one page). It will save you coins.

---

## The menu: pick ONE problem

Every problem is understandable in 30 seconds and runs on your laptop with one command. No Docker, no databases to install.

| Problem | Type | Language | The 30-second version |
|---|---|---|---|
| **[ClaimsFlow](claimsflow/)** | Brownfield | Python (Flask + SQLite) | An insurance claims app with no tests is paying claims wrongly and paying some twice. Take it over with an agent and make it trustworthy. |
| **[The Open Slot](open-slot/)** | Greenfield | Your choice (Node.js or Python suggested) | A clinic appointment opens up. Offer it to the waitlist one patient at a time, without ever double-offering. |

**How to choose:**
- Want to work with *existing* code (the most common day job)? Pick **ClaimsFlow** (brownfield, Python).
- Want to see how well the agent builds something *from a spec*? Pick **The Open Slot** (greenfield, any language).
  Inputs are JSON/text files, expected outputs are files, and a checker tells you PASS/FAIL.

## Every problem is a ladder. Nobody is expected to reach the top.

| Level | What it means |
|---|---|
| **1 - Core** | The basic working version, describable in one sentence. |
| **2 - Extension** *(opt-in card)* | An extra requirement in the problem's `LEVELS.md`. Pick it up when you are ready. It builds on Level 1; it never throws your work away. |
| **3 - Trustworthy** | Tests, edge cases, error handling, a clean README and structure. |
| **4 - Go further** | Open-ended stretch ideas. |

When you report back, tell us **the highest level you reached** and what stopped you. "Did you finish?" is not the question.

---

## How to get your own copy (template repo)

1. On this repo's GitHub page, click **Use this template → Create a new repository**.
2. Make it yours (public or private, under your own account), then clone *your* copy:
   ```
   git clone https://github.com/<you>/<your-copy>.git
   ```
3. Work only in the folder of the problem you picked. Commit as often as you like.

You do **not** open pull requests against this repo. Your copy is your sandbox.

If GitHub is not available to you, `git clone` this repo directly and work locally. That is fine too.

## Suggested 90-minute timeline

| Time | What |
|---|---|
| 0-10 min | Intro, pick a problem, run the problem's smoke test |
| 10-15 min | Read the brief, write the first prompt (plan first, see [AGENT_GUIDE.md](AGENT_GUIDE.md)) |
| 15-65 min | Build with the agent, climb the ladder |
| 65-75 min | Try it, verify one result yourself, fill in the experience report |
| 75-90 min | Debrief: a few teams share one win and one failure |

## Share your experience (this is the most important part)

When you are done, open an **experience report** issue. It has six short questions and takes about 5 minutes:

**→ [Open an experience report](https://github.com/TheMalavikaV/WAD-IBMBob-Workshop/issues/new?template=experience-report.md)**

Please file it on **this** repo (the link above), not on your template copy.

---

## What is in this repo

```
README.md               <- you are here
PREREQUISITES.md        install Git / Python / Node (Windows, macOS, Linux)
AGENT_GUIDE.md          one page of tips for working with the agent
check-setup/            python check-setup/check_setup.py
claimsflow/             problem 1 (brownfield, Python)
open-slot/              problem 2 (greenfield, any language)
.github/                experience-report issue template, CI for ClaimsFlow
```
