#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"
LICENSE_FILE="/var/lib/pos-restaurant/license.json"


cd "$APP_DIR"


compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}


# -----------------------------------------------------------------------------
# Verificar que exista el archivo de licencia antes de invocar Docker.
#
# Evita que Docker cree accidentalmente un directorio llamado license.json
# cuando el origen del bind mount no existe.
# -----------------------------------------------------------------------------

if [ ! -f "$LICENSE_FILE" ]; then
  echo "ERROR: no se encontro el archivo de licencia:" >&2
  echo "  $LICENSE_FILE" >&2
  exit 1
fi


echo "Iniciando contenedores..."

compose up -d


echo "Esperando backend..."

for _ in {1..45}; do

  # ---------------------------------------------------------------------------
  # ¿Backend saludable?
  # ---------------------------------------------------------------------------

  if compose exec -T backend \
    python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" \
    >/dev/null 2>&1
  then
    echo "Backend listo."
    exit 0
  fi


  # ---------------------------------------------------------------------------
  # Detectar si el proceso backend ya fallo y Docker lo esta reiniciando.
  # ---------------------------------------------------------------------------

  BACKEND_CONTAINER="$(
    compose ps -q backend 2>/dev/null || true
  )"


  if [ -n "$BACKEND_CONTAINER" ]; then

    BACKEND_STATUS="$(
      docker inspect \
        -f '{{.State.Status}}' \
        "$BACKEND_CONTAINER" \
        2>/dev/null || true
    )"

    RESTART_COUNT="$(
      docker inspect \
        -f '{{.RestartCount}}' \
        "$BACKEND_CONTAINER" \
        2>/dev/null || echo "0"
    )"


    if [ "$BACKEND_STATUS" = "restarting" ] \
      || [ "${RESTART_COUNT:-0}" -gt 0 ]
    then

      echo
      echo "ERROR: el backend fallo durante el arranque." >&2
      echo
      echo "Ultimos mensajes del backend:" >&2
      echo >&2

      compose logs \
        --tail=30 \
        backend \
        >&2 || true

      echo
      echo "Deteniendo contenedores..." >&2

      compose down || true

      exit 1
    fi

  fi


  sleep 2

done


echo
echo "ERROR: el backend no respondio dentro del tiempo esperado." >&2
echo
echo "Ultimos mensajes del backend:" >&2
echo >&2

compose logs \
  --tail=30 \
  backend \
  >&2 || true


compose down || true

exit 1