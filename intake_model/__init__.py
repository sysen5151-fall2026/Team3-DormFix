"""Stub language-model participant for the DormFix walking skeleton."""


def structure_request(description: str) -> dict:
    """Return hard-coded structured maintenance information."""
    return {
        "description": description,
        "category": "plumbing",
        "missing_fields": [
            "location",
            "availability",
        ],
    }
