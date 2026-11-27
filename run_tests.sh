#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python demo_scenario.py
python -m unittest discover -s tests -v
