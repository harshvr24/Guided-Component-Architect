#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Backend syntax check"
python3 -m compileall pythrust/backend >/dev/null

echo "[2/4] Start backend from repo root"
uvicorn pythrust.backend.server:app --host 127.0.0.1 --port 8000 >/tmp/gca_backend.log 2>&1 &
BACKEND_PID=$!
trap 'kill ${BACKEND_PID} >/dev/null 2>&1 || true' EXIT

for _ in $(seq 1 20); do
  if curl -sS http://127.0.0.1:8000/docs >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if ! curl -sS http://127.0.0.1:8000/docs >/dev/null 2>&1; then
  echo "Backend failed to start"
  cat /tmp/gca_backend.log
  exit 1
fi

echo "[3/4] API smoke test"
curl -sS -X POST http://127.0.0.1:8000/v1/generate/page \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Build a full page app with hero and footer"}' \
  | python3 -m json.tool >/tmp/gca_api_response.json

if ! grep -q '"status": "success"' /tmp/gca_api_response.json; then
  echo "API smoke test failed"
  cat /tmp/gca_api_response.json
  exit 1
fi

echo "[4/4] Frontend production build"
cd pythrust/frontend
npm run build >/tmp/gca_frontend_build.log 2>&1

echo "Smoke run completed successfully."
