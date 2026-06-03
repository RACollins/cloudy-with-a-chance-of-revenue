#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../infra/cdk"
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap
cdk deploy --all --require-approval never
