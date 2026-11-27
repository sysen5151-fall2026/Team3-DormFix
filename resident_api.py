"""JSON boundary for the primary resident workflow on the built-in web server."""
import json
import uuid
from http import HTTPStatus
from urllib.parse import unquote, urlsplit

from resident_interface import describe_issue, submit_issue
from ticket_service import get_visible_ticket, require_account

FIELDS = ("description", "building", "room", "category", "availability", "resident_contact")


def text_fields(value):
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object of draft fields")
    result = {key: value.get(key, "") for key in FIELDS}
    if any(not isinstance(v, str) or len(v) > 4000 for v in result.values()):
        raise ValueError("Draft fields must be text of at most 4000 characters")
    return result


def handle(handler):
    route = urlsplit(handler.path).path
    if not route.startswith("/api/"):
        return False
    try:
        actor = handler.headers.get("X-DormFix-Actor")
        if not actor:
            status, result = 401, {"error": "Select a demo identity"}
        elif handler.command == "GET" and route.startswith("/api/tickets/"):
            status, result = 200, get_visible_ticket(actor, unquote(route[len("/api/tickets/"):]))
        elif handler.command == "POST" and route in ("/api/drafts", "/api/tickets"):
            require_account(actor, "Resident")
            size = int(handler.headers.get("Content-Length", 0))
            if handler.headers.get_content_type() != "application/json" or not 0 < size <= 32768:
                raise ValueError("Send a JSON body of at most 32 KiB")
            body = json.loads(handler.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError("Expected a JSON object")
            if route == "/api/drafts":
                fields = text_fields(body)
                description = fields.pop("description")
                if not description.strip():
                    raise ValueError("Enter a description")
                status, result = 200, describe_issue(description, fields, body.get("use_ai", True) is True)
            else:
                if body.get("confirmed") is not True:
                    raise ValueError("Resident confirmation required")
                draft = text_fields(body.get("draft"))
                if describe_issue(draft["description"], draft, False)["emergency_warning"]:
                    raise ValueError("Possible emergency. Contact the appropriate emergency service.")
                key = str(uuid.UUID(str(body.get("submission_key", ""))))
                raw = body.get("suggestions", {})
                if not isinstance(raw, dict):
                    raise ValueError("Invalid suggestions")
                suggestions = {k:v for k,v in raw.items() if k in ("summary","category","availability","source") and isinstance(v,str)}
                saved = submit_issue(actor, draft, key, suggestions)
                status, result = 200, {"ticket_id": saved["ticket_id"], "status": saved["status"]}
        else:
            status, result = 404, {"error": "Unknown route"}
    except PermissionError as exc:
        status, result = 403, {"error": str(exc)}
    except KeyError:
        status, result = 404, {"error": "Ticket not found"}
    except (ValueError, TypeError) as exc:
        status, result = 400, {"error": str(exc)}
    except Exception:
        status, result = 500, {"error": "Request could not be completed. Retry with the same key."}
    payload = json.dumps(result).encode("utf-8")
    handler.send_response(HTTPStatus(status))
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)
    return True
