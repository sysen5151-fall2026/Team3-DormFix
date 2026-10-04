# DormFix — Chapter 3 specification

SYSEN 5151 Fall 2026 · Team 3

## Baseline and scope

Source: the team-supplied *DormFix Stakeholder Needs and Requirements* report,
2 October 2026 baseline, sections 4–8 (15 needs, 34 stakeholder requirements).
[Needs document](https://cloud.innoslate.com/cornell/p/748/documents/230576) ·
[Requirements document](https://cloud.innoslate.com/cornell/p/748/documents/230592).

Need statements and requirement acceptance text below are transcribed from the
supplied report. The per-need summaries combine those existing criteria; they
introduce no new numerical performance target. Must/Should/Later priorities are
retained. SN.12/SR.34 remains deferred, with its missing measurable criterion
explicitly visible. Neither the report nor these files claim product acceptance.

Chapter 3 adds specification and deliberately red acceptance-test scaffolding.
The Chapter 2 canned UC.1 implementation is unchanged. The tests are explicit
unimplemented acceptance obligations, as in the lab manual's Chapter 3 example;
they do not execute human usability studies or pretend to measure the prototype.
Later increments must replace each failure with a requirement-derived check and
retain the need identifier. Do not skip, xfail, or weaken a test to make CI green.

## Needs and acceptance criteria

### SN.1 — Resident — Must

I need to report a problem in everyday language and confirm a structured draft without knowing maintenance categories.

Why: Missing location, category or access information causes repeated questions and delays.

CTQ / source: Low reporting effort and complete confirmed information

Origin: BMA + discussion

Traces to: SR.1, SR.2, SR.3, SR.4, SR.24, SR.25, SR.26, SR.33.

Acceptance: At least 90% unassisted first-use reporting success; every successful attempt takes at most 3 minutes from opening the flow to an acknowledged ticket ID. Cover at least two tasks per category (eight distinct tasks total), report people and attempts separately, and count assisted/failed attempts as unsuccessful. All draft fields remain editable; no ticket before confirmation; missing/uncertain values are not invented. Exercise manual fallback and the non-emergency notice.

Protocols: V.1, V.2.

Named test: `test_SN01_reporting_and_confirmation`. Status: RED; acceptance behavior/evidence not implemented.

### SN.2 — Resident — Must

I need to see the current stage, who is handling my request and what happens next so I can plan room access.

Why: Progress is dispersed across channels and residents must repeatedly ask for updates.

CTQ / source: Understandable status and a reliable shared history

Origin: BMA + discussion

Traces to: SR.5, SR.6, SR.17, SR.28, SR.30.

Acceptance: Show the six lifecycle stages with assigned technician/indicator, latest update time and next step. At least 90% of assessed resident responses identify BOTH stage and next step without prompting. Technician completion awaits resident confirmation; proposed access changes remain pending until resident confirmation.

Protocols: V.3, V.5, V.6, V.7.

Named test: `test_SN02_progress_and_comprehension`. Status: RED; acceptance behavior/evidence not implemented.

### SN.3 — Resident — Must

I need to reopen an unresolved repair while keeping its previous record so I do not have to explain the problem again.

Why: Starting a new request loses context and separates follow-up work from the original repair.

CTQ / source: Continuous history and a clear path back to the manager

Origin: BMA + discussion

Traces to: SR.7, SR.17, SR.28, SR.29.

Acceptance: Both primary reopen cases preserve ticket identity and all prior events, append actor/time/reason and return to manager attention. All closure checks follow the authorized actor rules. Deny the no-response manager exception at 71 hours 59 minutes; permit at 72 hours only without resident response, recording the exception and retaining reopening.

Protocols: V.4, V.6, V.7.

Named test: `test_SN03_reopening_and_closure`. Status: RED; acceptance behavior/evidence not implemented.

### SN.4 — Manager — Must

I need to distinguish complete requests from requests needing clarification before deciding priority and assignment.

Why: Repeated clarification consumes the manager's limited time and delays assignment.

CTQ / source: Visible completeness and fewer clarification cycles

Origin: BMA + discussion

Traces to: SR.3, SR.8, SR.31.

Acceptance: At least 90% of the 35 predeclared reporting opportunities need no further manager clarification after the intended correction flow. Include every designated case in the outcome count. For each missing/unusable description, building, room, category or access arrangement, assignment remains unavailable until corrected.

Protocols: V.2, V.5.

Named test: `test_SN04_manager_readiness`. Status: RED; acceptance behavior/evidence not implemented.

### SN.5 — Manager — Must

I need a consolidated view of pending work so that submitted or reopened requests are not forgotten.

Why: Fragmented status records make unprocessed requests easy to overlook.

CTQ / source: Complete pending-work coverage

Origin: BMA + discussion

Traces to: SR.7, SR.9, SR.14, SR.26, SR.27, SR.29.

Acceptance: 100% of submitted, reopened and returned tickets requiring manager action appear in the pending view. Reconcile expected IDs; retain assigned/in-progress work in the separate open-work view. No success before storage commit; retries of one submission create at most one committed ticket, including after a lost acknowledgement. Apply the recorded 72-hour closure exception.

Protocols: V.4, V.6, V.7, V.8.

Named test: `test_SN05_pending_work_and_retry`. Status: RED; acceptance behavior/evidence not implemented.

### SN.6 — Manager — Must

I need to correct AI suggestions and retain a record of my decisions so that final control and accountability remain with me.

Why: Incorrect AI output must not silently determine priority, assignment or the resident's original account.

CTQ / source: Human authority and traceable changes

Origin: BMA + discussion

Traces to: SR.2, SR.10, SR.11, SR.17, SR.33.

Acceptance: Only the manager commits priority/assignment after readiness passes. Resident, technician and AI attempts cannot do so. All tested corrections retain original description and AI suggestion, with field/old value/new value/actor/time. Ticket creation requires explicit resident confirmation.

Protocols: V.1, V.2, V.4, V.7.

Named test: `test_SN06_human_authority_and_audit`. Status: RED; acceptance behavior/evidence not implemented.

### SN.7 — Technician — Must

I need the problem, exact location and agreed access arrangements before leaving for a repair so that I can avoid an unnecessary trip.

Why: Missing information causes extra calls, inaccessible rooms or repeat visits.

CTQ / source: Enough information to depart without further questions

Origin: BMA + discussion

Traces to: SR.8, SR.12, SR.23, SR.30, SR.32.

Acceptance: At least 90% of predeclared eligible assigned-job scenarios receive a sufficient-to-depart judgment before extra information is revealed. Every eligible technician view matches confirmed description/building/room/category/access. Apply the assignment gate and field-access matrix; retain old access arrangements until the resident confirms the replacement.

Protocols: V.2, V.5, V.7.

Named test: `test_SN07_technician_readiness_and_access`. Status: RED; acceptance behavior/evidence not implemented.

### SN.8 — Technician — Should

I need to update progress and mark work complete from my phone with little typing while I am on site.

Why: Technicians work away from a desktop and may have unreliable connectivity.

CTQ / source: Usable mobile interaction and honest save feedback

Origin: Assumption

Traces to: SR.13.

Acceptance: Demonstrate both progress updates and work-complete action on a phone-sized browser. An unacknowledged update is visibly unsaved. No tap-count, response-time or offline-sync target is claimed.

Protocols: V.6.

Named test: `test_SN08_mobile_updates_and_save_feedback`. Status: RED; acceptance behavior/evidence not implemented.

### SN.9 — Technician — Should

I need to record why a job cannot be completed and return it to the manager for another arrangement.

Why: There is no consistent way to return blocked work and explain the next decision needed.

CTQ / source: Recorded reason and restored manager attention

Origin: Assumption

Traces to: SR.14.

Acceptance: Return without a reason is refused; return with a reason retains all earlier events and appears in manager pending work. Record Returned by technician using the Reopened state.

Protocols: V.4, V.6.

Named test: `test_SN09_return_blocked_work`. Status: RED; acceptance behavior/evidence not implemented.

### SN.10 — Admin. — Must

I need privacy-preserving summaries of outstanding work, processing time and repeat reports to supervise service quality.

Why: Administration cannot judge overall performance from scattered individual communications.

CTQ / source: Useful aggregate measures with limited personal information

Origin: BMA + discussion

Traces to: SR.15, SR.16, SR.22, SR.23, SR.27.

Acceptance: Summary unfinished counts and open/closed duration measures exactly reconcile to known fixtures, with cohort identified and open/closed durations kept separate. For configured window T, same-building/room/category matches include the T boundary; count each newer distinct ticket once; reopening is not a new report. Expose aggregates only and no sensitive ticket fields.

Protocols: V.7, V.8.

Named test: `test_SN10_aggregate_privacy_and_repeats`. Status: RED; acceptance behavior/evidence not implemented.

### SN.11 — Admin. — Must

I need the manager to provide a reliable account of who did what and when if a repair is disputed.

Why: A fragmented record makes it difficult to reconstruct events. Administration itself sees summaries only.

CTQ / source: Complete evidence that the manager can reconstruct

Origin: BMA + discussion

Traces to: SR.7, SR.11, SR.17, SR.29.

Acceptance: For 10 randomly selected synthetic tickets, the manager reconstructs every action, actor and time (100%); preserve full history through reopening, correction and exception closure. Administration receives the manager review account, not a ticket-history view.

Protocols: V.4, V.6, V.7.

Named test: `test_SN11_dispute_history`. Status: RED; acceptance behavior/evidence not implemented.

### SN.12 — Admin. — Later

I would like trends by building or problem category to support future service decisions.

Why: Overall totals do not reveal where recurring demand concentrates.

CTQ / source: Useful grouping without exposing residents

Origin: Assumption

Traces to: SR.34.

Acceptance: DEFERRED: SR.34 explicitly makes no acceptance claim in this increment. Aggregation periods and privacy controls must be agreed before this feature is scheduled. There is no approved measurable acceptance criterion yet; its named red test exposes that unresolved item rather than inventing one.

Protocols: Deferred.

Named test: `test_SN12_deferred_trend_criterion`. Status: RED; deferred criterion not agreed.

### SN.13 — IT support — Must

I need to see service and AI-connection failures and inspect diagnostic logs so I can identify the fault.

Why: A failure can remain unnoticed without health information and useful error records.

CTQ / source: Observable failure state without unnecessary ticket content

Origin: Assumption

Traces to: SR.18, SR.24.

Acceptance: Inject service and AI-connection failures: support health shows failure and timestamped diagnostics identify the type without resident descriptions/contacts/photos. On unavailable or malformed AI output, show manual-entry notice, preserve description and valid extracted fields, allow correction and complete normal submission. Alert latency remains unspecified.

Protocols: V.1, V.8.

Named test: `test_SN13_failure_diagnostics_and_fallback`. Status: RED; acceptance behavior/evidence not implemented.

### SN.14 — IT support — Must

I need committed tickets and histories to survive a restart and a usable backup-and-restore procedure so that records remain dependable.

Why: Lost tickets or histories defeat both operational follow-up and oversight.

CTQ / source: Persistence and demonstrable recovery

Origin: Assumption

Traces to: SR.19, SR.20, SR.26, SR.27.

Acceptance: After restart, zero acknowledged ticket/history/account/role/AI-suggestion/human-change records are missing or changed. Backup/restore reproduces all records in the selected backup; measure restoration time without a time target or a claim about post-backup writes. Success follows commit; repeated submission leaves at most one ticket.

Protocols: V.4, V.7, V.8.

Named test: `test_SN14_restart_restore_and_durable_submission`. Status: RED; acceptance behavior/evidence not implemented.

### SN.15 — IT support — Should

I need to add or deactivate accounts and change roles with a record of each change so that access remains appropriate.

Why: Uncontrolled permissions can expose information beyond the work each role needs to perform.

CTQ / source: Manageable roles and an auditable access policy

Origin: Assumption

Traces to: SR.21, SR.22, SR.23.

Acceptance: Exercise account create/deactivate/role-change with actor/target/old-new values/time recorded; a deactivated account gets no further access. Check all five roles against allowed/denied views and direct record requests, including cross-resident and unassigned-technician denial and sensitive-field restrictions.

Protocols: V.5, V.7, V.8.

Named test: `test_SN15_account_roles_and_privacy`. Status: RED; acceptance behavior/evidence not implemented.

## Evidence and denominators

The report specifies 40 primary synthetic cases: 24 nominal (six each plumbing,
electrical, appliances, general), five missing-information, four AI-error, two
AI-unavailable/malformed, three permission and two completion/reopen cases.
V.2 predeclares the first four families as 35 reporting opportunities. Failed or
poor reports stay in that denominator. Permission-only and reopen-only cases
serve other checks. Cross-cutting subchecks additionally cover the full role
matrix, both sides of 72 hours, storage failure/lost acknowledgement, ten sampled
histories, restart and restore. The headline 40 is not an exhaustive access test.

First-use participants are separate from synthetic fixtures. V.1 needs people
unfamiliar with the prototype; participant count/recruitment are still TBD.
Before execution record build/fixture version, case IDs, roles, devices,
expected outcomes and exclusions. Retain actual results, timestamps,
evidence, pass/fail and deviations. No observations have been manufactured.

## Data Contract

This is a Chapter 3 semantic contract for later implementation, not a claim
that the current stub persists these records or that an API exists. Python dicts
in the skeleton correspond to JSON objects at future boundaries. Field spellings
below are a proposed serialization of report concepts; review them before the
Chapter 7 interface is frozen. Existing `description`, `category`, `location`,
`availability`, `missing_fields`, `ticket_id`, `status`, and `request` names are
retained. Building/room refine the existing location concept (SR.3/SR.12).

### Sources, types and units

| Source → consumer | Fields / type / units | Absence and ownership |
|---|---|---|
| Resident → resident_interface → ticket_service | Original `description`: nonempty string; `building`, `room`: strings; `location`: display string; `availability`: string with explicit `anytime` permitted; `category`: one of plumbing/electrical/appliances/general or null while uncertain; `photos`: optional list of references | Never invent required values. Uncertain category stays null/blank. `missing_fields` is a list of required-field names; photos are not required. The resident reviews and confirms the draft. |
| intake_model → ticket_service → resident | Suggested `category`, `summary`, `location`, `availability`: string or null; `missing_fields`: list of strings | Suggestions only; original description preserved. See Model Response Contract. Priority and assignment do not come from the model. |
| Manager → ticket_service | Priority: manager-selected string; assigned technician: identifier string or null before assignment; corrections: field/old value/new value/actor/time | Priority vocabulary is not fixed by this baseline. Do not default an absent priority/assignee into an authorized decision. Assignment requires complete usable information. |
| ticket_store → authorized views | `ticket_id`: opaque string; `request`: structured object; owner/assigned technician: identifier strings; `status`: lifecycle enum below; submitted/latest-update timestamps; ordered history events | The committed store is authoritative. No success or committed identifier is presented on write failure. Unassigned technician is null; show an unassigned indicator. |
| Technician/resident/manager → ticket event history | Action/type: string; actor: identifier string; timestamp; notes/reason: string when required; changed-field old/new values | Return and reopening retain earlier events. A return requires a reason. Corrections preserve originals. Completed work is not automatically accepted. |
| Identity/role store → access control | Account identifier: string; active: boolean; role: Resident/Technician/Manager/Administration/IT Support; change record: actor/target/old/new/time | Missing or inactive identity grants no access. Administrative restore is a privileged procedure, not ordinary IT ticket browsing. |
| Committed records → Administration | Unfinished count: nonnegative integer, tickets; open age and submission-to-close duration: nonnegative elapsed time; cohort; repeat count and configured window T | No ticket-level personal fields. Keep open and closed duration cohorts separate; absent close time is null, never zero-duration closure. |
| Service/model connections → IT support | Health state, failure type, diagnostic timestamp, non-sensitive context | Do not log resident descriptions, contacts or photos. Do not show a healthy state from a missing response. |
| Database → authorized backup/restore procedure | Snapshot of tickets, histories, accounts, roles, AI suggestions and human changes; backup identifier/time | Restore reproduces that snapshot. It does not promise zero loss of writes newer than the selected backup. |

Timestamp representation for later adapters: timezone-aware ISO 8601 strings;
elapsed durations and configurable T expressed in seconds (72 hours = 259200
seconds). Human-facing units must be labeled. These serialization conventions
do not add a response-time target or choose the operational T value.

Lifecycle values: Submitted, Assigned, In progress, Awaiting resident confirmation,
Closed, Reopened. `Needs information` is a completeness marker, not a seventh
state. A technician return uses Reopened with event type Returned by technician.
The existing stub's `submitted` string is its canned representation; no runtime
migration is made in this increment.

### Refresh cadence and unavailable-source behavior

Read authoritative ticket/history data on each requested view or user action;
acknowledged changes become the source for the next view. Model extraction is
requested on an explicit reporting interaction, not a background decision loop.
Summaries are computed for the declared cohort/window when requested and display
T. No polling interval, cache freshness SLA or alert latency has been agreed.
Backup is an authorized explicit operation; schedule/frequency and recovery-time
target remain TBD. These event-based trigger descriptions prescribe no hidden
periodic service in this increment.

If required input is null/missing/unusable, retain it as unconfirmed, request
clarification and block assignment (SR.3/SR.8). A complete draft still needs
resident confirmation before submission. A source/storage write outage produces
visible failure and retained input for retry, never a false success (SR.26).
Retries of the same submission must commit at most one ticket (SR.27); the
idempotency mechanism belongs to later design. For unreadable records do not
invent current status or totals; report unavailable information and record a
non-sensitive diagnostic (SR.18). On AI failure use manual entry (SR.24).

### Access restrictions

Residents: own tickets. Technicians: assigned tickets. Managers: all tickets.
Administration: aggregates only. Ordinary IT support: diagnostics only.
Room/access/photos are visible only to owning resident, manager and assigned
technician; resident contact details only to the manager. Apply these rules to
returned records as well as pages, logs and summary responses (SR.22/SR.23).
Privileged backup/restore remains separate from ordinary ticket-view access.

## Model Response Contract

Participant: `intake_model`, planned local LM Studio / Llama 3.1 8B Instruct per
`docs/environment.md`. No live model call or paid API is introduced here.
Input is the resident's description plus explicitly supplied clarification;
the original description remains authoritative and is never overwritten.

The requested result is exactly one structured JSON object of suggestions:

```json
{
  "category": null,
  "summary": null,
  "location": null,
  "availability": null,
  "missing_fields": ["category", "building", "room", "availability"]
}
```

Each of category/summary/location/availability is a string or null. Category, if
present, belongs to the four supported categories above; summary is one sentence
when supported by the input. `missing_fields` is an array of required-field names.
The service also checks completeness against resident-confirmed data; a model
claim of completeness cannot bypass the gate. Null means unknown, not permission
to infer an address/access window. No priority, assignee, closure decision or
commit instruction is accepted from the model (SR.33).

Unavailable, malformed, missing-field or wrong-type output switches to visible
manual entry. Preserve the original description and individually valid extracted
fields; permit correction and normal confirmed submission. Do not display raw
malformed output or silently choose an uncertain category. Unexpected
priority/assignee fields cannot set those decisions. Even well-formed suggestions
are editable and require resident confirmation; the manager retains operational
authority (SR.2/SR.10/SR.24/SR.33). Diagnostic records omit private ticket content.

## Open decisions retained from the report

- SN.12/SR.34: Later. No current acceptance commitment; period/privacy controls
  must be set before a measurable trend criterion is approved. The SN12 test is
  deliberately red for this specific missing specification, not passed/skipped.
- D.3: operational repeat window T remains open; boundary behavior is specified.
- D.4: recovery time and backup frequency remain open; restart/restore correctness
  is testable without inventing either number.
- D.5: direct resident contact is manager-only; coordination mechanism remains TBD.
- D.6: optional display of two category candidates is undecided; unknown stays blank.
- D.7: first-use participant recruitment/count remain open. A rehearsed team demo
  cannot count as first-use success.

## Requirement register and exact planned acceptance

The 34 entries below preserve the report's wording and source-need links. They
are the detailed obligations referenced by the per-need red tests above.

### SR.1 — Structured draft — Must

DormFix shall present an editable structured draft from the resident's everyday-language description, including any extracted category, one-sentence summary, location and access arrangements.

Rationale: Residents can check an interpretation without needing maintenance terminology.

Planned acceptance / trace:

Inspect drafts for the four supported categories. All proposed fields are visible and editable before submission.

Needs: SN.1
Protocol: V.1, V.2

### SR.2 — Resident submission confirmation — Must

DormFix shall require an explicit resident confirmation of the draft before creating a submitted ticket.

Rationale: The resident remains responsible for confirming what is reported.

Planned acceptance / trace:

Attempt submission without confirmation, then with confirmation; only the confirmed attempt may create a ticket.

Needs: SN.1, SN.6
Protocol: V.1

### SR.3 — Missing and uncertain information — Must

DormFix shall identify unconfirmed or missing required information without inventing a value for category, location or access arrangements.

Rationale: Completeness must reflect information supplied or confirmed by a person.

Planned acceptance / trace:

Required information is description, building, room, category and access arrangement; photos are optional and access may explicitly be anytime. Uncertain category remains blank. Missing location/access is highlighted.

Needs: SN.1, SN.4
Protocol: V.2

### SR.4 — Reporting effort — Must

DormFix shall support an unassisted first-use reporting success rate of at least 90%, with successful attempts completed within 3 minutes under the V.1 protocol.

Rationale: The team chose an observable usability target for the reporting flow.

Planned acceptance / trace:

Apply V.1 and report first-time participant and attempt counts; include confirmation time and all unsuccessful attempts.

Needs: SN.1
Protocol: V.1

### SR.5 — Resident progress view — Must

DormFix shall show the resident the current state, assigned technician or an assigned indicator, latest update time and next step for each of the resident's tickets.

Rationale: A shared view reduces repeated requests for progress information.

Planned acceptance / trace:

Inspect Submitted, Assigned, In progress, Awaiting resident confirmation, Closed and Reopened pages. Show the appropriate next action at each state.

Needs: SN.2
Protocol: V.3

### SR.6 — Understandable status — Must

DormFix shall enable at least 90% of assessed resident responses to identify both the current stage and next step correctly under V.3.

Rationale: Understanding is the intended outcome of displaying status.

Planned acceptance / trace:

Apply the unprompted two-part comprehension check in V.3.

Needs: SN.2
Protocol: V.3

### SR.7 — Reopen with history — Must

DormFix shall reopen an unresolved ticket at the resident's request by preserving its complete history, appending a reopening event and returning it to manager attention.

Rationale: Reopening should continue the repair record rather than create a disconnected report.

Planned acceptance / trace:

Both primary reopen cases retain every prior event and ticket identity, append actor/time/reason and appear in the manager pending view.

Needs: SN.3, SN.5, SN.11
Protocol: V.4, V.6

### SR.8 — Assignment readiness gate — Must

DormFix shall prevent assignment until the ticket has a usable description, category, complete location and access arrangements, and shall mark any request needing clarification as Needs information.

Rationale: Presence of text alone is insufficient if the manager cannot use it to arrange work.

Planned acceptance / trace:

Try each missing or unusable field in turn; assignment stays unavailable until corrected. Needs information is a completeness marker, not another lifecycle state.

Needs: SN.4, SN.7
Protocol: V.2, V.5

### SR.9 — Complete pending-work view — Must

DormFix shall include every submitted, reopened or returned ticket requiring manager action in the manager's pending-work view.

Rationale: The manager needs both a decision queue and visibility of ongoing work.

Planned acceptance / trace:

Reconcile 100% of expected pending ticket IDs under V.4; maintain a separate open-work view for assigned and in-progress tickets.

Needs: SN.5
Protocol: V.4

### SR.10 — Manager decision authority — Must

DormFix shall reserve priority and technician-assignment decisions for the property manager and record the selected technician and assignment time.

Rationale: AI advice does not transfer operational decision authority.

Planned acceptance / trace:

Resident, technician and AI outputs cannot commit a priority or assignment; a manager can do so after the readiness gate passes.

Needs: SN.6
Protocol: V.4

### SR.11 — Auditable manager corrections — Must

DormFix shall preserve the original resident description and AI suggestions while recording each manager correction with field, previous value, new value, actor and time.

Rationale: The team needs to explain changes without rewriting the resident's original account.

Planned acceptance / trace:

Change category, priority and supplemental notes; verify all five audit fields and that the original description is unchanged.

Needs: SN.6, SN.11
Protocol: V.7

### SR.12 — Technician job information — Must

DormFix shall show the assigned technician the issue description, building, room, category and confirmed access arrangements before work begins.

Rationale: These are the minimum details required to prepare for a visit.

Planned acceptance / trace:

For every eligible job, compare the technician view with the confirmed ticket fields.

Needs: SN.7
Protocol: V.5

### SR.13 — Mobile progress updates — Should

DormFix shall allow the assigned technician to record progress and mark work complete using a mobile browser.

Rationale: An on-site technician cannot depend on a desktop; offline synchronization is not currently promised.

Planned acceptance / trace:

Demonstrate both actions on a phone-sized browser; an unacknowledged update remains visibly unsaved. Tap-count and time limits are not yet agreed.

Needs: SN.8
Protocol: V.6

### SR.14 — Return blocked work — Should

DormFix shall allow the assigned technician to return a job to the manager with a required reason and a retained event history.

Rationale: The manager needs a clear reason before arranging further action.

Planned acceptance / trace:

Attempt return without a reason, then with one; verify pending visibility and retained earlier events. Reopened is used with event type Returned by technician.

Needs: SN.9, SN.5
Protocol: V.4, V.6

### SR.15 — Aggregate service summary — Must

DormFix shall provide Housing Administration with aggregate counts of unfinished tickets and processing durations without ticket-level personal information.

Rationale: Clearly defined summary measures support supervision without expanding access.

Planned acceptance / trace:

Unfinished means any state other than Closed. Display elapsed age for open tickets and submission-to-close duration for closed tickets; disclose the selected cohort and avoid averaging open and closed durations together. Reconcile to fixture values.

Needs: SN.10
Protocol: V.7

### SR.16 — Repeat-report summary — Must

DormFix shall summarize repeat reports using the same room and category within an explicitly configured time window.

Rationale: A declared window makes the count reproducible; the operational value is selected before a pilot.

Planned acceptance / trace:

Set window T and test same-building, same-room, same-category matches inside, at and outside T; include the boundary. Count each newer distinct ticket once if a prior match exists within T. Reopening is not a new report. Display T with the summary.

Needs: SN.10
Protocol: V.7

### SR.17 — Reconstructable event history — Must

DormFix shall retain an ordered ticket-event history identifying each action, actor and time for reconstruction by the property manager.

Rationale: A disputed repair needs a continuous, attributable account.

Planned acceptance / trace:

The manager reconstructs every event for 10 randomly selected synthetic tickets. Administration receives the manager's review account and has no ticket-history view.

Needs: SN.2, SN.3, SN.6, SN.11
Protocol: V.7

### SR.18 — Failure visibility — Must

DormFix shall provide IT support with service-health information and time-stamped diagnostic records of service and AI-connection failures.

Rationale: Support needs evidence that a failure occurred and where to investigate it.

Planned acceptance / trace:

Inject service and AI failures; the support view reports failure and logs contain enough context to identify its type without resident descriptions, contacts or photos. Alert latency is not yet specified.

Needs: SN.13
Protocol: V.8

### SR.19 — Persistence across restart — Must

DormFix shall retain all acknowledged tickets, status histories, accounts, roles, AI suggestions and human-change records across a service restart.

Rationale: The record of accepted work must outlive the service process.

Planned acceptance / trace:

Compare complete pre-restart committed fixtures with the post-restart records; require zero missing or changed records.

Needs: SN.14
Protocol: V.8

### SR.20 — Backup and restoration — Must

DormFix shall enable an authorized support operator to create a database backup and restore its recorded contents.

Rationale: Recovery needs a demonstrated procedure as well as persistent storage.

Planned acceptance / trace:

Demonstrate backup and restore against a known fixture and compare all included records. Measure restoration time, but do not claim a time target until one is agreed.

Needs: SN.14
Protocol: V.8

### SR.21 — Account and role maintenance — Should

DormFix shall enable an authorized support operator to create or deactivate an account and change its role with an attributable change record.

Rationale: Permission maintenance needs the same accountability as ticket changes.

Planned acceptance / trace:

Exercise all three actions; log actor, target account, old/new values and time. A deactivated account cannot obtain further access.

Needs: SN.15
Protocol: V.8

### SR.22 — Role-based ticket access — Must

DormFix shall limit resident access to owned tickets, technician access to assigned tickets, manager access to all tickets, administration access to aggregates, and ordinary IT access to system diagnostics.

Rationale: Privacy takes precedence over broader visibility for convenience.

Planned acceptance / trace:

Apply the role-access matrix to permitted and forbidden views and direct record requests; confirm no cross-resident or unassigned-technician access.

Needs: SN.10, SN.15
Protocol: V.7, V.8

### SR.23 — Minimum sensitive fields — Must

DormFix shall expose room location, access arrangements and photos only to the owning resident, manager and assigned technician, and resident contact details only to the manager.

Rationale: Each role should receive only the information needed for its work.

Planned acceptance / trace:

Inspect each role response and page against the field-access matrix; logs and summaries contain no such sensitive ticket fields.

Needs: SN.7, SN.10, SN.15
Protocol: V.5, V.7

### SR.24 — Manual fallback — Must

DormFix shall switch to manual entry when the AI service is unavailable or its response is malformed, preserving the description and any successfully extracted fields.

Rationale: The reporting service must remain usable when AI assistance fails.

Planned acceptance / trace:

Inject unavailability and a malformed response. Show an explicit manual-entry notice, preserve valid inputs, allow correction and complete a normal submission.

Needs: SN.1, SN.13
Protocol: V.1, V.8

### SR.25 — Emergency boundary notice — Must

DormFix shall display a prominent non-emergency-use notice and external-channel guidance when the configured emergency warning keywords are encountered.

Rationale: The routine repair flow must not imply that it dispatches an emergency response; keyword coverage is limited.

Planned acceptance / trace:

Use synthetic fire, gas leak and severe-water-leak terms. Verify the notice identifies DormFix as non-emergency and the prototype contact as a nonfunctional placeholder.

Needs: SN.1
Protocol: V.1

### SR.26 — Acknowledged submission — Must

DormFix shall show submission success and a ticket identifier only after storage confirms that the ticket was committed.

Rationale: A resident must not believe that an unrecorded report has been accepted.

Planned acceptance / trace:

Force a storage failure; success is absent, an error is visible and the entered form remains available for retry. Then verify the acknowledged path returns the committed ID.

Needs: SN.1, SN.5, SN.14
Protocol: V.4, V.8

### SR.27 — Safe submission retry — Must

DormFix shall prevent retries of the same submission from creating duplicate tickets.

Rationale: Retries must not inflate queues or repeat-report measures.

Planned acceptance / trace:

Repeat a failed or interrupted submission and repeat a request after a lost acknowledgement; at most one committed ticket exists for that submission.

Needs: SN.5, SN.10, SN.14
Protocol: V.4, V.7

### SR.28 — Resident-confirmed completion — Must

DormFix shall move technician-completed work to Awaiting resident confirmation and close it when the resident confirms resolution, subject to the manager exception in SR.29.

Rationale: Completion and acceptance are different decisions.

Planned acceptance / trace:

A technician cannot close a ticket directly. Resident confirmation from Awaiting resident confirmation creates a recorded Closed transition.

Needs: SN.2, SN.3
Protocol: V.6

### SR.29 — Three-day exception closure — Must

DormFix shall permit the manager to close a ticket without resident confirmation only after 72 hours without a resident response in Awaiting resident confirmation, recording the exception and retaining reopening access.

Rationale: The team confirmed a three-day exception while preserving transparency and recourse.

Planned acceptance / trace:

Attempt at 71 hours 59 minutes and at 72 hours; only the latter may succeed when there is no resident response. Record Closed without resident confirmation, actor and time. A resident response prevents this no-response exception.

Needs: SN.3, SN.5, SN.11
Protocol: V.6, V.7

### SR.30 — Coordinated access changes — Must

DormFix shall retain the existing confirmed access arrangement until the manager coordinates a technician-requested change and the resident confirms the replacement.

Rationale: A manager's coordination decision must not silently change the resident's access consent.

Planned acceptance / trace:

Record a technician proposal, manager-coordinated option and resident confirmation; before confirmation show the new option as pending, not agreed.

Needs: SN.2, SN.7
Protocol: V.5

### SR.31 — Manager-ready reporting outcome — Must

DormFix shall achieve at least 90% of eligible submitted requests requiring no manager clarification under the V.2 readiness protocol.

Rationale: Fewer clarification cycles are the outcome sought by the manager.

Planned acceptance / trace:

Use the V.2 checklist on 30–50 predeclared eligible synthetic reporting cases and record every judgment.

Needs: SN.4
Protocol: V.2

### SR.32 — Technician-ready assignment outcome — Must

DormFix shall achieve a sufficient-to-depart judgment in at least 90% of eligible assigned-job scenarios under V.5.

Rationale: The ticket should provide actionable visit information.

Planned acceptance / trace:

Record technician-proxy decisions and missing-field reasons before revealing additional scenario information.

Needs: SN.7
Protocol: V.5

### SR.33 — Advisory AI boundary — Must

DormFix shall restrict AI assistance to category, summary, location, access-arrangement and missing-information suggestions, leaving priority and assignment decisions to the manager.

Rationale: The team explicitly limited the AI role to supporting information entry.

Planned acceptance / trace:

Inject an AI response containing a priority or assignee suggestion; verify it cannot set either decision. All accepted extracted fields remain subject to resident confirmation.

Needs: SN.1, SN.6
Protocol: V.2, V.4

### SR.34 — Grouped service trends — Later

DormFix shall support aggregate trend views by building or category in a later increment.

Rationale: This is a recorded future need rather than a current implementation commitment.

Planned acceptance / trace:

No acceptance claim in this increment. Define aggregation periods and privacy controls before scheduling this feature.

Needs: SN.12
Protocol: Deferred

## Running the Chapter 3 checks

Use Python 3.12. No third-party dependency or model server is needed:

```sh
python app.py
python -m unittest discover -s tests -v
```

The first command still runs the canned Chapter 2 demonstration. The second
collects 15 named acceptance placeholders and exits nonzero with 15 explicit
failures. Fourteen cover baseline needs whose evidence is unimplemented; one
records SN.12's deferred, unapproved criterion. These are requirements obligations,
not fifteen observed product defects or fifteen completed validation studies.
`.github/workflows/tests.yml` runs the same command on push and pull request.
