"""Stub ticket data participant for the DormFix walking skeleton."""


def create_ticket(structured_request: dict) -> dict:
    """Return a hard-coded ticket record without database access."""
    return {
        "ticket_id": "DORMFIX-001",
        "status": "submitted",
        "request": structured_request,
    }
