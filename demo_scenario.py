"""Command-line demonstration of UC.1–UC.4 without Streamlit."""
from __future__ import annotations
import uuid
from ticket_service import (
    begin_request, initialize, manager_assign, resident_confirm_resolution,
    submit_maintenance_request, technician_complete, technician_progress,
    get_visible_ticket,
)

initialize(reset=True)
print("DormFix integrated demo")
print("=======================")
intake = begin_request(
    "The kitchen sink is leaking under the cabinet.",
    {"building": "Demo Hall", "room": "101", "availability": "Weekdays after 3 PM"},
    use_ai=False,
)
print("1. Resident draft:", intake["draft"])
ticket = submit_maintenance_request("resident.alex", intake["draft"], str(uuid.uuid4()), intake["suggestions"])
print("2. Ticket committed:", ticket["ticket_id"], ticket["status"])
ticket = manager_assign("manager.morgan", ticket["ticket_id"], "tech.taylor", "Normal")
print("3. Manager assigned:", ticket["assigned_technician"], ticket["status"])
technician_progress("tech.taylor", ticket["ticket_id"], "Inspected supply line")
waiting = technician_complete("tech.taylor", ticket["ticket_id"], "Replaced leaking line")
print("4. Technician completed; state:", waiting["status"])
closed = resident_confirm_resolution("resident.alex", ticket["ticket_id"], True, "Repair verified")
print("5. Resident confirmed; state:", closed["status"])
view = get_visible_ticket("resident.alex", ticket["ticket_id"])
print("6. Audit events:", len(view["history"]))
print("PASS: UC.1–UC.4 demonstration completed.")
