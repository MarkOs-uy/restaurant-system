#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$APP_DIR"

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}


echo "Iniciando contenedores..."

compose up -d


echo "Esperando backend..."

for _ in {1..45}; do

  if compose exec -T backend \
    python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" \
    >/dev/null 2>&1
  then
    echo "Backend listo."
    exit 0
  fi

  sleep 2
done


echo "ERROR: backend no pudo iniciar." >&2

compose logs --tail=30 backend >&2 || true

compose down || true

exit 1