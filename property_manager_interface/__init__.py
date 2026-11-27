"""Property-manager adapter for assignment and work-queue actions."""
from ticket_service import manager_assign, manager_correct_ticket, manager_open, manager_pending
__all__ = ["manager_assign", "manager_correct_ticket", "manager_open", "manager_pending"]
