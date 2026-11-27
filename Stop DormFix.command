#!/bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"; PIDFILE="$HERE/data/dormfix-web.pid"
if [ -f "$PIDFILE" ]; then PID="$(cat "$PIDFILE" 2>/dev/null || true)"; [ -n "$PID" ] && kill "$PID" 2>/dev/null || true; rm -f "$PIDFILE"; echo "DormFix stopped."; else echo "No DormFix PID file found."; fi
read -r -p "Press Return to close..." _
