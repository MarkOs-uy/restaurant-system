#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${APP_DIR}/backend/.env"
HOSTNAME_LOCAL="pos"
FRONTEND_PORT="80"
BACKEND_PORT="8000"
COMPOSE_FILE="docker-compose.prod.yml"

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

section() {
  printf "\n%s==> %s%s\n" "$BLUE" "$1" "$RESET"
}

success() {
  printf "%s[OK]%s %s\n" "$GREEN" "$RESET" "$1"
}

warn() {
  printf "%s[AVISO]%s %s\n" "$YELLOW" "$RESET" "$1"
}

fail() {
  printf "%s[ERROR]%s %s\n" "$RED" "$RESET" "$1" >&2
  exit 1
}

get_local_ip() {
  ip route get 1.1.1.1 2>/dev/null | awk '{for (i=1; i<=NF; i++) if ($i=="src") {print $(i+1); exit}}'
}

env_value() {
  awk -F= -v key="$1" '$1 == key {sub(/\r$/, ""); print substr($0, index($0, "=") + 1); exit}' "$ENV_FILE"
}

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

wait_for_postgres() {
  local ready=0

  for _ in {1..30}; do
    if compose exec -T db pg_isready -U "${POSTGRES_USER_VALUE:-pos_user}" -d "${POSTGRES_DB_VALUE:-restaurant}" >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 2
  done

  [ "$ready" -eq 1 ] || fail "Postgres no respondio despues de 60 segundos. Revisa: docker compose -f ${COMPOSE_FILE} logs db"
}

wait_for_backend() {
  local ready=0

  for _ in {1..45}; do
    if compose exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 2
  done

  [ "$ready" -eq 1 ] || fail "El backend no quedo listo despues de 90 segundos. Revisa: docker compose -f ${COMPOSE_FILE} logs backend"
}

printf "%sPOS Restaurant - instalador de produccion%s\n" "$BOLD" "$RESET"

if ! command -v apt-get >/dev/null 2>&1; then
  fail "Este instalador esta pensado para Linux Debian/Ubuntu."
fi

if [ "$EUID" -ne 0 ]; then
  fail "Ejecuta el instalador como root: sudo bash install.sh"
fi

cd "$APP_DIR"

section "Instalando dependencias del sistema"
apt-get update -qq
apt-get install -y \
  avahi-daemon \
  ca-certificates \
  curl \
  gnupg \
  iproute2 \
  libnss-mdns \
  python3 \
  python3-zeroconf
success "Dependencias base instaladas"

section "Instalando Docker"
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
  warn "Docker ya instalado — omitiendo"
else
  # Detectar Ubuntu o Debian automaticamente
  . /etc/os-release
  if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
    fail "Sistema no soportado: $ID. Se requiere Ubuntu o Debian."
  fi

  printf "Sistema detectado: %s %s\n" "$ID" "$VERSION_CODENAME"

  # Remover versiones viejas si existen
  apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

  # Clave GPG oficial de Docker
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/${ID}/gpg" \
    -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc

  # Repositorio oficial — mismo mecanismo para Ubuntu y Debian
  echo \
    "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/${ID} \
    ${VERSION_CODENAME} stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null

  apt-get update -qq
  apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

  success "Docker instalado"
fi

section "Configurando mDNS: ${HOSTNAME_LOCAL}.local"
AVAHI_CONF="/etc/avahi/avahi-daemon.conf"
AVAHI_BACKUP="/etc/avahi/avahi-daemon.conf.pos-backup.$(date +%Y%m%d%H%M%S)"
cp "$AVAHI_CONF" "$AVAHI_BACKUP"

if grep -q "^#\?host-name=" "$AVAHI_CONF"; then
  sed -i "s/^#\?host-name=.*/host-name=${HOSTNAME_LOCAL}/" "$AVAHI_CONF"
else
  sed -i "/^\[server\]/a host-name=${HOSTNAME_LOCAL}" "$AVAHI_CONF"
fi

systemctl enable avahi-daemon >/dev/null
hostnamectl set-hostname $HOSTNAME_LOCAL
systemctl restart avahi-daemon
success "mDNS activo como ${HOSTNAME_LOCAL}.local"

section "Generando configuracion"
ENV_CREATED=0
ADMIN_PASSWORD=""
LOCAL_IP="$(get_local_ip)"

if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi

[ -n "$LOCAL_IP" ] || fail "No pude detectar la IP local del servidor."

if [ ! -f "$ENV_FILE" ]; then
  POSTGRES_PASSWORD="$(python3 -c "import secrets; print(secrets.token_hex(16))")"
  SECRET_KEY="$(python3 -c "import secrets; print(secrets.token_hex(32))")"
  ADMIN_PASSWORD="$(python3 -c "import secrets; print(secrets.token_urlsafe(12))")"

  cat > "$ENV_FILE" << EOF
POSTGRES_USER=pos_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=restaurant
DATABASE_URL=postgresql://pos_user:${POSTGRES_PASSWORD}@db:5432/restaurant

SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

CORS_ORIGINS=http://localhost,http://${LOCAL_IP},http://${HOSTNAME_LOCAL}.local

REDIS_HOST=redis
REDIS_PORT=6379

ADMIN_SEED_PASSWORD=${ADMIN_PASSWORD}

ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

  chmod 600 "$ENV_FILE"
  ENV_CREATED=1
  success "Configuracion creada en backend/.env"
else
  warn "backend/.env ya existe; no se sobreescribe."
fi

POSTGRES_USER_VALUE="$(env_value POSTGRES_USER)"
POSTGRES_DB_VALUE="$(env_value POSTGRES_DB)"

section "Iniciando Docker"
systemctl enable docker >/dev/null
systemctl start docker

until docker info >/dev/null 2>&1; do
  sleep 1
done
success "Docker esta listo"

section "Construyendo e iniciando contenedores"
compose up -d --build
success "Contenedores iniciados"

section "Verificando servicios"
printf "Esperando base de datos...\n"
wait_for_postgres
success "Postgres responde"

printf "Esperando backend...\n"
wait_for_backend
success "Backend responde en /health"

section "Registrando servicios del sistema"
tee /etc/systemd/system/pos-zeroconf.service >/dev/null << EOF
[Unit]
Description=POS Zeroconf Announcer
After=network-online.target avahi-daemon.service docker.service
Wants=network-online.target
Requires=avahi-daemon.service docker.service

[Service]
Type=simple
WorkingDirectory=${APP_DIR}
Environment=POS_HOSTNAME=${HOSTNAME_LOCAL}.local
Environment=POS_FRONTEND_PORT=${FRONTEND_PORT}
Environment=POS_BACKEND_PORT=${BACKEND_PORT}
ExecStart=/usr/bin/python3 ${APP_DIR}/scripts/announce_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

tee /etc/systemd/system/pos-restaurant.service >/dev/null << EOF
[Unit]
Description=POS Restaurant
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${APP_DIR}
ExecStart=/usr/bin/docker compose -f ${COMPOSE_FILE} up -d
ExecStop=/usr/bin/docker compose -f ${COMPOSE_FILE} down
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pos-zeroconf >/dev/null
systemctl restart pos-zeroconf
systemctl enable pos-restaurant >/dev/null
success "Servicios systemd registrados"

LOCAL_IP="$(get_local_ip)"
if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi

printf "\n%s+--------------------------------------------------+%s\n" "$GREEN" "$RESET"
printf "%s|       POS Restaurant instalado con exito         |%s\n" "$GREEN" "$RESET"
printf "%s+--------------------------------------------------+%s\n" "$GREEN" "$RESET"
printf "\n%sAcceso en la red local:%s\n" "$BOLD" "$RESET"
printf "  %shttp://%s.local%s\n" "$BLUE" "$HOSTNAME_LOCAL" "$RESET"
printf "  %shttp://%s%s\n" "$BLUE" "$LOCAL_IP" "$RESET"

printf "\n%sCredenciales iniciales:%s\n" "$BOLD" "$RESET"
printf "  Usuario:    admin\n"
if [ "$ENV_CREATED" -eq 1 ]; then
  printf "  Contrasena: %s\n" "$ADMIN_PASSWORD"
  printf "\n%sGuarda esta contrasena ahora; no se volvera a mostrar en pantalla.%s\n" "$YELLOW" "$RESET"
else
  printf "  Contrasena: ya configurada anteriormente en backend/.env\n"
fi

printf "\n%sComandos utiles:%s\n" "$BOLD" "$RESET"
printf "  Logs:       cd %s && docker compose -f %s logs -f\n" "$APP_DIR" "$COMPOSE_FILE"
printf "  Reiniciar:  systemctl restart pos-restaurant\n"
printf "  Estado:     systemctl status pos-restaurant\n"
printf "  Backup:     ls -lh %s/backups\n" "$APP_DIR"
printf "\n"
