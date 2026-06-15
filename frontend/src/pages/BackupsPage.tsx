import { useEffect, useState } from "react"
import toast from "react-hot-toast"
import { apiFetch } from "../api"

interface BackupStatus {
  last_backup_at: string | null
  last_backup_file: string | null
  last_backup_size: number | null
  email_enabled: boolean
  email_from: string | null
}

const emptyStatus: BackupStatus = {
  last_backup_at: null,
  last_backup_file: null,
  last_backup_size: null,
  email_enabled: false,
  email_from: null
}

function formatDateTime(value: string | null) {
  if (!value) return "Sin backups registrados"

  return new Date(value).toLocaleString("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  })
}

function formatBytes(value: number | null) {
  if (!value) return "Sin datos"

  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${(value / (1024 * 1024)).toFixed(1)} MB`
}

export default function BackupsPage() {
  const [status, setStatus] = useState<BackupStatus>(emptyStatus)
  const [email, setEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const [emailLoading, setEmailLoading] = useState(false)

  const loadStatus = async () => {
    const data = await apiFetch("/backups/status")
    setStatus(data)
  }

  useEffect(() => {
    loadStatus()
  }, [])

  const createBackup = async () => {
    setLoading(true)
    try {
      await apiFetch("/backups", { method: "POST" })
      toast.success("Backup generado correctamente")
      await loadStatus()
    } finally {
      setLoading(false)
    }
  }

  const createAndEmailBackup = async () => {
    if (!email.trim()) {
      toast.error("Ingresá un correo de destino")
      return
    }

    setEmailLoading(true)
    try {
      await apiFetch("/backups/email", {
        method: "POST",
        body: { email: email.trim() }
      })
      toast.success("Backup generado y enviado por correo")
      await loadStatus()
    } finally {
      setEmailLoading(false)
    }
  }

  return (
    <main className="backups-page">
      <header className="backups-header">
        <p>Administración</p>
        <h1>Backups</h1>
      </header>

      <section className="backup-section">
        <div className="backup-section__header">
          <div>
            <p>Estado actual</p>
            <h2>Último backup</h2>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            onClick={createBackup}
            disabled={loading || emailLoading}
          >
            {loading ? "Generando..." : "Realizar backup"}
          </button>
        </div>

        <div className="backup-status-grid">
          <div>
            <span>Fecha y hora</span>
            <strong>{formatDateTime(status.last_backup_at)}</strong>
          </div>
          <div>
            <span>Archivo</span>
            <strong>{status.last_backup_file || "Sin archivo"}</strong>
          </div>
          <div>
            <span>Tamaño</span>
            <strong>{formatBytes(status.last_backup_size)}</strong>
          </div>
          <div>
            <span>Correo configurado</span>
            <strong>{status.email_enabled ? status.email_from || "Disponible" : "No configurado"}</strong>
          </div>
        </div>
      </section>

      <section className="backup-section">
        <div className="backup-section__header">
          <div>
            <p>Envío externo</p>
            <h2>Backup por correo electrónico</h2>
          </div>
        </div>

        <div className="backup-email-form">
          <label>
            Correo destino
            <input
              type="email"
              placeholder="correo@ejemplo.com"
              value={email}
              onChange={event => setEmail(event.target.value)}
            />
          </label>

          <button
            type="button"
            className="btn btn-primary"
            onClick={createAndEmailBackup}
            disabled={emailLoading || loading || !status.email_enabled}
          >
            {emailLoading ? "Enviando..." : "Generar y enviar"}
          </button>
        </div>

        {!status.email_enabled && (
          <p className="backup-email-note">
            Configurá SMTP_HOST y SMTP_FROM o SMTP_USER en el backend para habilitar el envío por correo.
          </p>
        )}
      </section>
    </main>
  )
}
