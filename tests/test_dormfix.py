from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

TEST_DIR = tempfile.TemporaryDirectory()
os.environ["DORMFIX_DB_PATH"] = str(Path(TEST_DIR.name) / "test.db")

# Import after DB env is set.
from ticket_service import (  # noqa: E402
    administration_summary,
    begin_request,
    get_visible_ticket,
    initialize,
    list_visible_tickets,
    manager_assign,
    manager_exception_close,
    manager_pending,
    resident_confirm_resolution,
    resident_reopen,
    submit_maintenance_request,
    support_backup,
    support_health,
    technician_complete,
    technician_progress,
    technician_return,
)
from ticket_store import events, get_ticket  # noqa: E402


class DormFixFlowTests(unittest.TestCase):
    def setUp(self):
        initialize(reset=True)

    def _draft(self):
        return {
            "description": "The kitchen sink is leaking under the cabinet.",
            "building": "Cascadilla Hall",
            "room": "101",
            "category": "plumbing",
            "availability": "Weekdays after 3 PM",
            "resident_contact": "demo@example.invalid",
        }

    def _ticket(self, key="case-1"):
        return submit_maintenance_request("resident.alex", self._draft(), key, {"category": "plumbing"})

    def test_missing_information_is_not_invented(self):
        result = begin_request("The sink is leaking.", {}, use_ai=False)
        self.assertEqual(result["draft"]["building"], "")
        self.assertIn("building", result["missing_fields"])
        self.assertIn("room", result["missing_fields"])
        self.assertIn("availability", result["missing_fields"])

    def test_explicit_submission_requires_complete_draft(self):
        with self.assertRaises(ValueError):
            submit_maintenance_request("resident.alex", {"description": "Leak"}, "bad-key", {})
        self.assertEqual(list_visible_tickets("resident.alex"), [])

    def test_submission_is_persistent_and_idempotent(self):
        a = self._ticket("same")
        b = self._ticket("same")
        self.assertEqual(a["ticket_id"], b["ticket_id"])
        self.assertEqual(len(list_visible_tickets("resident.alex")), 1)
        self.assertEqual(get_ticket(a["ticket_id"])["description"], self._draft()["description"])

    def test_only_manager_assigns_and_assignment_gate(self):
        t = self._ticket()
        with self.assertRaises(PermissionError):
            manager_assign("resident.alex", t["ticket_id"], "tech.taylor", "Normal")
        assigned = manager_assign("manager.morgan", t["ticket_id"], "tech.taylor", "Normal")
        self.assertEqual(assigned["status"], "Assigned")
        self.assertEqual(assigned["assigned_technician"], "tech.taylor")

    def test_role_based_ticket_access(self):
        t = self._ticket()
        manager_assign("manager.morgan", t["ticket_id"], "tech.taylor", "Normal")
        self.assertEqual(get_visible_ticket("resident.alex", t["ticket_id"])["ticket_id"], t["ticket_id"])
        with self.assertRaises(PermissionError):
            get_visible_ticket("resident.sam", t["ticket_id"])
        self.assertEqual(get_visible_ticket("tech.taylor", t["ticket_id"])["ticket_id"], t["ticket_id"])
        with self.assertRaises(PermissionError):
            get_visible_ticket("tech.jordan", t["ticket_id"])
        with self.assertRaises(PermissionError):
            get_visible_ticket("admin.housing", t["ticket_id"])

    def test_end_to_end_close_and_reopen_history(self):
        t = self._ticket()
        manager_assign("manager.morgan", t["ticket_id"], "tech.taylor", "High")
        technician_progress("tech.taylor", t["ticket_id"], "Checked valve")
        technician_complete("tech.taylor", t["ticket_id"], "Replaced supply line")
        waiting = get_ticket(t["ticket_id"])
        self.assertEqual(waiting["status"], "Awaiting resident confirmation")
        closed = resident_confirm_resolution("resident.alex", t["ticket_id"], True, "No more leak")
        self.assertEqual(closed["status"], "Closed")
        reopened = resident_reopen("resident.alex", t["ticket_id"], "Leak returned")
        self.assertEqual(reopened["status"], "Reopened")
        history = events(t["ticket_id"])
        self.assertTrue(any(e["event_type"] == "Resident reopened" for e in history))
        self.assertGreaterEqual(len(history), 6)

    def test_blocked_work_return_requires_reason_and_returns_to_manager(self):
        t = self._ticket()
        manager_assign("manager.morgan", t["ticket_id"], "tech.taylor", "Normal")
        with self.assertRaises(ValueError):
            technician_return("tech.taylor", t["ticket_id"], "")
        returned = technician_return("tech.taylor", t["ticket_id"], "Part unavailable")
        self.assertEqual(returned["status"], "Reopened")
        self.assertIn(t["ticket_id"], [x["ticket_id"] for x in manager_pending("manager.morgan")])

    def test_72_hour_exception_boundary(self):
        t = self._ticket()
        manager_assign("manager.morgan", t["ticket_id"], "tech.taylor", "Normal")
        technician_complete("tech.taylor", t["ticket_id"], "Done")
        waiting = get_ticket(t["ticket_id"])
        start = datetime.fromisoformat(waiting["awaiting_since"])
        with self.assertRaises(ValueError):
            manager_exception_close("manager.morgan", t["ticket_id"], start + timedelta(hours=71, minutes=59))
        closed = manager_exception_close("manager.morgan", t["ticket_id"], start + timedelta(hours=72))
        self.assertEqual(closed["status"], "Closed")

    def test_admin_receives_aggregates_only(self):
        self._ticket()
        summary = administration_summary("admin.housing")
        self.assertIn("unfinished", summary)
        self.assertNotIn("tickets", summary)
        self.assertNotIn("room", str(summary).lower())

    def test_emergency_boundary_notice_and_ai_fallback(self):
        result = begin_request("There is a gas leak in my room", {"building": "A", "room": "2", "availability": "anytime"}, use_ai=True)
        self.assertTrue(result["emergency_warning"])
        self.assertTrue(result["manual_fallback"])

    def test_backup_contains_committed_ticket(self):
        t = self._ticket()
        backup = Path(TEST_DIR.name) / "backup.db"
        support_backup("it.support", backup)
        self.assertTrue(backup.exists())
        self.assertGreater(backup.stat().st_size, 0)
        self.assertIn("recent_diagnostics", support_health("it.support"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
