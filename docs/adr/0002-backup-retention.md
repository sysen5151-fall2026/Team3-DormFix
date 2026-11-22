# ADR 0002 · Retain two verified SQLite checkpoints

**Status** — Selected for the local demonstration build. Integration into the shared demo branch is subject to team review.

**Decision** — IT Support creates checkpoints on demand. Keep the two newest usable generations, each with its own SQLite snapshot and manifest. Verify the digest, SQLite integrity, references and ticket count on recovery. Try the preceding generation when the newest fails verification. Display the selected generation and recovery time point so the operator can identify later work that needs re-entry.

## Criteria and trade study

Recovery (C1, SN.11/14, SR.17/19/20, A2/A7) measures the fraction of complete ticket histories recovered. Its value is 100 × fraction recovered. Full data copies (C2, SN.15, SR.22/23, A7/DC.2) measure exposure of room and access details. Its value is 100 × (2 − retained copies).

| Design | Intact newest | Unreadable newest | Full copies | Weighted value / 100 | Estimated 12-week cost |
|---|---:|---:|---:|---:|---:|
| A · One verified copy | 11/11 | 0/11 | 1 | 62.96 | $86.25 |
| B · Two verified copies | 11/11 | 10/11 | 2 | 70.71 | $157.50 |

The team report’s scoring assumptions give the intact and unreadable cases equal weight. The swing points of 100 for recovery and 35 for copies normalize to 74.07% and 25.93%. A wins at a recovery weight of 60%, the designs tie at 68.75%, and B wins above that point. Both fit the assumed $200 ceiling at $25 per labor hour using existing storage. The figures are planning estimates from the Task 6 trade study.

## Consequences and evidence

B adds one full sensitive copy. Both generations share a host and storage device. Changes made after the selected checkpoint require reconciliation, and loss of the whole backup directory requires a separate recovery source. Operator-created standalone exports remain outside managed rotation.

The store implements the decision in [checkpoints.py](../../ticket_store/checkpoints.py). The [verification record](../../VERIFICATION.md) documents the product recovery results. The highest-priority risk and model references are in [the product risk register](../risks.md).
