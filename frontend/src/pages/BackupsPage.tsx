import { useEffect, useState } from "react"
import { waitForServer } from "../services/health"
import toast from "react-hot-toast"
import { apiFetch } from "../api"
import { downloadBackup } from "../services/downloadBackup"

interface BackupStatus {
  last_backup_at: string | null
  last_backup_file: string |null
  last_backup_size: number | null
  last_backup_source: string | null

  email_enabled: boolean
  email_from: string | null

  last_automatic_backup_at: string | null
  next_automatic_backup_at: string | null
  last_backup_result: string | null
}

interface SystemSettings {
  smtp_host: string
  smtp_port: number
  smtp_user: string
  smtp_password: string
  smtp_from: string
  smtp_use_tls: boolean

  backup_email: string

  backup_enabled: boolean
  backup_frequency: string
  backup_retention_daily: number
  backup_retention_weekly: number
  backup_retention_monthly: number
  backup_time: string
  backup_weekday: number | null
  backup_monthday: number | null

  backup_keep_local: boolean
  backup_send_email: boolean

  backup_timezone: string
}

interface BackupFile {
    filename: string
    created_at: string
    size: number
    type: string
}

const emptyStatus: BackupStatus = {
last_backup_at: null,
last_backup_file: null,
last_backup_size: null,
last_backup_source: null,
email_enabled: false,
email_from: null,
last_automatic_backup_at: null,
next_automatic_backup_at: null,
last_backup_result: null
}

const emptySettings: SystemSettings = {
  smtp_host: "",
  smtp_port: 587,
  smtp_user: "",
  smtp_password: "",
  smtp_from: "",
  smtp_use_tls: true,

  backup_email: "",

  backup_enabled: false,
  backup_frequency: "manual",
  backup_retention_daily: 30,
  backup_retention_weekly: 4,
  backup_retention_monthly: 12,

  backup_time: "03:00:00",
  backup_weekday: 0,
  backup_monthday: 1,

  backup_keep_local: true,
  backup_send_email: true,

  backup_timezone: "America/Montevideo"
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
  const [settings, setSettings] = useState<SystemSettings>(emptySettings)

  const [loading, setLoading] = useState(false)
  const [emailLoading, setEmailLoading] = useState(false)
  const [settingsLoading, setSettingsLoading] = useState(false)
  const [testLoading, setTestLoading] = useState(false)
  const [files,setFiles]=useState<BackupFile[]>([])

  const loadStatus = async () => {
    const data = await apiFetch("/backups/status")
    setStatus(data)
  }

  const loadSettings = async () => {
    const data = await apiFetch("/settings")
    setSettings(data)
  }

  const loadFiles = async()=>{
      const data=await apiFetch("/backups/files")
      setFiles(data)
  }


  useEffect(() => {
    loadStatus()
    loadSettings()
    loadFiles()

    const statusTimer = window.setInterval(() => {
      loadStatus()
    }, 30000)

    return () => {
      window.clearInterval(statusTimer)
    }
  }, [])

  const createBackup = async () => {
    setLoading(true)
    try {
      await apiFetch("/backups", {
        method: "POST"
      })
      toast.success("Backup generado correctamente")
      await loadStatus()
      await loadFiles()
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    setSettingsLoading(true)
    try {
      await apiFetch("/settings", {
        method: "PATCH",
        body: settings
      })
      toast.success("Configuración guardada")
      await loadStatus()
    } finally {
      setSettingsLoading(false)
    }
  }

  const createAndEmailBackup = async () => {
    if (!settings.backup_email.trim()) {
      toast.error("Ingresa un correo destino")
      return
    }
    setEmailLoading(true)
    try {
      await apiFetch("/backups/email", {
        method: "POST",
        body: {
          email: settings.backup_email.trim()
        }
      })
      toast.success("Backup generado y enviado")
      await loadStatus()
      await loadFiles()
    } finally {
      setEmailLoading(false)
    }
  }

  const testEmail = async () => {
    setTestLoading(true)
    try {
      await apiFetch("/settings/test-email", {
        method: "POST"
      })
      toast.success("Correo de prueba enviado")
    } finally {
      setTestLoading(false)
    }
  }

  const restoreBackup = async (filename: string) => {
    if (!window.confirm(
      "¿Restaurar este backup?\n\nSe reemplazarán todos los datos actuales."
    )) {
      return
    }
    setLoading(true)
    try {
      const result = await apiFetch(
          `/backups/restore/${filename}`,
          {
              method: "POST"
          }
      )
      if (result.restart_required) {
        toast.loading(
          "Restaurando base de datos...\nEsperando que el servidor vuelva a estar disponible.",
          {
            id: "restore"
          }
        )
        const ok = await waitForServer()
        toast.dismiss("restore")
        if (ok) {
          toast.success("Backup restaurado correctamente.")
          window.location.reload()
        } else {
          toast.error(
            "La restauración terminó, pero el servidor aún no responde."
          )
        }
      } else {
        toast.success("Backup restaurado correctamente.")
        await loadStatus()
        await loadFiles()
      }
    } finally {
      setLoading(false)
    }
  }

  const deleteBackup = async(filename:string)=>{
      if(!window.confirm("Eliminar backup?"))
          return
      await apiFetch(`/backups/${encodeURIComponent(filename)}`,{
          method:"DELETE"
      })
      toast.success("Backup eliminado")
      await loadFiles()
  }

  const handleDownload = async (filename: string) => {
    try {
      await downloadBackup(filename)
      toast.success("Backup descargado")
    } catch {
      toast.error("No fue posible descargar el backup")
    }
  }


  function frequencyLabel(freq: string) {

    switch (freq) {
      case "daily":
        return "Diario"

      case "weekly":
        return "Semanal"

      case "monthly":
        return "Mensual"

      default:
        return "Manual"
    }

  }

  function backupTypeLabel(type: string) {
    switch (type) {
      case "manual":
        return "Manual"

      case "daily":
        return "Diario"

      case "weekly":
        return "Semanal"

      case "monthly":
        return "Mensual"

      case "before_restore":
        return "Antes de restaurar"

      default:
        return type
    }
  }

  return (
    <main className="backups-page">

      <header className="backups-header">
        <p>Administración</p>
        <h1>Backups y Correo</h1>
      </header>

      <section className="backup-section">

        <div className="backup-section__header">
          <div>
            <p>Estado actual</p>
            <h2>Último backup</h2>
          </div>
        </div>

        <div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={createBackup}
            disabled={loading || emailLoading}
          >
            {loading
              ? "Generando..."
              : "Realizar backup"}
          </button>
        </div>

        <div className="backup-status-grid">
          <div>
            <span>Fecha y hora</span>
            <strong>
              {formatDateTime(status.last_backup_at)}
            </strong>
          </div>
          <div>
            <span>Tipo</span>
            <strong>
              {backupTypeLabel(status.last_backup_source || "manual")}
            </strong>
          </div>
          <div>
            <span>Archivo</span>
            <strong>
              {status.last_backup_file || "Sin archivo"}
            </strong>
          </div>
          <div>
            <span>Tamaño</span>
            <strong>
              {formatBytes(status.last_backup_size)}
            </strong>
          </div>
          <div>
            <span>Correo configurado</span>
            <strong>
              {status.email_enabled
                ? status.email_from || "Disponible"
                : "No configurado"}
            </strong>
          </div>
        </div>

        <div>
          <span>Último backup automático</span>
          <strong>
            {formatDateTime(status.last_automatic_backup_at)}
          </strong>
          <span>Próximo backup</span>
          <strong>
            {formatDateTime(status.next_automatic_backup_at)}
          </strong>
          <span>Resultado</span>
          <strong>
            {status.last_backup_result || "Sin resultados"}
          </strong>
        </div>

      </section>

      <section className="backup-section">
        <div className="backup-section__header">
          <div>
            <p>Configuración</p>
            <h2>Programar Backup</h2>
          </div>       
          <button
            className="btn btn-primary"
            onClick={saveSettings}
            disabled={settingsLoading}
          >
            {settingsLoading
              ? "Guardando..."
              : "Guardar configuración"}
          </button>  
        </div>
        <div className="backup-schedule-form">
          <div className="backup-status-grid">
            <div>
              <label className="checkbox-label">
                <span>Habilitar backups automáticos</span>
                <input
                  type="checkbox"
                  checked={settings.backup_enabled}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_enabled: e.target.checked
                    })
                  }
                />
              </label>
            </div>

            <div>
              <label className="checkbox-label">
                <span>Conservar backup local</span>

                <input
                  type="checkbox"
                  checked={settings.backup_keep_local}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_keep_local: e.target.checked
                    })
                  }
                />
              </label>
            </div>


            <div>
              <label className="checkbox-label">
                <span>Enviar backup por correo</span>

                <input
                  type="checkbox"
                  checked={settings.backup_send_email}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_send_email: e.target.checked
                    })
                  }
                />
              </label>
            </div>



            <div>
              <label>
                Frecuencia
                <select
                  value={settings.backup_frequency}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_frequency: e.target.value
                    })
                  }
                >
                  <option value="manual">Manual</option>
                  <option value="daily">Diario</option>
                  <option value="weekly">Semanal</option>
                  <option value="monthly">Mensual</option>
                </select>
              </label>
            </div>

            <div>
              <label>
                Hora

                <input
                  type="time"
                  value={settings.backup_time.substring(0,5)}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_time: `${e.target.value}:00`
                    })
                  }
                />

              </label>
            </div>

            {
            settings.backup_frequency === "weekly" && (

            <div>
              <label>
                Día de la semana

                <select
                  value={settings.backup_weekday ?? 0}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_weekday: Number(e.target.value)
                    })
                  }
                >
                  <option value={0}>Lunes</option>
                  <option value={1}>Martes</option>
                  <option value={2}>Miércoles</option>
                  <option value={3}>Jueves</option>
                  <option value={4}>Viernes</option>
                  <option value={5}>Sábado</option>
                  <option value={6}>Domingo</option>
                </select>

              </label>
            </div>

            )}


            {
            settings.backup_frequency === "monthly" && (

            <div>
              <label>
                Día del mes

                <input
                  type="number"
                  min={1}
                  max={31}
                  value={settings.backup_monthday ?? 1}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_monthday: Number(e.target.value)
                    })
                  }
                />

              </label>
            </div>

            )}

            <div>
              <label>
                Conservar backups diarios(días)
                <input
                  type="number"
                  min={1}
                  value={settings.backup_retention_daily}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_retention_daily: Number(e.target.value)
                    })
                  }
                />
              </label>
              <label>
                Conservar backups semanales (días)
                <input
                  type="number"
                  min={1}
                  value={settings.backup_retention_weekly}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_retention_weekly: Number(e.target.value)
                    })
                  }
                />
              </label>
                            <label>
                Conservar backups mensuales (días)
                <input
                  type="number"
                  min={1}
                  value={settings.backup_retention_monthly}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_retention_monthly: Number(e.target.value)
                    })
                  }
                />
              </label>
            </div>
          </div>
        </div>
      </section>

      <section className="backup-section">

        <div className="backup-section__header">
          <div>
            <p>Configuración</p>
            <h2>Servidor SMTP</h2>
          </div>

          <button
            className="btn btn-primary"
            onClick={saveSettings}
            disabled={settingsLoading}
          >
            {settingsLoading
              ? "Guardando..."
              : "Guardar configuración"}
          </button>
        </div>

        <div className="backup-email-form">
          <div className="backup-status-grid">
            <div className="backup-field-group">
              <label>
                SMTP Host
                <input
                  value={settings.smtp_host}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      smtp_host: e.target.value
                    })
                  }
                />
              </label>

              <label>
                Puerto
                <input
                  type="number"
                  value={settings.smtp_port}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      smtp_port: Number(e.target.value)
                    })
                  }
                />
              </label>
            </div>
            <div className="backup-field-group">
              <label>
                Usuario
                <input
                  value={settings.smtp_user}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      smtp_user: e.target.value
                    })
                  }
                />
              </label>

              <label>
                Contraseña
                <input
                  type="password"
                  value={settings.smtp_password}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      smtp_password: e.target.value
                    })
                  }
                />
              </label>
            </div>
            <div className="backup-field-group">
              <label>
                Remitente
                <input
                  value={settings.smtp_from}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      smtp_from: e.target.value
                    })
                  }
                />
              </label>

              <label>
                Correo para backups
                <input
                  type="email"
                  value={settings.backup_email}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      backup_email: e.target.value
                    })
                  }
                />
              </label>
            </div>
            <div>
              <label className="checkbox-label">
                <span>Usar TLS</span>
                <input
                  type="checkbox"
                  checked={settings.smtp_use_tls}
                  onChange={e =>
                    setSettings({
                      ...settings,
                      smtp_use_tls: e.target.checked
                    })
                  }
                />
              </label>
            </div>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            gap: 10,
            marginTop: 20
          }}
        >

          <button
            type="button"
            className="btn btn-secondary"
            onClick={testEmail}
            disabled={testLoading}
          >
            {testLoading
              ? "Probando..."
              : "Probar correo"}
          </button>

        </div>

      </section>

      <section className="backup-section">

        <div className="backup-section__header">
          <div>
            <p>Envío externo</p>
            <h2>Backup por correo electrónico</h2>
          </div>
        </div>

        <div className="backup-send-layout">
          <button
            type="button"
            className="btn btn-primary"
            onClick={createAndEmailBackup}
            disabled={
              emailLoading ||
              loading ||
              !status.email_enabled
            }
          >
            {emailLoading
              ? "Enviando..."
              : "Generar y enviar"}
          </button>
          <div className="backup-send-info">

            <div>
              <span>Último automático</span>

              <strong>
                {formatDateTime(status.last_automatic_backup_at)}
              </strong>

            </div>

            <div>
              <span>Próximo backup</span>

              <strong>
                {formatDateTime(status.next_automatic_backup_at)}
              </strong>

            </div>

            <div>
              <span>Frecuencia</span>

              <strong>
                {frequencyLabel(settings.backup_frequency)}
              </strong>

            </div>

          </div>
        </div>
      </section>

      <section className="backup-section">

        <h2>Historial de Backups</h2>

          <table className="backup-files">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Tamaño</th>
                <th>Archivo</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {files.map(file=>(
                <tr key={file.filename}>
                  <td>{backupTypeLabel(file.type)}</td>
                  <td>{formatDateTime(file.created_at)}</td>
                  <td>{formatBytes(file.size)}</td>
                  <td>{file.filename}</td>                  
                  <td>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={()=>handleDownload(file.filename)}
                    >
                      Descargar
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={()=>restoreBackup(file.filename)}
                    >
                      Restaurar
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={()=>deleteBackup(file.filename)}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
            ))}
            </tbody>
          </table>
        </section>

    </main>
  )
}
