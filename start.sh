#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/mvp_absenteismo"

exec streamlit run app.py \
  --server.port="${PORT:-8501}" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
