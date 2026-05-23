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

cd "$APP_DIR"

echo "Iniciando POS Restaurant..."

if command -v systemctl >/dev/null 2>&1 && systemctl cat "$SERVICE_NAME" >/dev/null 2>&1; then
  run_privileged systemctl start docker
  run_privileged systemctl start "$SERVICE_NAME"

  if systemctl cat "$ZEROCONF_SERVICE" >/dev/null 2>&1; then
    run_privileged systemctl start "$ZEROCONF_SERVICE"
  fi
else
  compose up -d
fi

echo "Servidor iniciado."
echo "Acceso local: http://pos.local"
if [ -t 0 ]; then
  echo "Presiona Enter para cerrar esta ventana."
  read -r _
fi
