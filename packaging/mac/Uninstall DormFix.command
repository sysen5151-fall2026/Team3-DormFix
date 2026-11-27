#!/bin/bash
TARGET="$HOME/Applications/DormFix"
APP="$HOME/Applications/DormFix.app"
echo "DormFix Uninstaller"
read -r -p "Type UNINSTALL to continue: " ANSWER
if [ "$ANSWER" != "UNINSTALL" ]; then echo "Cancelled."; read -r -p "Press Return to close..." _; exit 0; fi
if [ -f "$TARGET/data/dormfix-web.pid" ]; then PID="$(cat "$TARGET/data/dormfix-web.pid" 2>/dev/null || true)"; [ -n "$PID" ] && kill "$PID" 2>/dev/null || true; fi
rm -rf "$APP" "$TARGET"
echo "DormFix removed from ~/Applications."
read -r -p "Press Return to close..." _
