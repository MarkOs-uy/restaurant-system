import os

APP_NAME = "Marcha Monitor"

MARCHA_HOST = os.getenv(
    "MARCHA_HOST",
    "localhost",
)

BASE_URL = f"http://{MARCHA_HOST}"

HEALTH_URL = f"{BASE_URL}/api/health"
FRONTEND_URL = BASE_URL

SYSTEMD_SERVICE = "pos-restaurant.service"

CHECK_INTERVAL_MS = 5000

DISK_WARNING_PERCENT = 90
DISK_CRITICAL_PERCENT = 95