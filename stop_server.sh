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

echo "Deteniendo POS Restaurant..."

if command -v systemctl >/dev/null 2>&1 && systemctl cat "$SERVICE_NAME" >/dev/null 2>&1; then
  if systemctl cat "$ZEROCONF_SERVICE" >/dev/null 2>&1; then
    run_privileged systemctl stop "$ZEROCONF_SERVICE"
  fi

  run_privileged systemctl stop "$SERVICE_NAME"
else
  compose down
fi

echo "Servidor detenido."
if [ -t 0 ]; then
  echo "Presiona Enter para cerrar esta ventana."
  read -r _
fi
