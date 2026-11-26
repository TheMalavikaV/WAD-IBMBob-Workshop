# The Storm Inbox: level cards

Report the highest level you reached, not whether you "finished". The cards are **opt-in**: pick one up when you are
ready. Each one builds on the level before it; nothing from Level 1 changes.

---

## Level 2 card: "Give it to someone with room"

**Ready for a harder requirement?**

Let Divya select a **Ready** claim and an **available** adjuster with room. Each adjuster can handle **two active
claims**, counting the ones they already have. After a successful assignment, remove the claim from Ready, show its
assigned adjuster in the details, and update that adjuster's workload ("2 of 2 active claims").

Two browser tabs share one desk. When an assignment arrives, the **server** must check:

| Check | Decline when |
|---|---|
| Documents | the claim still has missing documents |
| Current assignment | the claim already has an assigned adjuster |
| Availability | the adjuster is unavailable |
| Capacity | the adjuster already has 2 active claims |

If the desk has changed, decline the request, **explain why**, and bring the tab up to date.
If two requests compete for the last slot, **exactly one succeeds** and the other claim stays Ready.

Keep accepted changes when Divya refreshes the page. Keeping state in a single running server process is enough
(a restart may reset the desk to the seed).

**Done when** (start from the original desk, restart the server first):
1. Assign CLM-008 to Ravi → Ready shows 6 claims led by CLM-009; Ravi shows **2 of 2**; CLM-008's details show Ravi.
2. Try to assign CLM-009 to Ravi → declined ("Ravi has no room" or similar), CLM-009 stays Ready.
3. Try to assign CLM-003 (missing photo) or CLM-005 (already Ravi's) to Meera → declined with a reason.
4. In a fresh desk, send two requests at the same time giving Ravi two different Ready claims → exactly one succeeds.
   (A test is the easiest way to prove this; clicking fast is not proof.)
5. Refresh the page → the assignment is still there.

---

## Level 3 card: "The morning changes" (trustworthy)

Add a **Load storm update** action that applies the two events in [`fixtures/storm-update.json`](fixtures/storm-update.json).

| Time | What happens | What Divya should see |
| --- | --- | --- |
| 10:30 | The JP Nagar family sends the missing roof photo for CLM-003. | The claim moves into Ready with its original 08:10 filing time. On the starting desk it moves ahead of CLM-008. |
| 10:35 | Meera calls from a site visit. She can finish the claim she's handling and cannot take another. | Meera becomes unavailable for new assignments. CLM-006 still lists Meera as its assigned adjuster and shows **Owner unavailable**. Other existing assignments stay intact. |

Rules:
- Keep accepted changes when Divya refreshes the page.
- **Replaying** the file must leave the same queue, photo list, workloads and assignments (the photo is listed once,
  not twice; nobody is unassigned).
- A tab that loaded the desk before the update must not be able to sneak in a stale assignment: the server decides.

**The demonstration** (start the server fresh; open the desk in **two tabs**):
1. Show seven Ready claims, explain why CLM-008 precedes CLM-009, and find both missing documents for CLM-002 in Waiting.
2. Load the storm update in the first tab **before making any new assignment**. Show eight Ready claims with CLM-003
   first. Open CLM-006 and show who is still handling it.
3. From the older (second) tab, try to assign CLM-008 to Meera. Show the rejection and the updated desk. Then assign
   CLM-003 to Ravi. His workload should reach two, and CLM-008 should return to the top.
4. Refresh and replay the update. Show **seven ready, two waiting and three assigned**. CLM-003 has one roof photo and
   stays with Ravi. CLM-006 stays with Meera.
5. Run the original and new tests. Cover priority ties, missing documents, assignment checks, two requests for one slot,
   the storm update and replay. Walk through one test and one decision your team made with the agent.

**Done when:** all five steps work, and `npm test` is green (the 5 original tests plus yours).

---

## Level 4 ideas: "Go further"
- **Undo / reassign:** Divya assigned the wrong person. Let her move a claim back to Ready (and decide what happens to
  the order).
- **Activity log:** every assignment, decline, document arrival and availability change, with time and who did it.
- **"Why is this next?"** A one-line explanation beside the top Ready claim (*"High severity, filed 08:10, oldest High claim"*).
- **Suggest an adjuster:** pre-select the available adjuster with the most room.
- **Live updates:** the second tab refreshes itself when the desk changes (polling is fine; no extra libraries needed).
- **Persistence to disk:** keep the desk in a JSON file so a restart keeps it, with a documented way to restore the seed.
