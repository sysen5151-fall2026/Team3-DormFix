from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import DB_PATH


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def db_path() -> Path:
    p = Path(DB_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@contextmanager
def connect():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(reset: bool = False) -> None:
    p = db_path()
    if reset and p.exists():
        p.unlink()
    with connect() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                submission_key TEXT NOT NULL UNIQUE,
                resident_id TEXT NOT NULL,
                description TEXT NOT NULL,
                building TEXT NOT NULL,
                room TEXT NOT NULL,
                category TEXT NOT NULL,
                availability TEXT NOT NULL,
                resident_contact TEXT,
                status TEXT NOT NULL,
                priority TEXT,
                assigned_technician TEXT,
                submitted_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                awaiting_since TEXT,
                ai_suggestions TEXT NOT NULL DEFAULT '{}',
                pending_access TEXT,
                needs_information INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(resident_id) REFERENCES accounts(account_id)
            );
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                ts TEXT NOT NULL,
                notes TEXT,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
            );
            CREATE TABLE IF NOT EXISTS diagnostics (
                diagnostic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                state TEXT NOT NULL,
                ts TEXT NOT NULL,
                detail TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS account_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                action TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                ts TEXT NOT NULL
            );
            """
        )
    seed_demo_accounts()


def seed_demo_accounts() -> None:
    demo = [
        ("resident.alex", "Alex Resident", "Resident"),
        ("resident.sam", "Sam Resident", "Resident"),
        ("manager.morgan", "Morgan Manager", "Manager"),
        ("tech.taylor", "Taylor Technician", "Technician"),
        ("tech.jordan", "Jordan Technician", "Technician"),
        ("admin.housing", "Housing Administration", "Administration"),
        ("it.support", "IT Support", "IT Support"),
    ]
    with connect() as c:
        for account_id, name, role in demo:
            c.execute(
                "INSERT OR IGNORE INTO accounts(account_id,display_name,role,active,created_at) VALUES(?,?,?,?,?)",
                (account_id, name, role, 1, utcnow()),
            )


def rowdict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    d = dict(row)
    for key in ("ai_suggestions", "pending_access"):
        if key in d and d[key]:
            try:
                d[key] = json.loads(d[key])
            except Exception:
                pass
    d["needs_information"] = bool(d.get("needs_information", 0))
    return d


def list_accounts(active_only: bool = False) -> list[dict[str, Any]]:
    q = "SELECT * FROM accounts" + (" WHERE active=1" if active_only else "") + " ORDER BY role, display_name"
    with connect() as c:
        return [dict(r) for r in c.execute(q).fetchall()]


def get_account(account_id: str) -> dict[str, Any] | None:
    with connect() as c:
        r = c.execute("SELECT * FROM accounts WHERE account_id=?", (account_id,)).fetchone()
        return dict(r) if r else None


def upsert_account(actor_id: str, account_id: str, display_name: str, role: str, active: bool = True) -> None:
    old = get_account(account_id)
    with connect() as c:
        c.execute(
            "INSERT INTO accounts(account_id,display_name,role,active,created_at) VALUES(?,?,?,?,?) "
            "ON CONFLICT(account_id) DO UPDATE SET display_name=excluded.display_name, role=excluded.role, active=excluded.active",
            (account_id, display_name, role, int(active), utcnow()),
        )
        c.execute(
            "INSERT INTO account_events(actor_id,target_id,action,old_value,new_value,ts) VALUES(?,?,?,?,?,?)",
            (actor_id, account_id, "account_upsert", json.dumps(old, default=str) if old else None,
             json.dumps({"display_name": display_name, "role": role, "active": active}), utcnow()),
        )


def set_account_active(actor_id: str, account_id: str, active: bool) -> None:
    old = get_account(account_id)
    if not old:
        raise KeyError(account_id)
    with connect() as c:
        c.execute("UPDATE accounts SET active=? WHERE account_id=?", (int(active), account_id))
        c.execute(
            "INSERT INTO account_events(actor_id,target_id,action,old_value,new_value,ts) VALUES(?,?,?,?,?,?)",
            (actor_id, account_id, "active_change", str(bool(old["active"])), str(active), utcnow()),
        )


def next_ticket_id(c: sqlite3.Connection) -> str:
    n = c.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] + 1
    return f"DORMFIX-{n:04d}"


def create_ticket(*, submission_key: str, resident_id: str, request: dict[str, Any], ai_suggestions: dict[str, Any]) -> dict[str, Any]:
    now = utcnow()
    with connect() as c:
        existing = c.execute("SELECT * FROM tickets WHERE submission_key=?", (submission_key,)).fetchone()
        if existing:
            return rowdict(existing)  # idempotent retry
        ticket_id = next_ticket_id(c)
        c.execute(
            """INSERT INTO tickets(ticket_id,submission_key,resident_id,description,building,room,category,availability,
               resident_contact,status,priority,assigned_technician,submitted_at,updated_at,awaiting_since,ai_suggestions,
               pending_access,needs_information) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ticket_id, submission_key, resident_id, request["description"], request["building"], request["room"],
             request["category"], request["availability"], request.get("resident_contact"), "Submitted", None, None,
             now, now, None, json.dumps(ai_suggestions), None, 0),
        )
        c.execute(
            "INSERT INTO events(ticket_id,event_type,actor_id,ts,notes) VALUES(?,?,?,?,?)",
            (ticket_id, "Submitted", resident_id, now, "Resident confirmed structured request"),
        )
        return rowdict(c.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone())


def get_ticket(ticket_id: str) -> dict[str, Any] | None:
    with connect() as c:
        return rowdict(c.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone())


def list_tickets(where: str = "", params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    q = "SELECT * FROM tickets"
    if where:
        q += " WHERE " + where
    q += " ORDER BY updated_at DESC"
    with connect() as c:
        return [rowdict(r) for r in c.execute(q, params).fetchall()]


def update_ticket(ticket_id: str, actor_id: str, changes: dict[str, Any], event_type: str, notes: str | None = None) -> dict[str, Any]:
    allowed = {"category","availability","status","priority","assigned_technician","awaiting_since","pending_access","needs_information"}
    unknown = set(changes) - allowed
    if unknown:
        raise ValueError(f"Unsupported fields: {sorted(unknown)}")
    with connect() as c:
        row = c.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone()
        if not row:
            raise KeyError(ticket_id)
        current = dict(row)
        now = utcnow()
        for field, value in changes.items():
            old = current.get(field)
            db_value = json.dumps(value) if field == "pending_access" and value is not None else value
            c.execute(f"UPDATE tickets SET {field}=?, updated_at=? WHERE ticket_id=?", (db_value, now, ticket_id))
            if str(old) != str(db_value):
                c.execute(
                    "INSERT INTO events(ticket_id,event_type,actor_id,ts,notes,field_name,old_value,new_value) VALUES(?,?,?,?,?,?,?,?)",
                    (ticket_id, event_type, actor_id, now, notes, field, None if old is None else str(old), None if db_value is None else str(db_value)),
                )
        if not changes:
            c.execute("INSERT INTO events(ticket_id,event_type,actor_id,ts,notes) VALUES(?,?,?,?,?)", (ticket_id,event_type,actor_id,now,notes))
        return rowdict(c.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone())


def add_event(ticket_id: str, event_type: str, actor_id: str, notes: str = "") -> None:
    with connect() as c:
        c.execute("INSERT INTO events(ticket_id,event_type,actor_id,ts,notes) VALUES(?,?,?,?,?)", (ticket_id,event_type,actor_id,utcnow(),notes))
        c.execute("UPDATE tickets SET updated_at=? WHERE ticket_id=?", (utcnow(), ticket_id))


def events(ticket_id: str) -> list[dict[str, Any]]:
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM events WHERE ticket_id=? ORDER BY event_id", (ticket_id,)).fetchall()]


def record_diagnostic(kind: str, state: str, detail: str) -> None:
    # Keep this intentionally non-sensitive: caller must not pass resident content.
    with connect() as c:
        c.execute("INSERT INTO diagnostics(kind,state,ts,detail) VALUES(?,?,?,?)", (kind,state,utcnow(),detail))


def diagnostics(limit: int = 50) -> list[dict[str, Any]]:
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM diagnostics ORDER BY diagnostic_id DESC LIMIT ?", (limit,)).fetchall()]


def aggregate_summary() -> dict[str, Any]:
    with connect() as c:
        rows = c.execute("SELECT status, COUNT(*) AS n FROM tickets GROUP BY status").fetchall()
        total = c.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        unfinished = c.execute("SELECT COUNT(*) FROM tickets WHERE status != 'Closed'").fetchone()[0]
        return {"cohort": "all demo tickets", "total": total, "unfinished": unfinished, "by_status": {r["status"]: r["n"] for r in rows}}


def backup_database(destination: str | Path) -> Path:
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with connect() as c:
        target = sqlite3.connect(dest)
        try:
            c.backup(target)
        finally:
            target.close()
    return dest


def restore_database(source: str | Path) -> None:
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(source)
    p = db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, p)
