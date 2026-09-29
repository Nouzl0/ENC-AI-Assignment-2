#!/usr/bin/env bash
# End-to-end test of the pipeline on SYNTHETIC data. Nothing produced here is a real result.
# ONLINE=1 bash demo/run_demo.sh  -> also tests the HTTP checks against a local demo web server.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/make_demo_data.py
python3 scripts/validate_cases.py --data-dir demo/data

if [ "${ONLINE:-0}" = "1" ]; then
  (cd demo/example/site && python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1) &
  SERVER=$!
  trap 'kill $SERVER 2>/dev/null || true' EXIT
  sleep 1
  python3 scripts/check_citations.py --runs demo/example/run_plan_example.csv --data-dir demo/data \
    --out-dir demo/example/annotation --key-dir demo/example/annotation_key --retry-wait 0 --timeout 5
else
  python3 scripts/check_citations.py --runs demo/example/run_plan_example.csv --data-dir demo/data \
    --out-dir demo/example/annotation --key-dir demo/example/annotation_key --offline
fi

python3 scripts/score.py --runs "demo/runs/*.csv" --annotation-dir demo/annotation --key-dir demo/annotation_key --data-dir demo/data \
  --out demo/results --focus sys_D --boot 2000
echo "Hotovo: demo/results/report.md a demo/example/annotation/ (SYNTETICKÁ DATA – nejde o skutečné výsledky)"
