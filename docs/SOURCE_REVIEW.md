# Source review and implementation basis

Before implementing this build, the following project sources were reviewed and used as constraints rather than treated as optional inspiration:

1. **SYSEN 5151 Business/Mission Analysis report (`report.pdf`)**
   - DormFix is C.0, a role-based routine/non-emergency student-housing maintenance system.
   - Primary external actors: Student Resident, Property Manager, Maintenance Technician; Housing Administration is an oversight stakeholder.
   - UC.1–UC.4 cover resident request, manager review/assignment, technician execution/update, and resident confirmation.
   - Planned stack: Streamlit, Python/FastAPI, SQLite, configurable language model.
   - The report explicitly stated that the Chapter 2 walking skeleton still used stubs; UI/database/live LLM were planned at that time.

2. **SYSEN 5151 Milestone 1 criteria**
   - Repository must stay aligned to system context and requirements.
   - Walking skeleton must trace to the primary modeled use case.
   - Software must not introduce unexplained capabilities beyond model/requirements.

3. **Product Description: DormFix**
   - Three primary operational roles and four maintenance categories.
   - Assisted intake, dispatch/tracking, technician updates, resident resolution/reopen.
   - Emergency response, automated dispatch, parts purchasing, billing and rent integration are out of scope.
   - AI suggestions remain editable and the standard/manual path remains usable if the model is unavailable.

4. **Existing GitHub repository (`sysen5151-fall2026/Team3-DormFix`)**
   - Existing main branch contained the Chapter 2 stub and preserved module boundaries.
   - Original runnable command: `python app.py` for a canned UC.1 scenario.
   - Existing `docs/walking-skeleton.md` documented 11 internal interactions and explicitly said there was no production confirmation validation, persistence, authentication, error handling, retries or logging.
   - Existing manager/technician modules were placeholders.

5. **Open Chapter 3 specification PR #3**
   - 15 needs / 34 stakeholder requirements and acceptance obligations.
   - Six lifecycle states: Submitted, Assigned, In progress, Awaiting resident confirmation, Closed, Reopened.
   - Access boundaries: resident own tickets; technician assigned tickets; manager all tickets; Administration aggregates; ordinary IT diagnostics.
   - AI advisory boundary: category/summary/location/access/missing-information suggestions only; priority and assignment stay with the manager.
   - Manual fallback, commit-before-acknowledgement, duplicate-safe retry, resident-confirmed closure, 72-hour manager exception, event history, restart persistence, backup/restore and role maintenance.

6. **SYSEN 5151 / SYSEN 5930 WBS and schedule materials**
   - Integrated prototype work packages include resident intake/manual path, durable ticket service/history, manager assignment, technician workflow, resident closure/reopening, oversight/operations and a release candidate.
   - Later verification/validation gates require objective evidence and explicitly warn against claiming planned acceptance evidence as already completed.

## Important implementation honesty

This delivery therefore labels the original Chapter 2 capabilities as historical stubs and the expanded capabilities as **implemented in this demonstration build**. It does not rewrite the project history to claim those capabilities existed earlier.
