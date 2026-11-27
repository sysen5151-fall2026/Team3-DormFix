#!/bin/bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
PORT="${DORMFIX_PORT:-8502}"; PIDFILE="$HERE/data/dormfix-web.pid"; LOGFILE="$HERE/data/dormfix-web.log"; mkdir -p "$HERE/data"
PYTHON=""; [ -x "$HERE/.venv/bin/python" ] && PYTHON="$HERE/.venv/bin/python"; [ -z "$PYTHON" ] && command -v python3 >/dev/null 2>&1 && PYTHON="$(command -v python3)"
[ -z "$PYTHON" ] && { echo "Python 3 not found."; read -r -p "Press Return..." _; exit 1; }
if command -v curl >/dev/null 2>&1 && curl -fsS "http://127.0.0.1:$PORT" >/dev/null 2>&1; then open "http://127.0.0.1:$PORT"; exit 0; fi
[ -f "$PIDFILE" ] && OLD_PID="$(cat "$PIDFILE" 2>/dev/null || true)" && [ -n "$OLD_PID" ] && kill "$OLD_PID" 2>/dev/null || true
: > "$LOGFILE"; nohup "$PYTHON" "$HERE/webapp.py" --port "$PORT" >> "$LOGFILE" 2>&1 & PID=$!; echo "$PID" > "$PIDFILE"
for i in $(seq 1 30); do if curl -fsS "http://127.0.0.1:$PORT" >/dev/null 2>&1; then echo "DormFix ready: http://127.0.0.1:$PORT"; open "http://127.0.0.1:$PORT"; exit 0; fi; kill -0 "$PID" 2>/dev/null || break; sleep 0.5; done
echo "DormFix failed to start."; tail -n 40 "$LOGFILE" 2>/dev/null || true; read -r -p "Press Return..." _; exit 1
