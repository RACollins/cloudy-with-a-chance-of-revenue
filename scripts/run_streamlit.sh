#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export CLOUDY_API_URL="${CLOUDY_API_URL:-http://127.0.0.1:8000}"
uv run streamlit run app/frontend/main.py
