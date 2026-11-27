#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python webapp.py --port 8502
