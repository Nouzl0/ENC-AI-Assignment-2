#!/usr/bin/env bash
# Local software tests, including the deterministic offline integration fixture.
# No product calls or real benchmarking; no generated results persisted in Git.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONDONTWRITEBYTECODE=1 "${PYTHON:-python3}" -m unittest discover -s tests -v
