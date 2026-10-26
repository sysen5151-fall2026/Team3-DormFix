#!/bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"; [ -x .venv/bin/python ] || { echo "Run Install Optional Streamlit and API.command first."; read -r -p "Press Return..." _; exit 1; }; .venv/bin/python -m uvicorn api:app --reload --port 8000
