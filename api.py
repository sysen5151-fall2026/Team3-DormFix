from __future__ import annotations
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from ticket_service import (
    begin_request, get_visible_ticket, initialize, list_visible_tickets,
    manager_assign, resident_confirm_resolution, submit_maintenance_request,
    technician_complete, technician_progress, technician_return,
)

initialize()
app = FastAPI(title="DormFix API", version="0.1-demo")

class IntakeBody(BaseModel):
    description: str
    building: str = ""
    room: str = ""
    category: str = ""
    availability: str = ""
    resident_contact: str = ""
    use_ai: bool = True

class SubmitBody(BaseModel):
    draft: dict[str, Any]
    submission_key: str
    suggestions: dict[str, Any] = Field(default_factory=dict)

class AssignBody(BaseModel):
    technician_id: str
    priority: str

class NoteBody(BaseModel):
    note: str = ""

class ResolutionBody(BaseModel):
    resolved: bool
    reason: str = ""


def actor(x_dormfix_actor: str | None) -> str:
    if not x_dormfix_actor:
        raise HTTPException(401, "X-DormFix-Actor header required")
    return x_dormfix_actor

@app.get("/health")
def health():
    return {"status": "ok", "scope": "demo prototype"}

@app.post("/resident/intake")
def intake(body: IntakeBody):
    return begin_request(body.description, body.model_dump(exclude={"description", "use_ai"}), body.use_ai)

@app.post("/resident/submit")
def submit(body: SubmitBody, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return submit_maintenance_request(actor(x_dormfix_actor), body.draft, body.submission_key, body.suggestions)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

@app.get("/tickets")
def tickets(x_dormfix_actor: str | None = Header(default=None)):
    try:
        return list_visible_tickets(actor(x_dormfix_actor))
    except Exception as exc:
        raise HTTPException(403, str(exc)) from exc

@app.get("/tickets/{ticket_id}")
def ticket(ticket_id: str, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return get_visible_ticket(actor(x_dormfix_actor), ticket_id)
    except Exception as exc:
        raise HTTPException(403, str(exc)) from exc

@app.post("/manager/{ticket_id}/assign")
def assign(ticket_id: str, body: AssignBody, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return manager_assign(actor(x_dormfix_actor), ticket_id, body.technician_id, body.priority)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/technician/{ticket_id}/progress")
def progress(ticket_id: str, body: NoteBody, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return technician_progress(actor(x_dormfix_actor), ticket_id, body.note)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/technician/{ticket_id}/complete")
def complete(ticket_id: str, body: NoteBody, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return technician_complete(actor(x_dormfix_actor), ticket_id, body.note)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/technician/{ticket_id}/return")
def return_job(ticket_id: str, body: NoteBody, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return technician_return(actor(x_dormfix_actor), ticket_id, body.note)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/resident/{ticket_id}/resolution")
def resolution(ticket_id: str, body: ResolutionBody, x_dormfix_actor: str | None = Header(default=None)):
    try:
        return resident_confirm_resolution(actor(x_dormfix_actor), ticket_id, body.resolved, body.reason)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc
