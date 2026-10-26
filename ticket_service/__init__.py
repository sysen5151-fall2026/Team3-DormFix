from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import LIFECYCLE_STATES, ROLES, SUPPORTED_CATEGORIES
from intake_model import structure_request
from ticket_store import (
    add_event,
    aggregate_summary,
    backup_database,
    diagnostics,
    events,
    get_account,
    get_ticket,
    init_db,
    list_accounts,
    list_tickets,
    record_diagnostic,
    set_account_active,
    update_ticket,
    upsert_account,
    create_ticket,
)

NEXT_STEP = {
    "Submitted": "Property manager reviews completeness, priority, and assignment.",
    "Assigned": "Assigned technician reviews job details and starts work.",
    "In progress": "Technician records progress or marks work complete.",
    "Awaiting resident confirmation": "Resident confirms resolution or reopens the request.",
    "Closed": "No action required unless the resident needs to reopen the issue.",
    "Reopened": "Property manager reviews the returned/reopened request and reassigns as needed.",
}


def initialize(reset: bool = False) -> None:
    init_db(reset=reset)


def require_account(actor_id: str, *roles: str) -> dict[str, Any]:
    account = get_account(actor_id)
    if not account or not account["active"]:
        raise PermissionError("Inactive or unknown account")
    if roles and account["role"] not in roles:
        raise PermissionError(f"Role {account['role']} is not allowed")
    return account


def begin_request(description: str, provided: dict[str, Any] | None = None, use_ai: bool = True) -> dict[str, Any]:
    return structure_request(description, provided, use_ai=use_ai)


def submit_maintenance_request(resident_id: str, confirmed_draft: dict[str, Any], submission_key: str, suggestions: dict[str, Any] | None = None) -> dict[str, Any]:
    require_account(resident_id, "Resident")
    required = ("description", "building", "room", "category", "availability")
    missing = [k for k in required if not str(confirmed_draft.get(k, "")).strip()]
    if missing:
        raise ValueError(f"Missing required information: {', '.join(missing)}")
    if confirmed_draft["category"] not in SUPPORTED_CATEGORIES:
        raise ValueError("Unsupported category")
    # Ticket ID is returned only after SQLite commit succeeds.
    return create_ticket(
        submission_key=submission_key,
        resident_id=resident_id,
        request=confirmed_draft,
        ai_suggestions=suggestions or {},
    )


def readiness(ticket: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = [k for k in ("description", "building", "room", "category", "availability") if not ticket.get(k)]
    return (not missing, missing)


def manager_correct_ticket(manager_id: str, ticket_id: str, field: str, new_value: str) -> dict[str, Any]:
    require_account(manager_id, "Manager")
    if field not in {"category", "availability"}:
        raise ValueError("Only category and availability corrections are exposed in this prototype")
    if field == "category" and new_value not in SUPPORTED_CATEGORIES:
        raise ValueError("Unsupported category")
    return update_ticket(ticket_id, manager_id, {field: new_value}, "Manager correction", f"Manager corrected {field}")


def manager_assign(manager_id: str, ticket_id: str, technician_id: str, priority: str) -> dict[str, Any]:
    require_account(manager_id, "Manager")
    tech = require_account(technician_id, "Technician")
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise KeyError(ticket_id)
    ok, missing = readiness(ticket)
    if not ok:
        update_ticket(ticket_id, manager_id, {"needs_information": True}, "Needs information", ",".join(missing))
        raise ValueError(f"Assignment blocked; missing/unusable fields: {', '.join(missing)}")
    if ticket["status"] not in {"Submitted", "Reopened"}:
        raise ValueError("Only Submitted or Reopened tickets can be assigned")
    return update_ticket(
        ticket_id,
        manager_id,
        {"priority": priority, "assigned_technician": tech["account_id"], "status": "Assigned", "needs_information": False},
        "Manager assignment",
        "Manager confirmed priority and technician assignment",
    )


def technician_progress(technician_id: str, ticket_id: str, note: str) -> dict[str, Any]:
    require_account(technician_id, "Technician")
    ticket = _require_assigned_tech(technician_id, ticket_id)
    if ticket["status"] not in {"Assigned", "In progress"}:
        raise ValueError("Ticket is not available for progress update")
    result = update_ticket(ticket_id, technician_id, {"status": "In progress"}, "Technician progress", note)
    add_event(ticket_id, "Progress note", technician_id, note)
    return result


def technician_complete(technician_id: str, ticket_id: str, note: str) -> dict[str, Any]:
    require_account(technician_id, "Technician")
    _require_assigned_tech(technician_id, ticket_id)
    now = datetime.now(timezone.utc).isoformat()
    result = update_ticket(
        ticket_id,
        technician_id,
        {"status": "Awaiting resident confirmation", "awaiting_since": now},
        "Technician completed work",
        note,
    )
    add_event(ticket_id, "Completion note", technician_id, note)
    return result


def technician_return(technician_id: str, ticket_id: str, reason: str) -> dict[str, Any]:
    require_account(technician_id, "Technician")
    _require_assigned_tech(technician_id, ticket_id)
    if not reason.strip():
        raise ValueError("A reason is required to return blocked work")
    return update_ticket(
        ticket_id,
        technician_id,
        {"status": "Reopened", "assigned_technician": None},
        "Returned by technician",
        reason.strip(),
    )


def propose_access_change(technician_id: str, ticket_id: str, proposed: str) -> dict[str, Any]:
    require_account(technician_id, "Technician")
    _require_assigned_tech(technician_id, ticket_id)
    if not proposed.strip():
        raise ValueError("Proposed access arrangement is required")
    pending = {"proposed": proposed.strip(), "manager_coordinated": False, "resident_confirmed": False}
    return update_ticket(ticket_id, technician_id, {"pending_access": pending}, "Access change proposed", proposed.strip())


def manager_coordinate_access_change(manager_id: str, ticket_id: str, option: str) -> dict[str, Any]:
    require_account(manager_id, "Manager")
    ticket = get_ticket(ticket_id)
    if not ticket or not ticket.get("pending_access"):
        raise ValueError("No technician access-change proposal exists")
    pending = dict(ticket["pending_access"])
    pending.update({"coordinated_option": option.strip(), "manager_coordinated": True})
    return update_ticket(ticket_id, manager_id, {"pending_access": pending}, "Access change coordinated", option.strip())


def resident_confirm_access_change(resident_id: str, ticket_id: str, accept: bool) -> dict[str, Any]:
    require_account(resident_id, "Resident")
    ticket = _require_owner(resident_id, ticket_id)
    pending = ticket.get("pending_access")
    if not pending or not pending.get("manager_coordinated"):
        raise ValueError("No coordinated access change is awaiting confirmation")
    if accept:
        new_availability = pending.get("coordinated_option") or pending.get("proposed")
        return update_ticket(ticket_id, resident_id, {"availability": new_availability, "pending_access": None}, "Access change confirmed", new_availability)
    return update_ticket(ticket_id, resident_id, {"pending_access": None}, "Access change declined", "Resident kept existing arrangement")


def resident_confirm_resolution(resident_id: str, ticket_id: str, resolved: bool, reason: str = "") -> dict[str, Any]:
    require_account(resident_id, "Resident")
    ticket = _require_owner(resident_id, ticket_id)
    if ticket["status"] != "Awaiting resident confirmation":
        raise ValueError("Ticket is not awaiting resident confirmation")
    if resolved:
        return update_ticket(ticket_id, resident_id, {"status": "Closed"}, "Resident confirmed resolution", reason or "Resolved")
    return update_ticket(ticket_id, resident_id, {"status": "Reopened", "assigned_technician": None}, "Resident reopened", reason or "Issue unresolved")


def resident_reopen(resident_id: str, ticket_id: str, reason: str) -> dict[str, Any]:
    require_account(resident_id, "Resident")
    ticket = _require_owner(resident_id, ticket_id)
    if ticket["status"] != "Closed":
        raise ValueError("Only a closed ticket can be reopened through this action")
    if not reason.strip():
        raise ValueError("Reopen reason is required")
    return update_ticket(ticket_id, resident_id, {"status": "Reopened", "assigned_technician": None}, "Resident reopened", reason.strip())


def manager_exception_close(manager_id: str, ticket_id: str, now: datetime | None = None) -> dict[str, Any]:
    require_account(manager_id, "Manager")
    ticket = get_ticket(ticket_id)
    if not ticket or ticket["status"] != "Awaiting resident confirmation" or not ticket.get("awaiting_since"):
        raise ValueError("Ticket is not eligible for exception closure")
    start = datetime.fromisoformat(ticket["awaiting_since"])
    current = now or datetime.now(timezone.utc)
    if (current - start).total_seconds() < 72 * 3600:
        raise ValueError("72-hour no-response threshold has not been reached")
    return update_ticket(ticket_id, manager_id, {"status": "Closed"}, "Manager exception closure", "Closed after 72 hours without resident response")


def _require_owner(resident_id: str, ticket_id: str) -> dict[str, Any]:
    ticket = get_ticket(ticket_id)
    if not ticket or ticket["resident_id"] != resident_id:
        raise PermissionError("Resident may access only owned tickets")
    return ticket


def _require_assigned_tech(technician_id: str, ticket_id: str) -> dict[str, Any]:
    ticket = get_ticket(ticket_id)
    if not ticket or ticket.get("assigned_technician") != technician_id:
        raise PermissionError("Technician may access only assigned tickets")
    return ticket


def sanitize_ticket(ticket: dict[str, Any], role: str, actor_id: str) -> dict[str, Any]:
    out = dict(ticket)
    if role == "Resident" and ticket["resident_id"] != actor_id:
        raise PermissionError("Cross-resident access denied")
    if role == "Technician" and ticket.get("assigned_technician") != actor_id:
        raise PermissionError("Unassigned technician access denied")
    if role in {"Administration", "IT Support"}:
        raise PermissionError("This role has no ticket-detail access")
    if role == "Technician":
        out.pop("resident_contact", None)
        out.pop("ai_suggestions", None)
    if role == "Resident":
        out.pop("ai_suggestions", None)
        out.pop("resident_contact", None)
    out["next_step"] = NEXT_STEP[out["status"]]
    out["history"] = events(ticket["ticket_id"])
    return out


def get_visible_ticket(actor_id: str, ticket_id: str) -> dict[str, Any]:
    acct = require_account(actor_id)
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise KeyError(ticket_id)
    return sanitize_ticket(ticket, acct["role"], actor_id)


def list_visible_tickets(actor_id: str) -> list[dict[str, Any]]:
    acct = require_account(actor_id)
    role = acct["role"]
    if role == "Resident":
        rows = list_tickets("resident_id=?", (actor_id,))
    elif role == "Technician":
        rows = list_tickets("assigned_technician=?", (actor_id,))
    elif role == "Manager":
        rows = list_tickets()
    else:
        return []
    return [sanitize_ticket(t, role, actor_id) for t in rows]


def manager_pending(manager_id: str) -> list[dict[str, Any]]:
    require_account(manager_id, "Manager")
    return list_tickets("status IN ('Submitted','Reopened')")


def manager_open(manager_id: str) -> list[dict[str, Any]]:
    require_account(manager_id, "Manager")
    return list_tickets("status IN ('Assigned','In progress','Awaiting resident confirmation')")


def administration_summary(admin_id: str) -> dict[str, Any]:
    require_account(admin_id, "Administration")
    return aggregate_summary()


def support_health(it_id: str) -> dict[str, Any]:
    require_account(it_id, "IT Support")
    ds = diagnostics(50)
    return {"service": "ok", "database": "ok", "recent_diagnostics": ds}


def support_backup(it_id: str, destination: str | Path) -> Path:
    require_account(it_id, "IT Support")
    path = backup_database(destination)
    record_diagnostic("backup", "ok", f"backup={path.name}")
    return path


def support_create_or_update_account(it_id: str, account_id: str, display_name: str, role: str, active: bool = True) -> None:
    require_account(it_id, "IT Support")
    if role not in ROLES:
        raise ValueError("Unknown role")
    upsert_account(it_id, account_id, display_name, role, active)


def support_set_account_active(it_id: str, account_id: str, active: bool) -> None:
    require_account(it_id, "IT Support")
    set_account_active(it_id, account_id, active)


def demo_accounts() -> list[dict[str, Any]]:
    return list_accounts(active_only=False)
