# Verification record — generated in this delivery

## Task 6 backup and recovery · 21 November 2026

Python 3.12.14 and SQLite 3.53.1. The test suite ran locally against temporary databases with synthetic tickets.

`python -m unittest discover -s tests -v` passed **24/24** checks (11 existing and 13 recovery and ticket-failure checks). The command-line UC.1–UC.4 demonstration also passed.

| Injected condition | Observed product result |
|---|---|
| Newest checkpoint intact | All 11 checkpoint tickets and their complete event histories matched row for row. |
| Newest checkpoint unreadable | The older checkpoint restored all 10 tickets and 50 events. Ticket 11 was created after it. The operator saw the generation, UTC time and recovery-gap notice. One local service call took 2.4 ms on this fixture. |
| Both generations invalid | Restore reported no verified checkpoint. Current ticket and event rows remained identical. |
| Valid SQLite file altered after backup | Digest verification rejected it and recovery selected the preceding generation. |
| Live database missing | After normal app initialization, IT Support restored the checkpoint into the fresh database. |
| Event insert failure and lost acknowledgement | The failed write left zero tickets and events. Replaying a committed request left one ticket and one submission event. |

The standard-library HTTP handler was exercised from GET through POST and redirect, including the required restore confirmation. Streamlit was syntax-checked locally. The timing above is one observation on synthetic data.

## Original demonstration baseline tests

Command:

```bash
python -m unittest discover -s tests -v
```

Observed result in the delivery environment:

- 11 tests run
- 11 passed
- 0 failures
- 0 errors

Covered checks include missing-information handling, no ticket before complete confirmed submission, SQLite persistence, duplicate-safe retry, manager-only assignment, resident/technician RBAC, UC.1–UC.4 close/reopen path, blocked-work return, 71:59 vs 72:00 manager exception boundary, aggregate-only Administration view, emergency boundary/fallback, and SQLite backup.

## Command-line end-to-end demonstration

Command:

```bash
python demo_scenario.py
```

Observed sequence:

1. Resident structured draft generated.
2. Committed ticket `DORMFIX-0001` created in `Submitted`.
3. Manager assigned `tech.taylor` and state became `Assigned`.
4. Technician progress/completion moved state to `Awaiting resident confirmation`.
5. Resident confirmed resolution and state became `Closed`.
6. Audit history contained 11 events.

Result printed: `PASS: UC.1–UC.4 demonstration completed.`

## Zero-dependency web verification

Because the execution environment did not have Streamlit installed and could not reach the public internet to install it, `webapp.py` was added as a standard-library fallback.

Verified locally in the delivery environment:

- Resident page: HTTP 200
- Manager page: HTTP 200
- Administration page: HTTP 200
- Resident web form created `DORMFIX-0001`
- Manager web page subsequently displayed `DORMFIX-0001`
- Manager pending decision count displayed `1`

Run locally with:

```bash
python webapp.py --port 8502
```

Then open `http://127.0.0.1:8502`.

## Streamlit / FastAPI verification boundary

The code for `app.py` (Streamlit) and `api.py` (FastAPI) was syntax-compiled successfully, but the delivery environment does not have the third-party packages installed. Therefore this record does **not** claim that Streamlit/FastAPI were started here. Install `requirements.txt` on a normal local environment, then use the README commands.

The zero-dependency web UI was added specifically so the delivered website has an actually executed local path independent of package installation.
