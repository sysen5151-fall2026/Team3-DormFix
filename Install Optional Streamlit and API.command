#!/bin/bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"; python3 -m venv .venv; .venv/bin/python -m pip install --upgrade pip; .venv/bin/python -m pip install -r requirements.txt; echo "Optional environment installed."; read -r -p "Press Return..." _
