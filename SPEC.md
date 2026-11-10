# DormFix Specification

## Status

This is a working project specification. It records the current intended behavior, model links, and data expectations for DormFix. It does not claim that every behavior in this document has already been implemented or tested.

## Scope

DormFix supports routine student-housing maintenance from the first resident report through repair confirmation.

The main users are:

- Student Resident: reports a routine, non-emergency maintenance issue and later checks the result.
- Property Manager: reviews a ready ticket, sets the final priority, and assigns a Maintenance Technician.
- Maintenance Technician: performs assigned work and records progress or completion notes.

DormFix is limited to routine, non-emergency maintenance. Emergency response, automatic dispatch, parts purchasing, billing, and rent-system integration are outside the current scope.

## Needs and Acceptance Criteria

### 1.4.3 Review and Assign Maintenance Work

DormFix shall record an authorized Property Manager's priority and assignment decision after the ticket passes the readiness check. DormFix shall provide assigned-work information to the selected Maintenance Technician.

A3, **Review and Assign Maintenance Work**, is the selected system function for this work. A3 is allocated to P.3, **Work Assignment Subsystem**.

### Acceptance Criteria

- AC-1: Only an authorized Property Manager can make the final priority and technician assignment decision.
- AC-2: The ticket must have the required request information before it can be assigned.
- AC-3: An accepted manager decision records the ticket, manager, priority, selected technician, and decision time.
- AC-4: The selected technician receives the assigned-job information needed to begin work.
- AC-5: The decision remains part of the ticket history for later review.

### Related Component Requirements

- CR.1.1.4: Accept Approved Manager Decision.
- CR.1.2.1: Provide Shared Ticket and Event Record.
- CR.1.3.5: Interface with Work Assignment Subsystem.

## Data Contract

### DF.5 Shared Ticket and Event Record

The shared ticket record provides the information needed for review and assignment:

- ticket_id
- resident_id
- issue summary and category
- location
- resident availability or access information
- current ticket status
- ticket history

### DF.2 Approved Manager Decision

The approved manager decision records:

- ticket_id
- manager_id
- priority
- technician_id
- readiness_check_passed
- decision_time

### DO.3 Technician Assigned Work Information

The technician receives:

- ticket_id
- issue summary
- location
- access or availability information
- assigned priority
- manager decision time

## Model Response Contract

DormFix may use an AI model to help structure a resident's maintenance request. The model may identify the issue category, location, availability, and missing information.

The model must not make the final priority decision or select a technician. Those decisions belong to the authorized Property Manager.

A model response should return structured request help in this form:

```json
{
  "issue_category": "string",
  "location": "string or null",
  "availability": "string or null",
  "missing_fields": ["string"],
  "resident_summary": "string"
}
```

## Traceability

UC.2 Property Manager Reviews and Assigns Request
→ A3 Review and Assign Maintenance Work
→ 1.4.3 Review and Assign Maintenance Work
→ CR.1.1.4, CR.1.2.1, and CR.1.3.5
→ P.3 Work Assignment Subsystem

## Current Implementation Note

The current repository includes a walking-skeleton foundation for the early ticket-submission flow. The Property Manager assignment implementation and its automated tests are planned follow-on evidence for A3.
