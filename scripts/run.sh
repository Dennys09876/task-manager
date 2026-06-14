#!/bin/bash
# Ejecuta la aplicación en el ambiente especificado

set -e

ENV=${1:-dev}

echo "=== [RUN] Iniciando Task Manager en ambiente: $ENV ==="

case "$ENV" in
  dev)
    export $(cat .env.dev | grep -v '#' | xargs)
    echo "Puerto: $PORT | DB: $DATABASE_URL"
    source venv/bin/activate 2>/dev/null || true
    python run.py
    ;;
  test)
    export $(cat .env.test | grep -v '#' | xargs)
    source venv/bin/activate 2>/dev/null || true
    python run.py
    ;;
  prod)
    export $(cat .env.prod | grep -v '#' | xargs)
    source venv/bin/activate 2>/dev/null || true
    gunicorn --bind 0.0.0.0:$PORT --workers 4 run:app
    ;;
  docker-dev)
    docker compose -f docker-compose.dev.yml up --build
    ;;
  docker-test)
    docker compose -f docker-compose.test.yml up --build
    ;;
  docker-prod)
    docker compose -f docker-compose.prod.yml up --build -d
    ;;
  *)
    echo "Uso: ./scripts/run.sh [dev|test|prod|docker-dev|docker-test|docker-prod]"
    exit 1
    ;;
esac
