# DormFix class demonstration script

## 1. Start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Optional API in a second terminal:

```bash
uvicorn api:app --reload --port 8000
```

## 2. UC.1 — Resident Requests Maintenance

1. Choose **Alex Resident** in the sidebar.
2. Enter: `The kitchen sink is leaking under the cabinet.`
3. Enter Building `Demo Hall`, Room `101`, Access `Weekdays after 3 PM`.
4. Click **Prepare structured draft**.
5. Point out that the draft is editable and that no ticket exists yet.
6. Check the explicit confirmation box and submit.
7. Record the returned `DORMFIX-xxxx` ID.

Optional failure demonstration: enter `There is a gas leak in my room` and show the non-emergency warning. With no `DORMFIX_LLM_URL`, show the explicit fallback message rather than claiming a live AI call.

## 3. UC.2 — Property Manager Reviews and Assigns

1. Switch to **Morgan Manager**.
2. Show the pending decision count.
3. Select the new ticket and verify description, building, room, category, access and audit history.
4. Select priority and **Taylor Technician**; assign.
5. Point out that AI never sets priority or assignment.

## 4. UC.3 — Technician Performs Maintenance

1. Switch to **Taylor Technician**.
2. Show only assigned work.
3. Enter a progress note and click **Start / update progress**.
4. Enter `Replaced leaking supply line` and click **Mark work complete**.
5. Show status becomes **Awaiting resident confirmation**, not Closed.

Optional alternate path: use **Return to manager** with a required reason, or propose a new access arrangement.

## 5. UC.4 — Resident Confirms Resolution

1. Switch back to **Alex Resident**.
2. Open the ticket.
3. Show current stage, assigned technician, latest update, next step, and audit history.
4. Click **Confirm resolved and close**.
5. Optionally use **Reopen closed ticket** with a reason and show the same ticket ID/history is preserved.

## 6. Oversight and operations

- Switch to **Housing Administration**: show aggregates only, not ticket personal data.
- Switch to **IT Support**: show diagnostics and create a SQLite backup; demonstrate account/role maintenance without exposing ordinary ticket details.

## 7. Verification

```bash
python demo_scenario.py
python -m unittest discover -s tests -v
```

End by opening `docs/TRACEABILITY.md` and explicitly distinguishing implemented demo behavior from deferred or validation-only requirements.
