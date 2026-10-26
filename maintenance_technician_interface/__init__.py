"""Maintenance-technician adapter for assigned-work actions."""
from ticket_service import technician_complete, technician_progress, technician_return, propose_access_change
__all__ = ["technician_complete", "technician_progress", "technician_return", "propose_access_change"]
