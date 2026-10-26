from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from config import LIFECYCLE_STATES, SUPPORTED_CATEGORIES
from ticket_service import (
    administration_summary,
    begin_request,
    demo_accounts,
    get_visible_ticket,
    initialize,
    list_visible_tickets,
    manager_assign,
    manager_coordinate_access_change,
    manager_correct_ticket,
    manager_exception_close,
    manager_open,
    manager_pending,
    propose_access_change,
    resident_confirm_access_change,
    resident_confirm_resolution,
    resident_reopen,
    submit_maintenance_request,
    support_backup,
    support_create_or_update_account,
    support_health,
    support_set_account_active,
    technician_complete,
    technician_progress,
    technician_return,
)

st.set_page_config(page_title="DormFix", page_icon="🛠️", layout="wide")
initialize()

st.title("🛠️ DormFix")
st.caption("Student Housing Maintenance & Collaboration System · Cornell SYSEN 5151 / SYSEN 5930 demonstration prototype")
st.info("Prototype boundary: routine, non-emergency maintenance only. No emergency dispatch, billing, parts purchasing, or rent-system integration is provided.")

accounts = demo_accounts()
active_accounts = [a for a in accounts if a["active"]]
labels = {f"{a['display_name']} · {a['role']} ({a['account_id']})": a for a in active_accounts}
selected = st.sidebar.selectbox("Demo identity", list(labels))
account = labels[selected]
actor_id = account["account_id"]
role = account["role"]
st.sidebar.write(f"**Role:** {role}")
st.sidebar.caption("Demo identities are seeded locally; this is not production authentication.")


def status_badge(status: str) -> str:
    icons = {
        "Submitted": "🟦", "Assigned": "🟪", "In progress": "🟨",
        "Awaiting resident confirmation": "🟧", "Closed": "🟩", "Reopened": "🟥",
    }
    return f"{icons.get(status, '⬜')} {status}"


def ticket_card(t: dict):
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.markdown(f"### {t['ticket_id']}")
        c2.write(status_badge(t["status"]))
        c3.write(f"**{t.get('category','')}**")
        st.write(t["description"])
        st.caption(f"{t['building']} · {t['room']} · Access: {t['availability']}")
        st.write(f"**Assigned:** {t.get('assigned_technician') or 'Unassigned'}")
        st.write(f"**Next step:** {t.get('next_step','')}")
        st.caption(f"Latest update: {t['updated_at']}")


def render_history(t: dict):
    with st.expander("Audit history"):
        for e in t.get("history", []):
            detail = e.get("notes") or ""
            if e.get("field_name"):
                detail += f" | {e['field_name']}: {e.get('old_value')} → {e.get('new_value')}"
            st.write(f"**{e['event_type']}** · {e['actor_id']} · {e['ts']}")
            if detail:
                st.caption(detail)


if role == "Resident":
    tab1, tab2 = st.tabs(["Report maintenance", "My tickets"])
    with tab1:
        st.subheader("Report a routine maintenance issue")
        st.caption("AI assistance is advisory. You review and edit the structured draft before submission.")
        with st.form("resident-intake"):
            description = st.text_area("Describe the problem", placeholder="Example: The kitchen sink is leaking under the cabinet.")
            c1, c2 = st.columns(2)
            building = c1.text_input("Building")
            room = c2.text_input("Room / unit")
            category = st.selectbox("Category (optional before assistance)", [""] + list(SUPPORTED_CATEGORIES))
            availability = st.text_input("Access availability", placeholder="Example: Weekdays after 3 PM")
            contact = st.text_input("Resident contact (manager-only field, optional)")
            use_ai = st.checkbox("Use configured AI assistance if available", value=True)
            prepare = st.form_submit_button("Prepare structured draft")
        if prepare:
            result = begin_request(description, {
                "building": building, "room": room, "category": category,
                "availability": availability, "resident_contact": contact,
            }, use_ai=use_ai)
            st.session_state["draft_result"] = result
            st.session_state["submission_key"] = str(uuid.uuid4())

        result = st.session_state.get("draft_result")
        if result:
            if result["emergency_warning"]:
                st.error("Possible emergency keyword detected. DormFix does not dispatch emergency response. Use the appropriate local emergency or housing emergency channel. The prototype does not provide a live contact number.")
            if result["manual_fallback"]:
                st.warning("Live model assistance is unavailable or not configured. Manual entry remains available; deterministic local suggestions may be shown as a convenience.")
            if result["missing_fields"]:
                st.warning("Missing required information: " + ", ".join(result["missing_fields"]))
            st.markdown("#### Resident review — edit before confirmation")
            draft = result["draft"]
            with st.form("confirm-draft"):
                d_description = st.text_area("Description", value=draft["description"])
                c1, c2 = st.columns(2)
                d_building = c1.text_input("Building", value=draft["building"])
                d_room = c2.text_input("Room / unit", value=draft["room"])
                d_category = st.selectbox("Category", list(SUPPORTED_CATEGORIES), index=list(SUPPORTED_CATEGORIES).index(draft["category"]) if draft["category"] in SUPPORTED_CATEGORIES else 0)
                d_availability = st.text_input("Access availability", value=draft["availability"])
                d_contact = st.text_input("Resident contact", value=draft.get("resident_contact", ""))
                confirmed = st.checkbox("I reviewed this structured request and confirm it for submission.")
                submit = st.form_submit_button("Submit maintenance request")
            if submit:
                if not confirmed:
                    st.error("Explicit resident confirmation is required before ticket creation.")
                else:
                    try:
                        ticket = submit_maintenance_request(actor_id, {
                            "description": d_description, "building": d_building, "room": d_room,
                            "category": d_category, "availability": d_availability, "resident_contact": d_contact,
                        }, st.session_state["submission_key"], result.get("suggestions"))
                        st.success(f"Committed ticket {ticket['ticket_id']} created.")
                        st.session_state.pop("draft_result", None)
                    except Exception as exc:
                        st.error(str(exc))

    with tab2:
        tickets = list_visible_tickets(actor_id)
        if not tickets:
            st.write("No tickets yet.")
        for t in tickets:
            ticket_card(t)
            render_history(t)
            if t.get("pending_access"):
                pending = t["pending_access"]
                st.warning(f"Pending access change: {pending.get('coordinated_option') or pending.get('proposed')}")
                if pending.get("manager_coordinated"):
                    a, b = st.columns(2)
                    if a.button("Confirm new access arrangement", key=f"acc-{t['ticket_id']}"):
                        resident_confirm_access_change(actor_id, t["ticket_id"], True); st.rerun()
                    if b.button("Keep current access arrangement", key=f"dec-{t['ticket_id']}"):
                        resident_confirm_access_change(actor_id, t["ticket_id"], False); st.rerun()
            if t["status"] == "Awaiting resident confirmation":
                note = st.text_input("Resolution note", key=f"res-note-{t['ticket_id']}")
                a, b = st.columns(2)
                if a.button("Confirm resolved and close", key=f"close-{t['ticket_id']}"):
                    resident_confirm_resolution(actor_id, t["ticket_id"], True, note); st.rerun()
                if b.button("Not resolved — reopen", key=f"reopen-await-{t['ticket_id']}"):
                    resident_confirm_resolution(actor_id, t["ticket_id"], False, note); st.rerun()
            elif t["status"] == "Closed":
                reason = st.text_input("Reason to reopen", key=f"reopen-reason-{t['ticket_id']}")
                if st.button("Reopen closed ticket", key=f"reopen-{t['ticket_id']}"):
                    try:
                        resident_reopen(actor_id, t["ticket_id"], reason); st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

elif role == "Manager":
    st.subheader("Property Manager workspace")
    pending = manager_pending(actor_id)
    open_work = manager_open(actor_id)
    c1, c2 = st.columns(2)
    c1.metric("Pending decisions", len(pending))
    c2.metric("Assigned / active work", len(open_work))
    all_tickets = list_visible_tickets(actor_id)
    if not all_tickets:
        st.write("No tickets yet. Create one from a Resident demo identity first.")
    else:
        tid = st.selectbox("Select ticket", [t["ticket_id"] for t in all_tickets])
        t = get_visible_ticket(actor_id, tid)
        ticket_card(t); render_history(t)
        if t["status"] in {"Submitted", "Reopened"}:
            st.markdown("#### Review and assign")
            category = st.selectbox("Correct category if needed", list(SUPPORTED_CATEGORIES), index=list(SUPPORTED_CATEGORIES).index(t["category"]))
            if category != t["category"] and st.button("Save category correction"):
                manager_correct_ticket(actor_id, tid, "category", category); st.rerun()
            techs = [a for a in active_accounts if a["role"] == "Technician"]
            tech = st.selectbox("Technician", [a["account_id"] for a in techs])
            priority = st.selectbox("Manager-selected priority", ["Routine", "Normal", "High"])
            if st.button("Assign technician"):
                try:
                    manager_assign(actor_id, tid, tech, priority); st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        if t.get("pending_access"):
            st.markdown("#### Coordinate technician-proposed access change")
            st.json(t["pending_access"])
            option = st.text_input("Coordinated option", value=t["pending_access"].get("proposed", ""))
            if st.button("Send access option for resident confirmation"):
                manager_coordinate_access_change(actor_id, tid, option); st.rerun()
        if t["status"] == "Awaiting resident confirmation":
            if st.button("Attempt 72-hour no-response exception closure"):
                try:
                    manager_exception_close(actor_id, tid); st.rerun()
                except Exception as exc:
                    st.error(str(exc))

elif role == "Technician":
    st.subheader("Maintenance Technician workspace")
    tickets = list_visible_tickets(actor_id)
    if not tickets:
        st.write("No assigned tickets.")
    for t in tickets:
        ticket_card(t); render_history(t)
        note = st.text_input("Progress / completion note", key=f"tech-note-{t['ticket_id']}")
        a, b, c = st.columns(3)
        if a.button("Start / update progress", key=f"progress-{t['ticket_id']}"):
            technician_progress(actor_id, t["ticket_id"], note or "Work in progress"); st.rerun()
        if b.button("Mark work complete", key=f"complete-{t['ticket_id']}"):
            technician_complete(actor_id, t["ticket_id"], note or "Repair completed"); st.rerun()
        reason = st.text_input("Blocked-work return reason", key=f"return-reason-{t['ticket_id']}")
        if c.button("Return to manager", key=f"return-{t['ticket_id']}"):
            try:
                technician_return(actor_id, t["ticket_id"], reason); st.rerun()
            except Exception as exc:
                st.error(str(exc))
        proposed = st.text_input("Propose a different access arrangement", key=f"access-{t['ticket_id']}")
        if st.button("Propose access change", key=f"propose-access-{t['ticket_id']}"):
            try:
                propose_access_change(actor_id, t["ticket_id"], proposed); st.rerun()
            except Exception as exc:
                st.error(str(exc))

elif role == "Administration":
    st.subheader("Housing Administration — privacy-preserving summary")
    summary = administration_summary(actor_id)
    c1, c2 = st.columns(2)
    c1.metric("Total demo tickets", summary["total"])
    c2.metric("Unfinished", summary["unfinished"])
    st.bar_chart(summary["by_status"])
    st.caption("Administration intentionally receives aggregate counts only; no resident room/access/contact or ticket-history view is exposed here.")

elif role == "IT Support":
    tab1, tab2, tab3 = st.tabs(["Health & diagnostics", "Backup", "Accounts / roles"])
    with tab1:
        st.json(support_health(actor_id))
        st.caption("Diagnostics are designed to omit resident descriptions, contacts, and photos.")
    with tab2:
        if st.button("Create SQLite backup"):
            dest = Path("data/backups") / f"dormfix-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.db"
            p = support_backup(actor_id, dest)
            st.success(f"Backup created: {p}")
    with tab3:
        st.dataframe(demo_accounts(), use_container_width=True, hide_index=True)
        with st.form("account-form"):
            account_id = st.text_input("Account ID")
            name = st.text_input("Display name")
            role_new = st.selectbox("Role", ["Resident", "Technician", "Manager", "Administration", "IT Support"])
            active = st.checkbox("Active", value=True)
            save = st.form_submit_button("Create / update account")
        if save:
            support_create_or_update_account(actor_id, account_id, name, role_new, active)
            st.success("Account change recorded."); st.rerun()
        account_to_change = st.selectbox("Activate/deactivate existing account", [a["account_id"] for a in demo_accounts()])
        current = next(a for a in demo_accounts() if a["account_id"] == account_to_change)
        if st.button("Toggle active state"):
            support_set_account_active(actor_id, account_to_change, not bool(current["active"])); st.rerun()
