# Working with the agent: one page

You have about **50 coins** (roughly a few dozen agent turns) and **about 50 minutes of build time**.
Coins go fastest when the agent is guessing, re-reading big files, or fixing things it broke a minute ago.

## 1. Plan before code (about 10 coins)
- In your **first prompt**, give the agent the full brief: paste or point it to the problem README,
  `LEVELS.md` if you take a card, and the acceptance examples.
- Ask it to **restate the spec in its own words and list its questions** before it writes code.
  Answer the questions. This is the cheapest bug-fixing you will ever do.
- Put all requirements in the first prompt. One complete prompt beats ten small "oh, and also..." prompts.

## 2. Tests first
- Ask the agent to turn the acceptance examples into **automated tests before** it writes the solution.
- For brownfield problems: ask for a test that **fails on the current code** before it fixes anything.
  A fix without a failing test first is a guess.

## 3. Let the agent run things
- Tell it the exact commands (`python -m unittest`, `npm test`, `python checker/check.py ...`) and ask it to
  **run them and fix failures itself** until everything is green.
- Ask it to show you the test output, not just tell you "all tests pass".

## 4. Point, do not paste
- Refer to files by path ("read `docs/BUSINESS_RULES.md`") instead of pasting large files into the chat.

## 5. Verify one result yourself
- Pick one example and check it **by hand** (a calculator, a spreadsheet, reading 10 rows).
  The agent is confident even when it is wrong. Your experience report asks how you knew it was right.

## 6. Steer, do not just accept
- Read the diff. Ask "why?" when something looks odd. Ask it to keep changes small.
- If it goes in circles twice, stop it, say what you observed, and give it a narrower task.

## Suggested coin split (of 50)

| Phase | Coins |
|---|---|
| Planning and first build | ~10 |
| Iteration and fixes | ~25 |
| Extras, edge cases, next level | ~10 |
| Wrap-up (README, tidy, summary of what was done) | ~5 |

## Suggested timeline

| Minutes | What |
|---|---|
| 5 | Read the brief and plan (with the agent) |
| 40 | Build, test, climb the ladder |
| 10 | Try it end to end, verify a result yourself, prepare to share |

## Keep notes as you go (for the experience report)
Write down: the prompt that worked best, the moment the agent went wrong, how you checked correctness,
and your coin count at each level. The report form is linked from every problem README.
