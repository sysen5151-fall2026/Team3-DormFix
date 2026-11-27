# DormFix product risk register

SYSEN 5151 Team 3 · Project Task 6 · 21 November 2026

The identifiers below refer to the team’s architecture and requirements. Review their relationships in the native Innoslate model before closing Task 6.

## System risks

The Chapter 4–5 baseline assigns Medium likelihood and High overall impact to R1–R3. Under the verification scenario below, each has likelihood 3, overall impact 4 and a high score of 12. Overall impact is the largest of cost, schedule and technical impact.

| Risk | Corrective person-hours | Gate delay in working days | Cost | Schedule | Technical | Overall | L × I |
|---|---:|---:|---:|---:|---:|---:|---:|
| R1 Intake | 1.6 | 0 | 2 | 1 | 4 | 4 | 12 |
| R2 Privacy | 4.8 | 0 | 4 | 1 | 4 | 4 | 12 |
| R3 Ticket integrity | 8.0 | 2 | 4 | 4 | 4 | 4 | 12 |

Planning assumptions: assess one incident at a time with the full three-day WBS 1.6.3 correction allowance available. One person works at the scheduled 20% allocation (1.6 hours per working day). Assume one day for an R1 intake correction and retest, the three-day allowance for R2 role-access correction and checks, and the same allowance plus an additional two-day WBS 1.6.4 regression for R3. Delay is the excess over the three days. R3 takes priority because of its effect on the shared ticket record, tested exposure to loss and two-day verification delay in this scenario. These are planning estimates.

## Failure register

| ID / parent | Failure mode | Model trace | Control or planned check |
|---|---|---|---|
| P1 / R1 | Well-formed but wrong output | A1, DF.1, SR.33 | Editable intake and manager authority exist. Check an incorrect but valid category and invented access time before commit. |
| P2 / R1 | Model call unavailable or slow | A1, A7, SR.24 | Fallback code exists and the no-endpoint test passed. Inject a timeout and verify manual completion from the resident screen. |
| P3 / R1 | Untrusted resident text reaches the prompt | DI.1, A1, DC.1 | Adapter limits output fields. Verify that untrusted text cannot grant priority or assignment; keep those writes in manager actions. |
| P4 / R1 | Response schema changes | A1, A7, SR.24 | Malformed-output fallback exists. Exercise missing or retyped fields and verify a usable manual draft. |
| P5 / R1 | Model client or dependency is retired | A7, DF.6, SR.18, SR.24 | Proposed: pin a tested adapter configuration, rerun contract fixtures on upgrade and retain manual-only startup. |
| P6 / R2 | Unintended data egress or role disclosure | A7, DC.2, SR.22–23 | Demo role tests passed. A configured endpoint receives report fields. Review field minimization, destination policy and outbound data using synthetic records. |
| P7 / R3 | Partial commit, replay or bad checkpoint | A2, A7, DF.5–6 | Atomicity and retry tests passed. The product rotates two verified checkpoints. If the newest fails verification, IT Support can recover the previous version. See the failure-path results below. |

## R3 control evidence

On the product branch, an injected event-write failure left zero tickets and zero events. Retrying after a lost acknowledgement left one ticket and one submission event. With an intact latest checkpoint, recovery returned all 11 checkpoint tickets and their histories. After damaging that checkpoint, the product restored all 10 tickets and 50 events from the older checkpoint and reported the recovery gap. When both checkpoints failed verification, current tickets and histories remained intact. The full-record comparisons and HTTP operator test are in [the recovery suite](../tests/test_recovery.py). The [verification record](../VERIFICATION.md) includes the run environment and results.

## Monitoring

Before merge, require zero duplicates and zero partial commits in the failure tests. At integration, match every selected checkpoint ticket and event history. Record recovery time, selected generation and unrecovered recent changes. Review R3 weekly and retain the reviewed rating history, owner and verification evidence.

## Sources

Team 3, Chapter 4–5 architecture and requirements report, IDEF0 A1/A2/A7, and Task 6 trade study. The [decision record](adr/0002-backup-retention.md) links the selected architecture to its implementation. The [implementation baseline](https://github.com/sysen5151-fall2026/Team3-DormFix/tree/3a9c5d34b2f0f2cc3af4ba7b2eee8e567cb99868) identifies the product version on which the changes were based.
