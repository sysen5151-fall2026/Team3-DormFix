#!/bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
echo "DormFix diagnostics"; sw_vers; uname -m; echo; which python3 || true; python3 --version || true; echo; python3 -m unittest discover -s tests -v || true; echo; for p in 8502 8501 8000; do if curl -fsS "http://127.0.0.1:$p" >/dev/null 2>&1; then echo "Port $p: responding"; else echo "Port $p: no HTTP response"; fi; done
read -r -p "Press Return to close..." _
