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
  run_privileged systemctl restart "$SERVICE_NAME"

  if systemctl cat "$ZEROCONF_SERVICE" >/dev/null 2>&1; then
    run_privileged systemctl restart "$ZEROCONF_SERVICE"
  fi

else
  compose up -d
fi


echo "Esperando al servidor..."

if ! wait_for_frontend; then
  echo "AVISO: el servidor fue iniciado, pero el frontend no respondió."
  echo
  echo "Revisa los logs con:"
  echo "  cd ${APP_DIR}"
  echo "  docker compose -f ${COMPOSE_FILE} logs"
else
  echo "Servidor iniciado correctamente."
fi


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