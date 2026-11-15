#!/usr/bin/env bash
set -euo pipefail


APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"

SERVICE_NAME="pos-restaurant"
ZEROCONF_SERVICE="pos-zeroconf"

HOSTNAME_LOCAL="pos"

INSTALL_STATE_DIR="/var/lib/pos-restaurant"
INSTALL_STATE_FILE="${INSTALL_STATE_DIR}/install.conf"
LICENSE_FILE="${INSTALL_STATE_DIR}/license.json"

MONITOR_DIR="${APP_DIR}/monitor-marcha"
MONITOR_VENV="${MONITOR_DIR}/venv"


# -----------------------------------------------------------------------------
# Colores
# -----------------------------------------------------------------------------

if [ -t 1 ]; then
  RED=$'\033[31m'
  GREEN=$'\033[32m'
  YELLOW=$'\033[33m'
  BLUE=$'\033[34m'
  BOLD=$'\033[1m'
  RESET=$'\033[0m'
else
  RED=""
  GREEN=""
  YELLOW=""
  BLUE=""
  BOLD=""
  RESET=""
fi


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

section() {
  printf "\n%s==> %s%s\n" \
    "$BLUE" "$1" "$RESET"
}


success() {
  printf "%s[OK]%s %s\n" \
    "$GREEN" "$RESET" "$1"
}


warn() {
  printf "%s[AVISO]%s %s\n" \
    "$YELLOW" "$RESET" "$1"
}


fail() {
  printf "%s[ERROR]%s %s\n" \
    "$RED" "$RESET" "$1" >&2

  exit 1
}


compose() {
  docker compose \
    -f "$COMPOSE_FILE" \
    "$@"
}


# -----------------------------------------------------------------------------
# Detectar escritorio
# -----------------------------------------------------------------------------

desktop_dir_for_user() {
  local username="$1"
  local home_dir

  home_dir="$(
    getent passwd "$username" \
      | cut -d: -f6
  )"

  [ -n "$home_dir" ] || return 1


  if [ -d "${home_dir}/Desktop" ]; then

    printf "%s/Desktop" \
      "$home_dir"

  elif [ -d "${home_dir}/Escritorio" ]; then

    printf "%s/Escritorio" \
      "$home_dir"

  else

    printf "%s/Desktop" \
      "$home_dir"

  fi
}


# -----------------------------------------------------------------------------
# Detener Marcha Monitor
# -----------------------------------------------------------------------------

stop_monitor() {

  if pgrep \
    -f \
    "${MONITOR_DIR}/marcha_monitor.py" \
    >/dev/null 2>&1
  then

    pkill \
      -f \
      "${MONITOR_DIR}/marcha_monitor.py" \
      >/dev/null 2>&1 || true

    sleep 1

    success "Marcha Monitor detenido"

  else

    warn "Marcha Monitor no estaba ejecutandose"

  fi
}


# -----------------------------------------------------------------------------
# Quitar Marcha Monitor del usuario gráfico
# -----------------------------------------------------------------------------

remove_monitor_user_integration() {
  local target_user="$1"
  local home_dir
  local desktop_dir
  local autostart_file
  local shortcut_file


  if [ -z "$target_user" ]; then

    warn "No pude detectar el usuario grafico; no puedo quitar autostart ni acceso directo de Marcha Monitor."

    return

  fi


  home_dir="$(
    getent passwd "$target_user" \
      | cut -d: -f6
  )"


  if [ -z "$home_dir" ]; then

    warn "No pude detectar HOME de ${target_user}; no puedo quitar autostart de Marcha Monitor."

    return

  fi


  # ---------------------------------------------------------------------------
  # Autostart
  # ---------------------------------------------------------------------------

  autostart_file="${home_dir}/.config/autostart/marcha-monitor.desktop"


  if [ -f "$autostart_file" ]; then

    rm -f \
      "$autostart_file"

    success "Autostart de Marcha Monitor quitado"

  fi


  # ---------------------------------------------------------------------------
  # Acceso directo del escritorio
  # ---------------------------------------------------------------------------

  desktop_dir="$(
    desktop_dir_for_user "$target_user" || true
  )"


  if [ -n "${desktop_dir:-}" ]; then

    shortcut_file="${desktop_dir}/Marcha Monitor.desktop"


    if [ -f "$shortcut_file" ]; then

      rm -f \
        "$shortcut_file"

      success "Acceso directo de Marcha Monitor quitado"

    fi

  fi
}


# -----------------------------------------------------------------------------
# Quitar entorno virtual del monitor
#
# El entorno virtual es generado por install.sh y puede reconstruirse.
# No contiene datos del usuario ni configuracion persistente.
# -----------------------------------------------------------------------------

remove_monitor_venv() {

  if [ -d "$MONITOR_VENV" ]; then

    rm -rf \
      "$MONITOR_VENV"

    success "Entorno virtual de Marcha Monitor eliminado"

  else

    warn "No existe entorno virtual de Marcha Monitor"

  fi
}


# -----------------------------------------------------------------------------
# Restaurar hostname / Avahi
# -----------------------------------------------------------------------------

restore_network_configuration() {

  if [ ! -f "$INSTALL_STATE_FILE" ]; then

    warn "No encontre el estado original de hostname/Avahi; no se modificara la configuracion de red."

    return
  fi


  # El archivo fue creado por install.sh como root y con permisos 600.
  # shellcheck disable=SC1090
  source "$INSTALL_STATE_FILE"


  # ---------------------------------------------------------------------------
  # Restaurar configuración original de Avahi
  # ---------------------------------------------------------------------------

  if [ -n "${AVAHI_BACKUP:-}" ] \
    && [ -f "$AVAHI_BACKUP" ]
  then

    cp \
      "$AVAHI_BACKUP" \
      /etc/avahi/avahi-daemon.conf

    success "Configuracion original de Avahi restaurada"

  else

    warn "No encontre el backup original de Avahi."

  fi


  # ---------------------------------------------------------------------------
  # Restaurar hostname original
  # ---------------------------------------------------------------------------

  if [ -n "${ORIGINAL_HOSTNAME:-}" ]; then

    hostnamectl set-hostname \
      "$ORIGINAL_HOSTNAME"

    success "Hostname restaurado a ${ORIGINAL_HOSTNAME}"

  else

    warn "No encontre el hostname original."

  fi


  # ---------------------------------------------------------------------------
  # Reiniciar Avahi
  # ---------------------------------------------------------------------------

  if systemctl list-unit-files \
    avahi-daemon.service \
    >/dev/null 2>&1
  then

    systemctl restart \
      avahi-daemon \
      >/dev/null 2>&1 || true

  fi


  # ---------------------------------------------------------------------------
  # Borrar solamente el estado de instalación.
  #
  # IMPORTANTE:
  # NO borrar /var/lib/pos-restaurant porque allí vive license.json.
  # ---------------------------------------------------------------------------

  rm -f \
    "$INSTALL_STATE_FILE"


  # El backup ya cumplió su función.
  if [ -n "${AVAHI_BACKUP:-}" ] \
    && [ -f "$AVAHI_BACKUP" ]
  then

    rm -f \
      "$AVAHI_BACKUP"

  fi

}


# =============================================================================
# INICIO
# =============================================================================

printf "%sPOS Restaurant - desinstalador%s\n" \
  "$BOLD" "$RESET"


# -----------------------------------------------------------------------------
# Validar privilegios
# -----------------------------------------------------------------------------

if [ "$EUID" -ne 0 ]; then

  fail "Ejecuta el desinstalador como root: sudo bash uninstall.sh"

fi


# -----------------------------------------------------------------------------
# Detectar usuario gráfico
# -----------------------------------------------------------------------------

TARGET_USER="${SUDO_USER:-}"


if [ -z "$TARGET_USER" ] \
  || [ "$TARGET_USER" = "root" ]
then

  TARGET_USER="$(
    logname 2>/dev/null || true
  )"

fi


# -----------------------------------------------------------------------------
# Detener Marcha Monitor
# -----------------------------------------------------------------------------

section "Deteniendo Marcha Monitor"


stop_monitor


# -----------------------------------------------------------------------------
# Detener servicios
# -----------------------------------------------------------------------------

section "Deteniendo servicios"


if command -v systemctl >/dev/null 2>&1; then

  systemctl stop \
    "$ZEROCONF_SERVICE" \
    >/dev/null 2>&1 || true


  systemctl stop \
    "$SERVICE_NAME" \
    >/dev/null 2>&1 || true


  systemctl disable \
    "$ZEROCONF_SERVICE" \
    >/dev/null 2>&1 || true


  systemctl disable \
    "$SERVICE_NAME" \
    >/dev/null 2>&1 || true

fi


# Aunque systemd ya haya ejecutado compose down,
# lo repetimos explícitamente para garantizar que
# no quede ningún contenedor de Marcha activo.

if command -v docker >/dev/null 2>&1; then

  if [ -f "${APP_DIR}/${COMPOSE_FILE}" ]; then

    cd "$APP_DIR"

    compose down || true

  fi

fi


success "Servicios detenidos"


# -----------------------------------------------------------------------------
# Quitar servicios systemd
# -----------------------------------------------------------------------------

section "Quitando servicios systemd"


rm -f \
  "/etc/systemd/system/${ZEROCONF_SERVICE}.service"


rm -f \
  "/etc/systemd/system/${SERVICE_NAME}.service"


systemctl daemon-reload \
  >/dev/null 2>&1 || true


systemctl reset-failed \
  "$SERVICE_NAME" \
  >/dev/null 2>&1 || true


systemctl reset-failed \
  "$ZEROCONF_SERVICE" \
  >/dev/null 2>&1 || true


success "Servicios systemd quitados"


# -----------------------------------------------------------------------------
# Restaurar red
# -----------------------------------------------------------------------------

section "Restaurando configuracion de red"


restore_network_configuration


# -----------------------------------------------------------------------------
# Quitar accesos directos de Marcha
# -----------------------------------------------------------------------------

section "Quitando accesos directos"


if [ -n "$TARGET_USER" ]; then

  DESKTOP_DIR="$(
    desktop_dir_for_user "$TARGET_USER" || true
  )"


  if [ -n "${DESKTOP_DIR:-}" ]; then

    rm -f \
      "${DESKTOP_DIR}/POS Restaurant - Iniciar.desktop" \
      "${DESKTOP_DIR}/POS Restaurant - Detener.desktop" \
      "${DESKTOP_DIR}/POS Restaurant - Actualizar.desktop"


    success "Accesos directos quitados de ${DESKTOP_DIR}"

  else

    warn "No pude detectar el escritorio del usuario"

  fi

else

  warn "No pude detectar el usuario de escritorio"

fi


# -----------------------------------------------------------------------------
# Quitar integración de Marcha Monitor
# -----------------------------------------------------------------------------

section "Quitando Marcha Monitor"


remove_monitor_user_integration \
  "$TARGET_USER"


remove_monitor_venv


success "Marcha Monitor desinstalado"


# -----------------------------------------------------------------------------
# Información sobre datos conservados
# -----------------------------------------------------------------------------

section "Datos"


warn "La desinstalacion conserva todos los datos."


printf "\nSe conservaron:\n"

printf "  Base de datos PostgreSQL\n"

printf "  Backups:       %s/backups\n" \
  "$APP_DIR"

printf "  Configuracion: %s/backend/.env\n" \
  "$APP_DIR"

printf "  Licencia:      %s\n" \
  "$LICENSE_FILE"

printf "  Codigo:        %s\n" \
  "$APP_DIR"


printf "\n%sATENCION:%s\n" \
  "$RED" "$RESET"


printf "Para ELIMINAR DEFINITIVAMENTE la base de datos:\n"

printf "  cd %s && docker compose -f %s down -v\n" \
  "$APP_DIR" \
  "$COMPOSE_FILE"


printf "%sEse comando destruye el volumen PostgreSQL.%s\n" \
  "$YELLOW" "$RESET"


printf "\nLos backups en %s/backups se conservan incluso si se elimina el volumen PostgreSQL.\n" \
  "$APP_DIR"


printf "\nLa licencia tambien se conserva en:\n"

printf "  %s\n" \
  "$LICENSE_FILE"


printf "\n%sDesinstalacion completada.%s\n" \
  "$GREEN" "$RESET"


printf "El codigo de la aplicacion sigue en:\n"

printf "  %s\n" \
  "$APP_DIR"


printf "\nMarcha Monitor:\n"

printf "  Autostart eliminado\n"

printf "  Acceso directo eliminado\n"

printf "  Entorno virtual eliminado\n"

printf "  Codigo conservado en: %s\n" \
  "$MONITOR_DIR"


printf "\nHostname mDNS utilizado por Marcha:\n"

printf "  %s.local\n" \
  "$HOSTNAME_LOCAL"