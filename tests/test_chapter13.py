"""Targeted checks on a synthetic SQLite database. Each test is isolated."""
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


class Chapter13Checks(unittest.TestCase):
    def setUp(self):
        import ticket_service as svc
        import ticket_store as store
        self.svc, self.store = svc, store
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.enterContext(patch.object(store, "DB_PATH", Path(temp.name)/"test.sqlite"))
        svc.initialize()
        self.base=dict(description="Kitchen sink drips",building="Hall",room="10",category="plumbing",availability="4 PM")

    def submit(self, key, **values):
        return self.svc.submit_maintenance_request("resident.alex",dict(self.base,**values),key)["ticket_id"]

    def test_duration_and_inclusive_repeat_window(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        rows=[(0,"10"),(7,"10"),(15,"10"),(16,"10"),(16,"11")]
        for i,(day,room) in enumerate(rows):
            tid=self.submit(str(i),room=room)
            t=start+timedelta(days=day)
            with self.store.connect() as db:
                db.execute("UPDATE tickets SET status=?,submitted_at=?,updated_at=? WHERE ticket_id=?",
                           ("Closed" if i==0 else "Submitted",t.isoformat(),(t+timedelta(hours=4)).isoformat(),tid))
        with patch.dict("os.environ",{"DORMFIX_REPEAT_DAYS":"7"}):
            s=self.svc.administration_summary("admin.housing")
        self.assertEqual((s["repeat_count"],s["repeat_days"],s["total"],s["unfinished"]),(2,7,5,4))
        self.assertEqual(s["mean_closed_duration_hours"],4.0)
        self.assertGreater(s["mean_open_age_hours"],4)
        self.assertNotIn("10",str(s["by_status"]))
        self.assertNotIn("tickets",s)

    def test_access_changes_and_manager_corrections(self):
        t=self.submit("correct")
        self.svc.manager_correct_ticket("manager.morgan",t,"category","general")
        self.svc.manager_assign("manager.morgan",t,"tech.taylor","Normal")
        self.svc.propose_access_change("tech.taylor",t,"Friday 6 PM")
        self.svc.manager_coordinate_access_change("manager.morgan",t,"Friday 6 PM")
        self.assertEqual(self.store.get_ticket(t)["availability"],"4 PM")
        self.svc.resident_confirm_access_change("resident.alex",t,True)
        self.assertEqual(self.store.get_ticket(t)["availability"],"Friday 6 PM")
        self.assertIn("Manager correction",[r["event_type"] for r in self.store.events(t)])

    def test_ten_sampled_histories_and_queue(self):
        tickets=[self.submit(str(i),room=str(i)) for i in range(16)]
        for t in tickets:
            self.svc.manager_assign("manager.morgan",t,"tech.taylor","Normal")
            self.svc.technician_complete("tech.taylor",t,"Done")
            self.svc.resident_confirm_resolution("resident.alex",t,False,"Still drips")
        self.assertEqual({r["ticket_id"] for r in self.svc.manager_pending("manager.morgan")},set(tickets))
        for t in random.Random(5151).sample(tickets,10):
            h=self.svc.get_visible_ticket("manager.morgan",t)["history"]
            expected=[("Submitted","resident.alex",None)]
            expected.extend(("Manager assignment","manager.morgan",f) for f in ("priority","assigned_technician","status"))
            expected.extend(("Technician completed work","tech.taylor",f) for f in ("status","awaiting_since"))
            expected.append(("Completion note","tech.taylor",None))
            expected.extend(("Resident reopened","resident.alex",f) for f in ("status","assigned_technician"))
            self.assertEqual([(e["event_type"],e["actor_id"],e["field_name"]) for e in h],expected)
            stamps=[datetime.fromisoformat(e["ts"]) for e in h]
            self.assertEqual(stamps,sorted(stamps))

    def test_model_timeout_keeps_manual_path(self):
        import intake_model
        with patch.object(intake_model,"LLM_URL","http://fixture.invalid"), patch("urllib.request.build_opener") as opener:
            opener.return_value.open.side_effect=TimeoutError()
            result=self.svc.begin_request(self.base["description"],self.base,True)
        self.assertTrue(result["manual_fallback"])
        self.assertEqual(result["draft"]["availability"],"4 PM")
        self.assertEqual(self.svc.submit_maintenance_request("resident.alex",result["draft"],"timeout")["status"],"Submitted")
        self.assertEqual(self.svc.support_health("it.support")["recent_diagnostics"][0]["state"],"failure")
