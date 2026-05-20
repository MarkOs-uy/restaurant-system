#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTNAME_LOCAL="pos"
FRONTEND_PORT="80"
BACKEND_PORT="8000"

echo "=== Instalando POS Restaurant ==="

if ! command -v apt-get >/dev/null 2>&1; then
  echo "Este instalador está pensado para Linux Debian/Ubuntu."
  exit 1
fi

if [ "$EUID" -ne 0 ]; then
  echo "Ejecutar como root: sudo bash install.sh"
  exit 1
fi

cd "$APP_DIR"

# =============================================================
echo "=== Instalando dependencias del sistema ==="
# =============================================================

apt-get update -qq
apt-get install -y \
  avahi-daemon \
  docker.io \
  docker-compose-plugin \
  libnss-mdns \
  python3 \
  python3-zeroconf

# =============================================================
echo "=== Configurando mDNS: ${HOSTNAME_LOCAL}.local ==="
# =============================================================

cp /etc/avahi/avahi-daemon.conf /etc/avahi/avahi-daemon.conf.pos-backup

if grep -q "^#\?host-name=" /etc/avahi/avahi-daemon.conf; then
  sed -i "s/^#\?host-name=.*/host-name=${HOSTNAME_LOCAL}/" /etc/avahi/avahi-daemon.conf
else
  sed -i "/^\[server\]/a host-name=${HOSTNAME_LOCAL}" /etc/avahi/avahi-daemon.conf
fi

systemctl enable avahi-daemon
systemctl restart avahi-daemon

# =============================================================
echo "=== Generando configuración ==="
# =============================================================

if [ ! -f "./backend/.env" ]; then

  LOCAL_IP=$(ip route get 1 | awk '{print $7;exit}')
  POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(16))")
  SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  ADMIN_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(12))")

  cat > ./backend/.env << EOF
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

  # Guardar para mostrar al final
  echo "$ADMIN_PASSWORD" > /tmp/pos_admin_pass

  echo "Configuración generada"

else
  echo "backend/.env ya existe — no se sobreescribe"
fi

# =============================================================
echo "=== Iniciando Docker ==="
# =============================================================

systemctl enable docker
systemctl start docker

until docker info >/dev/null 2>&1; do
  sleep 1
done

# =============================================================
echo "=== Construyendo e iniciando contenedores ==="
# =============================================================

docker compose -f docker-compose.prod.yml up -d --build

# Esperar postgres
echo "Esperando base de datos..."
for i in {1..30}; do
  if docker compose -f docker-compose.prod.yml exec -T db \
      pg_isready -U pos_user -d restaurant &>/dev/null; then
    break
  fi
  sleep 2
done

# =============================================================
echo "=== Inicializando base de datos ==="
# =============================================================

echo "Esperando backend..."

for i in {1..30}; do
  if docker compose -f docker-compose.prod.yml exec -T backend \
     python -c "print('ready')" &>/dev/null; then
    break
  fi
  sleep 2
done

docker compose -f docker-compose.prod.yml exec -T backend \
  alembic upgrade head

docker compose -f docker-compose.prod.yml exec -T backend \
  python -m app.seed

# =============================================================
echo "=== Registrando servicios del sistema ==="
# =============================================================

# Zeroconf
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

# Arranque automático del POS
tee /etc/systemd/system/pos-restaurant.service >/dev/null << EOF
[Unit]
Description=POS Restaurant
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${APP_DIR}
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pos-zeroconf
systemctl restart pos-zeroconf
systemctl enable pos-restaurant

# =============================================================
LOCAL_IP=$(ip route get 1 | awk '{print $7;exit}')
ADMIN_PASSWORD=$(cat /tmp/pos_admin_pass 2>/dev/null || echo "(ver backend/.env)")
rm -f /tmp/pos_admin_pass

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   POS Restaurant instalado con éxito     ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Acceso desde cualquier dispositivo en la red:"
echo "  → http://${HOSTNAME_LOCAL}.local"
echo "  → http://${LOCAL_IP}"
echo ""
echo "  Usuario: admin"
echo "  Contraseña: ${ADMIN_PASSWORD}"
echo ""
echo "  Guardá esta contraseña — no se vuelve a mostrar"
echo ""
echo "  Comandos útiles:"
echo "  → Logs:       cd ${APP_DIR} && docker compose -f docker-compose.prod.yml logs -f"
echo "  → Reiniciar:  systemctl restart pos-restaurant"
echo "  → Estado:     systemctl status pos-restaurant"
echo ""