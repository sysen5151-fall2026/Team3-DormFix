"""Exercise the product's checkpoint and ticket failure paths on disposable databases."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlparse


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        import ticket_service
        import ticket_store
        self.service = ticket_service
        self.store = ticket_store
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.live = Path(directory.name) / "demo.db"
        self.backups = self.live.parent / "backups" / self.live.name
        location = patch.object(ticket_store, "DB_PATH", self.live)
        location.start()
        self.addCleanup(location.stop)
        ticket_service.initialize()
        self.draft = dict(description="Synthetic drip", building="Test Hall", room="10",
                          category="plumbing", availability="After class")

    def submit(self, n):
        return self.service.submit_maintenance_request("resident.alex", self.draft, str(n))

    def state(self):
        with self.store.connect() as db:
            return tuple([tuple(row) for row in db.execute(query)] for query in (
                "SELECT * FROM tickets ORDER BY ticket_id",
                "SELECT * FROM events ORDER BY event_id",
            ))

    def create(self):
        self.service.support_create_checkpoint("it.support")
        return sorted(self.backups.glob("gen-*"))[-1]

    def restore(self):
        return self.service.support_restore_checkpoint("it.support", confirmed=True)

    def two_versions(self):
        for n in range(10):
            ticket = self.submit(n)
            self.service.manager_assign("manager.morgan", ticket["ticket_id"], "tech.taylor", "Normal")
        older = self.create()
        ten = self.state()
        self.submit(10)
        newer = self.create()
        eleven = self.state()
        self.submit(11)
        return older, newer, ten, eleven

    def test_latest_recovers_eleven_tickets_and_exact_histories(self):
        _, _, _, eleven = self.two_versions()
        self.assertIn("latest verified checkpoint", self.restore())
        self.assertEqual(len(eleven[0]), 11)
        self.assertEqual(self.state(), eleven)

    def test_corrupt_latest_recovers_ten_and_reports_gap(self):
        _, newer, ten, _ = self.two_versions()
        (newer / "snapshot.sqlite").write_bytes(b"unreadable test snapshot")
        message = self.restore()
        self.assertIn("10 tickets from the previous verified checkpoint", message)
        self.assertIn("Changes after that checkpoint are excluded", message)
        self.assertEqual(len({event[1] for event in ten[1]}), 10)
        self.assertEqual(self.state(), ten)

    def test_both_invalid_leave_live_data_untouched(self):
        older, newer, _, _ = self.two_versions()
        before = self.state()
        (older / "snapshot.sqlite").unlink()
        (newer / "manifest.json").write_text("{")
        with self.assertRaisesRegex(ValueError, "No verified checkpoint"):
            self.restore()
        self.assertEqual(self.state(), before)

    def test_missing_live_database_recovers_after_normal_startup(self):
        self.submit(1)
        self.create()
        expected = self.state()
        self.live.unlink()
        self.service.initialize()
        self.assertEqual(self.state(), ([], []))
        self.restore()
        self.assertEqual(self.state(), expected)

    def test_checksum_catches_a_readable_but_modified_snapshot(self):
        _, newer, ten, _ = self.two_versions()
        with sqlite3.connect(newer / "snapshot.sqlite") as db:
            db.execute("UPDATE tickets SET room='changed' WHERE submission_key='10'")
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone(), ("ok",))
        self.restore()
        self.assertEqual(self.state(), ten)

    def test_third_checkpoint_prunes_oldest_and_spares_named_export(self):
        older, newer, _, _ = self.two_versions()
        export = self.backups.parent / "operator-export.db"
        self.assertEqual(self.service.support_backup("it.support", export), export)
        newest = self.create()
        self.assertFalse(older.exists())
        self.assertEqual(sorted(self.backups.glob("gen-*")), [newer, newest])
        self.assertTrue(export.is_file())

    def test_rotation_keeps_last_valid_predecessor(self):
        older, newer, ten, _ = self.two_versions()
        (newer / "manifest.json").unlink()
        third = self.create()
        self.assertEqual(sorted(self.backups.glob("gen-*")), [older, third])
        (third / "snapshot.sqlite").unlink()
        self.restore()
        self.assertEqual(self.state(), ten)

    def test_failed_snapshot_does_not_prune_prior_generations(self):
        older, newer, _, eleven = self.two_versions()
        with patch("ticket_store.checkpoints.backup_database", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                self.create()
        self.assertEqual(sorted(self.backups.glob("gen-*")), [older, newer])
        self.restore()
        self.assertEqual(self.state(), eleven)

    def test_concurrent_creations_publish_two_distinct_snapshots(self):
        self.submit(1)
        with ThreadPoolExecutor(max_workers=3) as pool:
            messages = list(pool.map(self.service.support_create_checkpoint, ["it.support"] * 3))
        self.assertEqual(len(set(messages)), 3)
        generations = sorted(self.backups.glob("gen-*"))
        self.assertEqual([p.name for p in generations], ["gen-000000000002", "gen-000000000003"])
        for p in generations:
            self.assertEqual(json.loads((p / "manifest.json").read_text())["tickets"], 1)

    def test_only_active_it_can_create_or_restore(self):
        self.create()
        self.service.support_set_account_active("it.support", "it.support", False)
        for actor in ("resident.alex", "manager.morgan", "it.support"):
            with self.subTest(actor=actor):
                with self.assertRaises(PermissionError):
                    self.service.support_create_checkpoint(actor)
                with self.assertRaises(PermissionError):
                    self.service.support_restore_checkpoint(actor, confirmed=True)

    def test_failed_history_write_rolls_back_ticket_then_retry_succeeds(self):
        with self.store.connect() as db:
            db.execute("""CREATE TRIGGER test_failure BEFORE INSERT ON events
                          BEGIN SELECT RAISE(ABORT, 'simulated history failure'); END""")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "simulated history failure"):
            self.submit(0)
        self.assertEqual(self.state(), ([], []))
        with self.store.connect() as db:
            db.execute("DROP TRIGGER test_failure")
        self.submit(0)
        self.assertEqual([len(rows) for rows in self.state()], [1, 1])

    def test_retry_after_lost_acknowledgement_keeps_one_ticket_and_event(self):
        first = self.submit(0)
        retry = self.submit(0)
        self.assertEqual(first["ticket_id"], retry["ticket_id"])
        self.assertEqual([len(rows) for rows in self.state()], [1, 1])

    def test_operator_web_flow_checks_confirmation_and_restores(self):
        from webapp import Handler

        # Exercise the actual HTTP parser, form dispatch and redirect, without a port.
        class Request:
            def __init__(self, data):
                self.incoming = BytesIO(data)
                self.outgoing = BytesIO()

            def makefile(self, *args):
                return self.incoming

            def sendall(self, data):
                self.outgoing.write(data)

        def request(method, path, **form):
            body = urlencode(form).encode()
            headers = f"{method} {path} HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n"
            req = Request(headers.encode() + body)
            Handler(req, ("127.0.0.1", 1), object())
            return req.outgoing.getvalue().decode()

        def post(action, **params):
            reply = request("POST", "/", actor="it.support", action=action, **params)
            self.assertIn(" 303 ", reply)
            location = next(line[10:] for line in reply.splitlines() if line.startswith("Location: "))
            return parse_qs(urlparse(location).query)["msg"][0]

        self.assertIn("Create verified checkpoint", request("GET", "/?actor=it.support"))
        self.assertNotIn("Restore verified checkpoint", request("GET", "/?actor=resident.alex"))
        self.submit(0)
        expected = self.state()
        self.assertIn("Created gen-", post("create_checkpoint"))
        self.submit(1)
        self.assertIn("Confirm", post("restore_checkpoint"))
        self.assertEqual(len(self.state()[0]), 2)
        self.assertIn("Restored 1 ticket", post("restore_checkpoint", confirm_restore="yes"))
        self.assertEqual(self.state(), expected)
