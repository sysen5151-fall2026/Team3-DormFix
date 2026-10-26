from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DORMFIX_DB_PATH", str(ROOT / "data" / "dormfix.db")))
LLM_URL = os.getenv("DORMFIX_LLM_URL", "").strip()
LLM_MODEL = os.getenv("DORMFIX_LLM_MODEL", "local-model").strip() or "local-model"
LLM_API_KEY = os.getenv("DORMFIX_LLM_API_KEY", "").strip()
SUPPORTED_CATEGORIES = ("plumbing", "electrical", "appliances", "general")
LIFECYCLE_STATES = (
    "Submitted",
    "Assigned",
    "In progress",
    "Awaiting resident confirmation",
    "Closed",
    "Reopened",
)
ROLES = ("Resident", "Technician", "Manager", "Administration", "IT Support")
