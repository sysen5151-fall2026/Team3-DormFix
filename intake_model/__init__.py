from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from config import LLM_API_KEY, LLM_MODEL, LLM_URL, SUPPORTED_CATEGORIES
from ticket_store import record_diagnostic

EMERGENCY_KEYWORDS = (
    "fire", "smoke", "gas leak", "gas smell", "severe water leak", "flooding", "electrical fire"
)


def _category_from_text(text: str) -> str | None:
    t = text.lower()
    if any(k in t for k in ("sink", "toilet", "leak", "faucet", "pipe", "drain")):
        return "plumbing"
    if any(k in t for k in ("outlet", "power", "light", "breaker", "electrical")):
        return "electrical"
    if any(k in t for k in ("fridge", "refrigerator", "oven", "stove", "dishwasher", "microwave", "washer", "dryer")):
        return "appliances"
    if text.strip():
        return "general"
    return None


def _heuristic(description: str, provided: dict[str, Any]) -> dict[str, Any]:
    category = provided.get("category") or _category_from_text(description)
    summary = description.strip()[:180] if description.strip() else None
    location = None
    if provided.get("building") and provided.get("room"):
        location = f"{provided['building']}, {provided['room']}"
    return {
        "category": category if category in SUPPORTED_CATEGORIES else None,
        "summary": summary,
        "location": location,
        "availability": provided.get("availability") or None,
        "missing_fields": [],
        "source": "local-heuristic",
    }


def _call_llm(description: str, provided: dict[str, Any]) -> dict[str, Any]:
    if not LLM_URL:
        raise RuntimeError("No LLM endpoint configured")
    prompt = {
        "description": description,
        "provided": {k: provided[k] for k in ("category", "availability") if provided.get(k)},
        "allowed_categories": list(SUPPORTED_CATEGORIES),
        "instruction": (
            "Suggest a category and a short factual summary of the resident description. "
            "Never infer permission to enter, priority, assignment or a location."
        ),
    }
    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are an advisory intake parser for routine non-emergency student housing maintenance."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
        "temperature": 0,
        "max_tokens": 150,
        "response_format": {"type":"json_schema", "json_schema":{"name":"maintenance_draft","strict":True,"schema":{
            "type":"object", "properties":{
                "category":{"type":"string","enum":list(SUPPORTED_CATEGORIES)},
                "summary":{"type":"string"}},
            "required":["category","summary"],"additionalProperties":False}}},
    }
    req = urllib.request.Request(
        LLM_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {LLM_API_KEY}"} if LLM_API_KEY else {}),
        },
        method="POST",
    )
    try:
        timeout = float(os.getenv("DORMFIX_LLM_TIMEOUT_SECONDS", "30"))
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        record_diagnostic("ai_connection", "failure", type(exc).__name__)
        raise RuntimeError("AI service unavailable") from exc
    try:
        content = payload["choices"][0]["message"]["content"]
        data = json.loads(content)
    except Exception as exc:
        record_diagnostic("ai_response", "failure", "malformed_response")
        raise RuntimeError("AI response malformed") from exc
    if not isinstance(data, dict) or not any(k in data for k in ("category", "summary", "missing_fields")):
        raise RuntimeError("AI response must contain draft fields")
    allowed = {"category", "summary", "location", "availability", "missing_fields"}
    data = {k: v for k, v in data.items() if k in allowed}
    for key in ("category", "summary", "location", "availability"):
        if data.get(key) is not None and not isinstance(data[key], str):
            raise RuntimeError("Invalid AI field type")
    if data.get("category") not in (*SUPPORTED_CATEGORIES, None):
        data["category"] = None
    if not isinstance(data.get("missing_fields", []), list):
        raise RuntimeError("AI missing_fields must be a list")
    data["source"] = "configured-llm"
    if isinstance(payload.get("model"), str):
        data["served_model"] = payload["model"]
    return data


def structure_request(description: str, provided: dict[str, Any] | None = None, use_ai: bool = True) -> dict[str, Any]:
    provided = dict(provided or {})
    emergency = any(k in description.lower() for k in EMERGENCY_KEYWORDS)
    fallback = False
    if use_ai and LLM_URL:
        try:
            suggestions = _call_llm(description, provided)
        except Exception:
            suggestions = _heuristic(description, provided)
            fallback = True
    else:
        suggestions = _heuristic(description, provided)
        fallback = bool(use_ai and not LLM_URL)
        if fallback:
            record_diagnostic("ai_connection", "degraded", "no_endpoint_configured")

    draft = {
        "description": description.strip(),
        "building": (provided.get("building") or "").strip(),
        "room": (provided.get("room") or "").strip(),
        "category": (provided.get("category") or suggestions.get("category") or "").strip(),
        "availability": (provided.get("availability") or "").strip(),
        "resident_contact": (provided.get("resident_contact") or "").strip(),
    }
    missing = [f for f in ("description", "building", "room", "category", "availability") if not draft.get(f)]
    suggestions["missing_fields"] = missing
    return {
        "draft": draft,
        "suggestions": suggestions,
        "missing_fields": missing,
        "manual_fallback": fallback,
        "emergency_warning": emergency,
    }
