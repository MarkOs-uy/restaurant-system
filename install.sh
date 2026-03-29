#!/bin/bash
set -e

echo "=== Instalando POS Restaurant ==="

# 1. Dependencias del sistema
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip docker.io docker-compose-plugin

# 2. Dependencias Python del HOST (solo para Zeroconf)
#    No necesita todo el requirements.txt del backend,
#    solo lo necesario para el script
pip3 install "zeroconf>=0.132"

# 3. Levantar los contenedores
docker compose up -d

# 4. Registrar Zeroconf como servicio del sistema
#    Para que arranque solo y sobreviva reinicios
sudo bash -c "cat > /etc/systemd/system/pos-zeroconf.service" << EOF
[Unit]
Description=POS Zeroconf Announcer
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/scripts/announce_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable pos-zeroconf
sudo systemctl start pos-zeroconf

echo "=== Instalación completa ==="
echo "Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo "Frontend: http://$(hostname -I | awk '{print $1}'):5173"
```

---

## Resumen del flujo completo
```
Host (Linux)
├── systemd: pos-zeroconf.service
│   └── python3 scripts/announce_service.py  ← anuncia IP:8000 via mDNS
│
└── Docker Compose
    ├── db        ← postgres (red interna)
    ├── backend   ← ve "db" y "redis" por nombre ✅
    ├── redis     ← red interna
    ├── frontend  ← puerto 5173
    └── backup    ← ve "db" por nombre ✅