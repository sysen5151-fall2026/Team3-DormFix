# DormFix System Context

Directions below are relative to the DormFix system boundary. The forms describe the information at the business level; they do not prescribe an API or wire format. This inventory covers the UC.1–UC.4 operational concept. The current walking skeleton implements only the canned UC.1 path, using text and Python dictionaries; the remaining exchanges are planned behavior.

## X.C.1 Student Resident

Direction: In / Out

Information entering DormFix:
- Maintenance issue description — free text.
- Location information — a text field identifying the repair location.
- Access availability — a text field describing the access window.
- Missing information responses — values for the requested information fields.
- Repair resolution confirmation — a confirmation decision associated with the ticket.

Information leaving DormFix:
- Missing-information prompts — text identifying the information still needed.
- Structured maintenance request — a draft record of request fields for resident review.
- Ticket status — a status record associated with the ticket identifier, including submission confirmation.
- Repair completion information — completion status and repair notes associated with the ticket.

## X.C.2 Property Manager

Direction: In / Out

Information entering DormFix:
- Priority decisions — a priority value associated with the ticket.
- Technician assignment decisions — an assigned technician identifier associated with the ticket.

Information leaving DormFix:
- Submitted maintenance requests — structured request records.
- Structured ticket information — ticket records containing the request fields and current status.
- Outstanding-work status — a list of open tickets and their current statuses.

## X.C.3 Maintenance Technician

Direction: In / Out

Information entering DormFix:
- Repair progress updates — status values and progress notes associated with the ticket.
- Completion status — a completion status value associated with the ticket.
- Repair notes — free-text notes associated with the ticket.

Information leaving DormFix:
- Assigned maintenance requests — ticket records identifying the assigned work.
- Issue details — the issue description and category fields within the ticket.
- Location and access information — the location and access-availability text fields within the ticket.

## X.C.4 Housing Administration

Role: External oversight stakeholder

Housing Administration does not directly participate in the nominal maintenance-request workflow. It has an interest in maintenance performance, unresolved work, and the traceability of maintenance records.

Direction and form: no direct exchange is defined for this stakeholder in the current nominal workflow; no separate oversight interface is claimed by this inventory.
