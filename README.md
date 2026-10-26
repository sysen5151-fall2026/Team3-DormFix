# DormFix — integrated demonstration prototype

**Cornell SYSEN 5151 / SYSEN 5930 · Team 3**

DormFix is a role-based student-housing maintenance and collaboration prototype for **routine, non-emergency** maintenance. This build extends the original Chapter 2 walking skeleton into a locally runnable demonstration while preserving the project boundaries and explicitly separating implemented behavior from deferred validation work.

## What is actually implemented

- Resident assisted intake with missing-field detection, editable structured draft, explicit confirmation and manual fallback.
- Optional configurable OpenAI-compatible local LLM call (for example LM Studio); AI is advisory only.
- SQLite persistence, committed ticket IDs, idempotent submission retry, ordered audit history.
- Property-manager pending/open work views, priority selection and technician assignment.
- Assigned-technician job view, progress notes, completion, blocked-work return and access-change proposal.
- Resident status tracking, close after technician completion, and reopen while preserving the same ticket/history.
- Six lifecycle states from the baseline: Submitted, Assigned, In progress, Awaiting resident confirmation, Closed, Reopened.
- Role-based access: resident own tickets; technician assigned tickets; manager all tickets; Administration aggregates only; ordinary IT Support diagnostics/operations only.
- 72-hour manager no-response exception closure.
- Administration aggregate summary, IT diagnostics, account/role maintenance and database backup.
- FastAPI endpoints for the core operational path plus a Streamlit class-demo UI.
- Automated tests and an end-to-end command-line demo.

## Not claimed

This is **not** a production housing service. The demo identity selector is not production authentication. Human usability percentages, the full 30–50 synthetic-scenario campaign, production security/deployment, advanced grouped trends, emergency dispatch, purchasing, billing, rent integration, and offline synchronization are not claimed as completed. See `docs/TRACEABILITY.md`.

## Quick start

Python 3.12 is recommended.

### Guaranteed zero-dependency web demo

This path uses only the Python standard library and was actually started and exercised during delivery:

```bash
python webapp.py --port 8502
```

Open `http://127.0.0.1:8502`. It supports the core resident → manager → technician → resident workflow and role-specific views.

### Preferred Streamlit UI

The course-documented stack remains the preferred presentation UI. Install dependencies, then start it:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

The app initializes `data/dormfix.db` and seeds demo identities.

### Optional API

```bash
uvicorn api:app --reload --port 8000
```

API calls use `X-DormFix-Actor` as a **demo identity header**, not production authentication.

### Optional local LLM

Copy `.env.example` values into your shell/environment. Set `DORMFIX_LLM_URL` to an OpenAI-compatible chat-completions endpoint. Example LM Studio-style value may look like:

```bash
export DORMFIX_LLM_URL=http://127.0.0.1:1234/v1/chat/completions
export DORMFIX_LLM_MODEL=local-model
```

If the endpoint is absent or fails, DormFix visibly uses manual/deterministic fallback and records a non-sensitive diagnostic. The resident still reviews every structured draft.

## Verify

```bash
python demo_scenario.py
python -m unittest discover -s tests -v
```

## Class demo

Follow `docs/DEMO_SCRIPT.md` for a short UC.1 → UC.4 walkthrough plus Administration/IT views.

## Architecture continuity

The implementation keeps the original repository boundaries (`resident_interface`, `ticket_service`, `intake_model`, `ticket_store`, `property_manager_interface`, `maintenance_technician_interface`) instead of replacing the project with an unrelated starter application. Streamlit + Python/FastAPI + SQLite + configurable LLM matches the documented planned toolchain.


## macOS first-run security / Gatekeeper

This classroom package is not Apple Developer ID signed/notarized. If macOS says Apple cannot verify `Install DormFix.command`, first attempt to open it once, then go to **System Settings → Privacy & Security → Security → Open Anyway**, authenticate with Touch ID/password, and choose **Open**. Finder Control-click → Open is another option. Do not disable Gatekeeper globally.

## Desktop installers and team workflow

Both Windows and macOS launchers are included. See packaging/README.md for the
original installer templates, guides and package assembly instructions.

Make changes on a branch and open a pull request targeting main. Obtain approval
from at least one other team member before merging. Each team member must make
at least one commit personally.
