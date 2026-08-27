#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="pos-restaurant"
ZEROCONF_SERVICE="pos-zeroconf"


run_privileged() {
  if [ "$EUID" -eq 0 ]; then
    "$@"
  else
    sudo "$@"
  fi
}


compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}


get_local_ip() {
  ip route get 1.1.1.1 2>/dev/null \
    | awk '{
        for (i=1; i<=NF; i++) {
          if ($i=="src") {
            print $(i+1)
            exit
          }
        }
      }'
}


wait_for_backend() {
  local ready=0

  for _ in {1..30}; do
    if compose exec -T backend \
      python -c \
      "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" \
      >/dev/null 2>&1
    then
      ready=1
      break
    fi

    sleep 2
  done

  [ "$ready" -eq 1 ]
}


wait_for_frontend() {
  local ready=0

  for _ in {1..30}; do
    if curl -fsS \
      http://127.0.0.1/ \
      >/dev/null 2>&1
    then
      ready=1
      break
    fi

    sleep 1
  done

  [ "$ready" -eq 1 ]
}


cd "$APP_DIR"

echo "Iniciando POS Restaurant..."


if command -v systemctl >/dev/null 2>&1 \
  && systemctl cat "$SERVICE_NAME" >/dev/null 2>&1
then

  run_privileged systemctl start docker

  if ! run_privileged systemctl restart "$SERVICE_NAME"; then
    echo
    echo "ERROR: POS Restaurant no pudo iniciar."
    echo
    echo "Revisa:"
    echo "  systemctl status ${SERVICE_NAME}"
    echo "  docker compose -f ${COMPOSE_FILE} logs backend"
    exit 1
  fi

  if systemctl cat "$ZEROCONF_SERVICE" >/dev/null 2>&1; then
    run_privileged systemctl restart "$ZEROCONF_SERVICE"
  fi

else

  compose up -d

fi


echo "Esperando al backend..."

if ! wait_for_backend; then
  echo
  echo "ERROR: el backend no pudo iniciar."
  echo
  echo "Posibles causas:"
  echo "  - Licencia inexistente o invalida"
  echo "  - Error de base de datos"
  echo "  - Error durante migraciones"
  echo
  echo "Revisa:"
  echo "  docker compose -f ${COMPOSE_FILE} logs backend"
  echo

  compose down || true

  exit 1
fi


echo "Esperando al frontend..."

if ! wait_for_frontend; then
  echo
  echo "ERROR: el backend inicio, pero el frontend no responde."
  echo
  echo "Revisa:"
  echo "  docker compose -f ${COMPOSE_FILE} logs frontend"
  echo

  exit 1
fi


echo "Servidor iniciado correctamente."


LOCAL_IP="$(get_local_ip)"

if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP="$(
    hostname -I 2>/dev/null \
      | awk '{print $1}'
  )"
fi


echo
echo "Acceso local:"
echo "  http://pos.local"

if [ -n "$LOCAL_IP" ]; then
  echo "  http://${LOCAL_IP}"
fi


if [ -t 0 ]; then
  echo
  echo "Presiona Enter para cerrar esta ventana."
  read -r _
fi