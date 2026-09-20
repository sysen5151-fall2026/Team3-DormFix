"""Resident-facing boundary for the three-stage, canned UC.1 scenario."""

from ticket_service import begin_request, complete_request, submit_maintenance_request


def describe_issue(description: str) -> dict:
    """Capture the description and return a draft with a missing-information prompt."""
    return begin_request(description)


def provide_information(draft: dict, supplemental_information: dict) -> dict:
    """Return the canned complete draft for resident review."""
    return complete_request(draft, supplemental_information)


def submit_issue(confirmed_draft: dict) -> dict:
    """Submit a draft only after the scenario's explicit resident confirmation."""
    return submit_maintenance_request(confirmed_draft)
