# marcha_monitor.py

from datetime import datetime
import tkinter as tk
from tkinter import ttk
import webbrowser

from checks import (
    check_health,
    check_disk,
    check_frontend,
    check_systemd,
    get_server_address,
)

from config import (
    APP_NAME,
    CHECK_INTERVAL_MS,
    FRONTEND_URL,
)


class MarchaMonitor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("520x500")
        self.resizable(False, False)

        self.status_vars = {}

        self._build_ui()

        self.after(
            500,
            self.refresh_status,
        )

    def _build_ui(self):
        container = ttk.Frame(
            self,
            padding=20,
        )

        container.pack(
            fill="both",
            expand=True,
        )

        title = ttk.Label(
            container,
            text="MARCHA",
            font=("Arial", 24, "bold"),
        )

        title.pack(
            pady=(0, 15),
        )

        self.general_status = ttk.Label(
            container,
            text="Comprobando...",
            font=("Arial", 16, "bold"),
        )

        self.general_status.pack(
            pady=(0, 20),
        )

        self._add_status_row(
            container,
            "Servicio Marcha",
            "systemd",
        )

        self._add_status_row(
            container,
            "Backend",
            "backend",
        )

        self._add_status_row(
            container,
            "PostgreSQL",
            "database",
        )

        self._add_status_row(
            container,
            "Redis",
            "redis",
        )

        self._add_status_row(
            container,
            "Último backup",
            "backup",
        )

        self._add_status_row(
            container,
            "Interfaz web",
            "frontend",
        )

        self._add_status_row(
            container,
            "Disco",
            "disk",
        )

        ttk.Separator(
            container,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=20,
        )

        self.server_ip = ttk.Label(
            container,
            text=f"Servidor Marcha: {get_server_address()}",
        )

        self.server_ip.pack(
            anchor="w",
        )

        self.version_label = ttk.Label(
            container,
            text="Versión: -",
        )

        self.version_label.pack(
            anchor="w",
            pady=(5, 0),
        )

        self.last_check = ttk.Label(
            container,
            text="Última comprobación: -",
        )

        self.last_check.pack(
            anchor="w",
            pady=(5, 20),
        )

        button_frame = ttk.Frame(container)
        button_frame.pack()

        ttk.Button(
            button_frame,
            text="Abrir Marcha",
            command=self.open_marcha,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            button_frame,
            text="Actualizar",
            command=self.refresh_status,
        ).pack(
            side="left",
            padx=5,
        )

    def _add_status_row(
        self,
        parent,
        label: str,
        key: str,
    ):
        frame = ttk.Frame(parent)

        frame.pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            frame,
            text=label,
            width=24,
        ).pack(
            side="left",
        )

        value = ttk.Label(
            frame,
            text="-",
            font=("Arial", 10, "bold"),
        )

        value.pack(
            side="right",
        )

        self.status_vars[key] = value

    def _set_status(
        self,
        key,
        result,
    ):
        if not result.applicable:
            text = f"— {result.status}"

        elif result.ok and not result.warning:
            text = f"● {result.status}"

        elif result.warning:
            text = f"⚠ {result.status}"

        else:
            text = f"● {result.status}"

        self.status_vars[key].config(
            text=text,
        )

    def refresh_status(self):
        systemd = check_systemd()
        health = check_health()

        backend = health.backend
        database = health.database
        redis = health.redis
        backup = health.backup
        frontend = check_frontend()
        disk = check_disk()

        self._set_status(
            "systemd",
            systemd,
        )

        self._set_status(
            "backend",
            backend,
        )

        self._set_status(
            "database",
            database,
        )

        self._set_status(
            "redis",
            redis,
        )

        self._set_status(
            "backup",
            backup,
        )

        self._set_status(
            "frontend",
            frontend,
        )

        self._set_status(
            "disk",
            disk,
        )

        results = [
            systemd,
            backend,
            database,
            redis,
            backup,
            frontend,
            disk,
        ]

        applicable_results = [
            result
            for result in results
            if result.applicable
        ]

        if any(not item.ok for item in applicable_results):
            general = "● SISTEMA CON ERROR"

        elif any(item.warning for item in applicable_results):
            general = "⚠ SISTEMA CON ADVERTENCIAS"

        else:
            general = "● SISTEMA OPERATIVO"

        self.general_status.config(
            text=general,
        )

        self.server_ip.config(
            text=f"Servidor Marcha: {get_server_address()}",
        )

        self.last_check.config(
            text=(
                "Última comprobación: "
                f"{datetime.now().strftime('%H:%M:%S')}"
            )
        )

        self.version_label.config(
            text=f"Versión: {health.version}",
        )

        self.after(
            CHECK_INTERVAL_MS,
            self.refresh_status,
        )

    def open_marcha(self):
        webbrowser.open(FRONTEND_URL)


if __name__ == "__main__":
    app = MarchaMonitor()
    app.mainloop()