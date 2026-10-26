# DormFix implementation traceability — demonstration build

This document distinguishes **implemented demo behavior** from **planned or validation-only requirements**. It is based on the project baseline retrieved from the prior SYSEN 5151/5930 materials and the Chapter 3 specification branch. It does not claim production deployment or completed human-subject validation.

## Implemented in this build

| Requirement / project intent | Demonstration implementation | Evidence |
|---|---|---|
| UC.1 resident request; SR.1–SR.3 | Resident description → structured/editable draft → missing-field gate → explicit confirmation → committed ticket | Streamlit Resident page; `begin_request`; `submit_maintenance_request`; tests |
| SR.24 / SR.33 AI advisory + manual fallback | Optional OpenAI-compatible LLM call; strips unapproved fields; deterministic/manual fallback when endpoint absent/fails; AI cannot set priority/assignee | `intake_model`; fallback test |
| SR.25 non-emergency boundary | Prominent application notice plus keyword-triggered emergency warning | `app.py`; test |
| UC.2 / SR.8–SR.11 manager authority | Manager queue; readiness gate; manager-only priority and technician assignment; audit events for corrections/decisions | Manager page; service tests |
| UC.3 / SR.12–SR.14 technician workflow | Assigned-job view; progress; complete; blocked return with required reason; access-change proposal | Technician page; tests |
| UC.4 / SR.7 / SR.28 | Completion moves to Awaiting resident confirmation; resident closes or reopens while retaining history | Resident page; end-to-end test |
| SR.29 | 72-hour manager exception closure implemented with 71:59 negative boundary and 72:00 positive test | `manager_exception_close`; unit test |
| SR.17 | Ordered event history with action, actor, time, notes and field changes | SQLite `events`; audit UI |
| SR.19 / SR.26 / SR.27 | SQLite persistence; commit-before-ticket response; unique submission key prevents duplicate retry | `ticket_store`; persistence/idempotency test |
| SR.20 | Authorized IT backup procedure creates a SQLite snapshot | IT page; backup test |
| SR.21–SR.23 | Demo account/role maintenance; inactive accounts denied; residents/technicians scoped to own/assigned tickets; administration aggregates only; IT diagnostics only | service layer + UI + tests |
| SR.18 | Non-sensitive diagnostic records for AI/fallback and backup operations | IT Support page |
| 5930 integrated-prototype WBS 1.5 | Resident intake, durable ticket history, manager assignment, technician progress, resident closure/reopening, service oversight/operations | full project |

## Implemented, but only at demonstration fidelity

- **Authentication:** role-based demo identities are seeded accounts selected from the sidebar. This verifies authorization logic but is **not production authentication**.
- **LLM:** an OpenAI-compatible local endpoint (such as LM Studio) can be configured. No external model is required; when unavailable, the UI explicitly falls back. Heuristic assistance is deterministic and must not be presented as a validated AI model.
- **Administration:** aggregate counts are available. Advanced grouped trend analysis remains deferred.
- **IT operations:** backup creation is implemented. Restore code exists at the data layer but the Streamlit UI intentionally avoids a one-click destructive restore during class demonstration.
- **Photos:** optional-photo storage/display is not implemented in this build; no claim is made that it is complete.
- **Access-change coordination:** technician proposal → manager coordination → resident confirmation is implemented for access text, preserving the existing access arrangement until resident confirmation.

## Not claimed as completed

- SR.4 / SR.6 / SR.31 / SR.32 percentage outcomes: no real participant/usability trial results are fabricated.
- SN.12 / SR.34 advanced grouped trend views: deferred in the baseline and still not claimed.
- Production security, SSO, deployment hardening, real emergency dispatch, billing, parts purchasing, rent integration, offline synchronization, or production monitoring.
- The baseline's 30–50 synthetic-scenario campaign and 10-ticket reconstruction study have **not** been represented as executed merely because the unit tests pass.

## Current automated verification

`python -m unittest discover -s tests -v` checks the implemented technical behaviors, including RBAC, idempotent submission, lifecycle transitions, reopen/history retention, blocked return, the 72-hour boundary, aggregate privacy, fallback behavior, and database backup.

These tests are engineering evidence for this demonstration build; they do not substitute for the later human validation metrics in the course baseline.
