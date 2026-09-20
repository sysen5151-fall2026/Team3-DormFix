"""DormFix service participants for one nominal, entirely stubbed UC.1 scenario."""

from intake_model import structure_request
from ticket_store import create_ticket


def begin_request(description: str) -> dict:
    """Return the stub extraction and a canned prompt; do not create a ticket."""
    return {
        "draft": structure_request(description),
        "prompt": "Please provide the location and access availability.",
    }


def complete_request(draft: dict, supplemental_information: dict) -> dict:
    """Return a fixed complete draft for this scenario, without processing input.

    The arguments preserve the modeled interface. This is deliberately a canned
    response, not field validation, extraction, or production request processing.
    """
    return {
        "description": "The sink is leaking.",
        "category": "plumbing",
        "location": "Example residence, Room 101",
        "availability": "Example access window",
        "missing_fields": [],
    }


def submit_maintenance_request(confirmed_draft: dict) -> dict:
    """Return a stub ticket after the separate resident submission call."""
    return {
        "message": "Maintenance request submitted.",
        "ticket": create_ticket(confirmed_draft),
    }
