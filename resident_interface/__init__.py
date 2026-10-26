"""Resident-facing adapter retained from the original walking-skeleton boundary."""
from ticket_service import begin_request, submit_maintenance_request


def describe_issue(description: str, provided: dict | None = None, use_ai: bool = True) -> dict:
    return begin_request(description, provided, use_ai=use_ai)


def submit_issue(resident_id: str, confirmed_draft: dict, submission_key: str, suggestions: dict | None = None) -> dict:
    return submit_maintenance_request(resident_id, confirmed_draft, submission_key, suggestions)
