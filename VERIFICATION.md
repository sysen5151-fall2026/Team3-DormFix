# Verification record — generated in this delivery

## Automated service-layer tests

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
