# DormFix

SYSEN 5151 Fall 2026 | Team 3. Work in progress, not a final submission.

## Operational Concept

DormFix supports the complete routine student-housing maintenance process from initial issue reporting through repair confirmation. A Student Resident reports a routine, non-emergency maintenance issue through DormFix. DormFix assists the resident by structuring the report, extracting relevant information such as issue category, location, and availability, and identifying missing information that should be clarified before submission.

After the resident reviews and submits the structured request, DormFix creates a shared maintenance ticket. A Property Manager reviews the ticket, confirms priority, assigns a Maintenance Technician, and monitors outstanding work. The Maintenance Technician reviews the assigned request, performs the repair, and records progress or completion notes. DormFix maintains the ticket status history throughout the process.

After repair completion is recorded, the Student Resident reviews the result and confirms whether the issue has been resolved. A successfully resolved request is closed, while an unresolved request may be reopened for additional work.

DormFix is limited to routine, non-emergency maintenance. Emergency response, automated dispatch, parts purchasing, billing, and rent-system integration are outside the current project scope.

## Run the Chapter 2 walking skeleton

With Python 3.12 available, run this command from the repository root:

```sh
python app.py
```

The current entry point uses only the Python standard library and the local
stub modules. It does not require installing the planned web-framework
dependencies or starting LM Studio. See
[the canned scenario and expected result](docs/walking-skeleton.md#run-the-canned-scenario)
for the output of the fixed example.

## Team workflow

Make changes on a branch and open a pull request targeting `main`.
Obtain approval from at least one other team member before merging the pull request.
Each team member must make at least one commit personally.
