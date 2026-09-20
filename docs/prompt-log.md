# Prompt Log

## 2026-09-19 — Team 3 

Built from:
- DormFix system context model
- DormFix operational concept
- UC.1 Resident Requests Maintenance

Prompt purpose:
Assist with establishing the Chapter 1 repository scaffold and documentation structure based on the team's existing DormFix model and product concept.

Reviewed by:
Team 3

Assistant assumptions:
No additional product features were promoted beyond the team's modeled scope. Repository artifacts were reviewed against the SYSEN 5151 Lab Manual before being added.
## 2026-09-19 — Team 3 

Built from:
- UC.1 Resident Requests Maintenance
- DormFix planned behavioral sequence
- docs/walking-skeleton.md

Prompt purpose:
Generate the Chapter 2 DormFix walking skeleton using stub participants that match the UC.1 architectural call sequence.

Components:
- resident_interface
- ticket_service
- intake_model
- ticket_store

Constraints:
- hard-coded stub values only
- no real SQLite access
- no real language-model call
- no error handling
- no retries
- no logging
- no functionality outside UC.1

Reviewed by:
Team 3

Assistant assumptions:
The provisional UC.1 call order uses resident_interface, ticket_service, intake_model, and ticket_store. This call sequence must be reconciled with the final Innoslate Sequence Diagram when the diagram is completed.

## Historical record completeness

The two historical entries above are preserved as recorded. Their individual
generator, assistant/model, original prompt, reviewer, review outcome, and
assumption disposition are not fully documented in this public log.
The UC.1 refinement below supersedes their provisional call-order description.

## 2026-09-19 — Documentation repair

Requested by: Gengrui Jiang (`gj248-arch`).
Generated and checked by: Codex. Assistant model identifier: not recorded.

Purpose and files: added the startup command in `README.md`, synchronized
`docs/environment.md` with ADR-0001 (LM Studio / Llama 3.1 8B Instruct), and
recorded known assistant usage and provenance gaps in `docs/prompt-log.md`.

Validation: the existing stub ran successfully with Python 3.12.14, and both
historical entries were preserved.

## 2026-09-19 — UC.1 model and walking-skeleton alignment

Requested by: Gengrui Jiang (`gj248-arch`).
Generated and checked by: Codex. Assistant model identifier: not recorded.

Purpose and files: changed `app.py`, `resident_interface/__init__.py`, and
`ticket_service/__init__.py` to separate description, supplementation/draft
review, and submission. Only submission creates the canned ticket. Updated
`docs/walking-skeleton.md` with eleven numbered UC.1.WS interactions and
participant mapping, and repaired its `README.md` link.

Model source: saved UC.1.WS Sequence 199600 and its four internal Assets.
UC.1 business Sequence 184356 is the system-boundary view.

Validation by Codex: checked the saved model's eleven ordered interactions and
five lifelines. A Python 3.12.14 execution trace observed all eleven interactions,
prompt/draft/ticket display order, no ticket before submission, and exactly one
creation receiving the displayed draft. A separate Codex review checked the
code and mapping; this was AI review.

Assumptions: inputs, missing-field responses, draft fields, and ticket ID are
fixed fixtures. The second stage returns a canned complete draft; display
followed by a separate submit call represents review and confirmation.
The increment has no real model call, persistence, authentication, confirmation
validation, error handling, retries, or logging.

## Human review status and remaining provenance

The team reports that human review of the existing Chapter 1–2 project is
complete, with no major content changes requested. The reviewer's name and
review date were not supplied. The new official-repository import pull request
still requires approval from another team member before merging.

This public log contains usage summaries. Complete prompt references,
unrecorded model identifiers, and individual generation/review details remain
provenance gaps; they have not been reconstructed or assigned to team members.
