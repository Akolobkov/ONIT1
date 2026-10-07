#!/bin/sh
set -e

echo "[entrypoint] Running Alembic migrations..."
python -m alembic -c /app/alembic.ini upgrade head

echo "[entrypoint] Starting FastAPI on 0.0.0.0:8000 ..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
