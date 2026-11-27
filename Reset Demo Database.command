#!/bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"; read -r -p "Type RESET to delete local demo database: " A; [ "$A" = "RESET" ] || { echo "Cancelled."; exit 0; }; rm -f "$HERE/data/dormfix.db"; echo "Database reset. It will be recreated on next start."; read -r -p "Press Return..." _
