# Consolidated implementation trace

| Need | Requirement | Function | Module | Evidence and deviations |
|---|---|---|---|---|
| SN.1 | SR.1 Structured draft | A1 | resident_interface, intake_model, resident_intake.js | I1 · Editable draft and original description. D2/D3. |
| SN.1, SN.6 | SR.2 Resident submission confirmation | A1/A2 | resident_api, ticket_service | I1 · Unconfirmed POST rejected. No ticket at draft stage. |
| SN.1, SN.4 | SR.3 Missing and uncertain information | A1 | intake_model, resident_api | I1 · Missing access stays blank. Empty building rejected. |
| SN.1 | SR.4 Reporting effort | A1 | webapp, resident_intake.js | V.1 open · First-use success and time require people. |
| SN.2 | SR.5 Resident progress view | A2/A5 | webapp.ticket_view, ticket_service | I1 · Owner reads the same ID, state and next step. |
| SN.2 | SR.6 Understandable status | A2/A5 | ticket_view, NEXT_STEP | V.3 open · Resident comprehension requires observation. |
| SN.3, SN.5, SN.11 | SR.7 Reopen with history | A2/A5 | resident_reopen, ticket_store.events | U1/U3 · Reopening retains the ID and ordered history. |
| SN.4, SN.7 | SR.8 Assignment readiness gate | A3 | property_manager_interface, readiness | U1/I1 · Complete drafts assign. Submission rejects missing data; legacy incomplete assignment case not separately run. |
| SN.5 | SR.9 Complete pending-work view | A2/A3 | manager_pending, webapp.manager | U3 · Reopened IDs reconciled on 16 synthetic tickets. |
| SN.6 | SR.10 Manager decision authority | A3 | manager_assign, intake_model | U1/I1 · Resident cannot assign. Injected priority discarded. |
| SN.6, SN.11 | SR.11 Auditable manager corrections | A3/A2 | manager_correct_ticket, update_ticket | U3 · Manager correction recorded. D6 covers audit noise. |
| SN.7 | SR.12 Technician job information | A4 | maintenance_technician_interface, get_visible_ticket | U1 · Assigned technician can read. Other technician denied. |
| SN.8 | SR.13 Mobile progress updates | A4 | webapp.technician, technician_progress | U1/B1 · Updates persist. Physical mobile use unmeasured. |
| SN.9, SN.5 | SR.14 Return blocked work | A4/A2 | technician_return, manager_pending | U1 · Missing reason rejected. Blocked job returns to queue. |
| SN.10 | SR.15 Aggregate service summary | A6 | administration_summary, aggregate_summary | U3/B1 · Open/closed hour measures separated. D7. |
| SN.10 | SR.16 Repeat-report summary | A6 | aggregate_summary, webapp.admin | U3 · Inside/at/outside window exercised. Demo T = 7 days. D7. |
| SN.2, SN.3, SN.6, SN.11 | SR.17 Reconstructable event history | A2/A6 | ticket_store.events, ticket_view | U3 · 10 of 16 seeded histories checked for action, actor, field and time. Manager-led reconstruction remains open. |
| SN.13 | SR.18 Failure visibility | A7 | support_health, record_diagnostic | U3 · Injected timeout produced an IT-visible failure. |
| SN.14 | SR.19 Persistence across restart | A2/A7 | ticket_store.connect, checkpoints | U1/U2 · Durable reads and checkpoint data. Full cold restart has a separate socket-mode check. |
| SN.14 | SR.20 Backup and restoration | A7 | ticket_store.checkpoints, IT controls | U2/B1 · Latest, predecessor, both-invalid, role and confirmation checks. ADR-0002. |
| SN.15 | SR.21 Account and role maintenance | A7 | support_set_account_active, account store | U2 · Inactive IT denied. Account creation/role maintenance available in Streamlit; full role-change audit protocol open. |
| SN.10, SN.15 | SR.22 Role-based ticket access | A7 | require_account, sanitize_ticket | U1/I1 · Cross-owner and unassigned-tech reads denied. Demo identity selector, ADR-0003. |
| SN.7, SN.10, SN.15 | SR.23 Minimum sensitive fields | A7/A6 | sanitize_ticket, intake_model, webapp.admin | U1/I1 · Role guards, aggregate-only output, contact field omitted from model call. Photos absent. |
| SN.1, SN.13 | SR.24 Manual fallback | A1/A7 | structure_request, resident_intake.js | I1/U3 · Wrong type, HTTP failure and timeout reach manual entry. |
| SN.1 | SR.25 Emergency boundary notice | A1 | intake_model, webapp.layout | U1 · Emergency warning and routine-use notice. Keyword coverage limited. |
| SN.1, SN.5, SN.14 | SR.26 Acknowledged submission | A1/A2 | resident_api, ticket_store.create_ticket | U2/I1 · Failed initial event rolls back ticket. Receipt follows commit. |
| SN.5, SN.10, SN.14 | SR.27 Safe submission retry | A2/A7 | create_ticket, resident_intake.js | I1/J1 · Eight simultaneous retries, stable key, one ID. Other owner denied. |
| SN.2, SN.3 | SR.28 Resident-confirmed completion | A4/A5 | technician_complete, resident_confirm_resolution | U1/I1 · Completion waits. Owner confirms before closure. |
| SN.3, SN.5, SN.11 | SR.29 Three-day exception closure | A2/A5 | manager_exception_close, ticket_store | U1 · Denied at 71 h 59 min. Allowed at 72 h. |
| SN.2, SN.7 | SR.30 Coordinated access changes | A4/A5 | propose_access_change, resident_confirm_access_change | U3 · Old access preserved until owner accepts the coordinated option. |
| SN.4 | SR.31 Manager-ready reporting outcome | A1/A3 | readiness, manager queue | V.2 open · Manager judgments on the predeclared cohort required. |
| SN.7 | SR.32 Technician-ready assignment outcome | A4 | technician view and scoped ticket service | V.5 open · Technician-proxy sufficient-to-depart judgments required. |
| SN.1, SN.6 | SR.33 Advisory AI boundary | A1/A3 | intake_model, resident_api | I1/J1 · Wrong classification corrected. Suggested assignment ignored. |
| SN.12 | SR.34 Grouped service trends | A6 | aggregate_summary (prospective extension) | Deferred · No grouped-trend implementation or approved criterion. ADR-0003. |

U1 = tests/test_dormfix.py. U2 = tests/test_recovery.py. U3 = tests/test_chapter13.py. I1 = verify_ch13.py (recorded offline transport via verify_inprocess.py). J1 = tests/test_resident_ui.cjs. B1 = measure_interfaces.py. V.1–V.8 = original Chapter 3 protocols.
