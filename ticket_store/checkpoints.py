"""Verified recovery points for the local DormFix SQLite database."""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from . import backup_database, db_path, restore_database, utcnow


@dataclass(frozen=True)
class Checkpoint:
    generation: str
    taken_at: str
    tickets: int
    used_previous: bool = False


@contextmanager
def _locked_root():
    live = db_path()
    root = live.parent / "backups" / live.name
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    # A SQLite write reservation serializes rotation and restore across both UIs.
    with closing(sqlite3.connect(root / "operations.sqlite", timeout=15)) as lock:
        lock.execute("BEGIN IMMEDIATE")
        try:
            for orphan in root.glob(".staging-*"):
                if orphan.is_dir() and not orphan.is_symlink():
                    shutil.rmtree(orphan)
            yield root
        finally:
            lock.rollback()


def _generations(root: Path) -> list[Path]:
    return sorted((path for path in root.glob("gen-" + "[0-9]" * 12) if path.is_dir()),
                  reverse=True)


def _digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def _ticket_count(path: Path) -> int:
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")
        if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise ValueError("Checkpoint contains a broken reference")
        for table in ("accounts", "events", "diagnostics", "account_events"):
            db.execute(f"SELECT 1 FROM {table} LIMIT 1")
        return db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]


def _verified(path: Path) -> Checkpoint | None:
    snapshot = path / "snapshot.sqlite"
    try:
        with (path / "manifest.json").open(encoding="utf-8") as stream:
            manifest = json.load(stream)
        if manifest["generation"] != path.name or manifest["sha256"] != _digest(snapshot):
            return None
        if datetime.fromisoformat(manifest["taken_at"]).tzinfo is None:
            return None
        count = _ticket_count(snapshot)
        if count != manifest["tickets"]:
            return None
        return Checkpoint(path.name, manifest["taken_at"], count)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error):
        return None


def create_checkpoint() -> Checkpoint:
    with _locked_root() as root:
        previous = _generations(root)
        number = int(previous[0].name[4:]) + 1 if previous else 1
        name = f"gen-{number:012d}"
        with TemporaryDirectory(dir=root, prefix=".staging-") as staging:
            candidate = Path(staging) / name
            candidate.mkdir()
            snapshot = backup_database(candidate / "snapshot.sqlite")
            manifest = dict(generation=name, taken_at=utcnow(), tickets=_ticket_count(snapshot),
                            sha256=_digest(snapshot))
            (candidate / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            result = _verified(candidate)
            if result is None:
                raise ValueError("New checkpoint did not verify. Prior checkpoints are retained.")
            candidate.rename(root / name)
        # Publish first, then retain the newest usable predecessor even if its
        # successor was damaged. An interrupted prune can safely be retried.
        keep = next((p for p in previous if _verified(p) is not None), None)
        for old in previous:
            if old != keep:
                shutil.rmtree(old)
        return result


def restore_checkpoint() -> Checkpoint:
    with _locked_root() as root:
        for position, path in enumerate(_generations(root)):
            checkpoint = _verified(path)
            if checkpoint is not None:
                # A destination error must surface; never retry it with older data.
                restore_database(path / "snapshot.sqlite")
                return Checkpoint(path.name, checkpoint.taken_at, checkpoint.tickets,
                                  used_previous=position > 0)
    raise ValueError("No verified checkpoint is available. The live database was left in place.")
