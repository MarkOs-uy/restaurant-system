import { useEffect, useState } from "react"
import { waitForServer } from "../services/health"
import toast from "react-hot-toast"
import { apiFetch } from "../api"
import { downloadBackup } from "../services/downloadBackup"
import { BackupType } from "../types/backup"
import { BackupFrequency } from "../types/systemSettings"

import type { 
  BackupStatus,
  BackupFile,
  BackupRestoreResponse
} from "../types/backup"
import type { 
  SystemSettings, 
  RawSystemSettings 
} from "../types/systemSettings"


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
  backup_frequency: BackupFrequency.MANUAL,
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

function formatDateTime(value: string | null): string {
  if (!value) {
    return "Sin backups registrados"
  }
  return new Date(value).toLocaleString(
    "es-UY",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    }
  )
}

function formatBytes(value: number | null): string {
  if (value === null) {
    return "Sin datos"
  }
  if (value < 1024) {
    return `${value} B`
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`
  }
  return `${
    (value / (1024 * 1024)).toFixed(1)
  } MB`
}

function normalizeSystemSettings(
  data: RawSystemSettings
): SystemSettings {
  return {
    smtp_host:
      data.smtp_host ?? "",

    smtp_port:
      data.smtp_port,

    smtp_user:
      data.smtp_user ?? "",

    smtp_password: "",

    smtp_from:
      data.smtp_from ?? "",

    smtp_use_tls:
      data.smtp_use_tls,

    backup_email:
      data.backup_email ?? "",

    backup_enabled:
      data.backup_enabled,

    backup_frequency:
      data.backup_frequency,

    backup_time:
      data.backup_time,

    backup_weekday:
      data.backup_weekday ?? 0,

    backup_monthday:
      data.backup_monthday ?? 1,

    backup_retention_daily:
      data.backup_retention_daily,

    backup_retention_weekly:
      data.backup_retention_weekly,

    backup_retention_monthly:
      data.backup_retention_monthly,

    backup_keep_local:
      data.backup_keep_local,

    backup_send_email:
      data.backup_send_email,

    backup_timezone:
      data.backup_timezone
  }
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
    const data = await apiFetch<BackupStatus>("/backups/status")
    setStatus(data)
  }

  const loadSettings = async () => {
    const data = await apiFetch<RawSystemSettings>("/settings")
    setSettings(normalizeSystemSettings(data))
  }

  const loadFiles = async()=>{
      const data=await apiFetch<BackupFile[]>("/backups/files")
      setFiles(data)
  }


  useEffect(() => {
    const init = async () => {
      await Promise.all([
        loadStatus(),
        loadSettings(),
        loadFiles()
      ])
    }

    init()

    const statusTimer =
      window.setInterval(
        loadStatus,
        30000
      )

    return () => {
      window.clearInterval(
        statusTimer
      )
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
      const {
        smtp_password,
        ...rest
      } = settings

      const payload = {
        ...rest,
        ...(smtp_password.trim()
          ? { smtp_password }
          : {})
      }

      await apiFetch("/settings", {
        method: "PATCH",
        body: payload
      })

      toast.success(
        "Configuración guardada"
      )

      await Promise.all([
        loadStatus(),
        loadSettings()
      ])

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
      const result = await apiFetch<BackupRestoreResponse>(
          `/backups/restore/${encodeURIComponent(filename)}`,
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
      await apiFetch(`/backups/${encodeURIComponent(filename)}`, {method:"DELETE"})
      toast.success("Backup eliminado")
      await Promise.all([
        loadFiles(),
        loadStatus()
      ])
  }

  const handleDownload = async (filename: string) => {
    try {
      await downloadBackup(filename)
      toast.success("Backup descargado")
    } catch {
      toast.error("No fue posible descargar el backup")
    }
  }

  function backupTypeLabel(
    type: BackupType
  ): string {
    switch (type) {
      case BackupType.MANUAL:
        return "Manual"

      case BackupType.DAILY:
        return "Diario"

      case BackupType.WEEKLY:
        return "Semanal"

      case BackupType.MONTHLY:
        return "Mensual"

      case BackupType.BEFORE_RESTORE:
        return "Antes de restaurar"

      default:
        return "Desconocido"
    }
  }

  return (
    <main className="backups-page">

      <header className="backups-header">
        <p>Administración</p>
        <h1>Backups y Correo</h1>
      </header>


      {/* Backup - Estado actual */}
      <section className="backup-section">

        <div className="backup-section__header">
          <div>
            <p>Estado actual</p>
            <h2>Backups</h2>
          </div>

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


        <div className="backup-status-group">

          <h3>Último backup realizado</h3>

          <div className="backup-status-grid">

            <div>
              <span>Fecha y hora</span>
              <strong>
                {formatDateTime(
                  status.last_backup_at
                )}
              </strong>
            </div>

            <div>
              <span>Archivo</span>
              <strong>
                {status.last_backup_file ||
                  "Sin archivo"}
              </strong>
            </div>

            <div>
              <span>Tamaño</span>
              <strong>
                {formatBytes(
                  status.last_backup_size
                )}
              </strong>
            </div>

          </div>

        </div>


        <div className="backup-status-group">

          <h3>Backups automáticos</h3>

          <div className="backup-status-grid">

            <div>
              <span>Fecha del último backup automático</span>
              <strong>
                {formatDateTime(
                  status.last_automatic_backup_at
                )}
              </strong>
            </div>

            <div>
              <span>Fecha del próximo backup automático</span>
              <strong>
                {formatDateTime(
                  status.next_automatic_backup_at
                )}
              </strong>
            </div>

            <div>
              <span>Último resultado</span>
              <strong>
                {status.last_backup_result ||
                  "Sin resultados"}
              </strong>
            </div>

          </div>

        </div>

      </section>


      {/* Configuración - Backups automáticos */}
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




        <div className="backup-config-group">

          <h3>Automatización</h3>

          <div className="backup-status-grid">

            <div>
              <label className="checkbox-label">
                <span>
                  Habilitar backups automáticos
                </span>

                <input
                  type="checkbox"
                  checked={
                    settings.backup_enabled
                  }
                  onChange={event =>
                    setSettings({
                      ...settings,
                      backup_enabled:
                        event.target.checked
                    })
                  }
                />
              </label>
            </div>


            <div>
              <label>
                Frecuencia

                <select
                  value={
                    settings.backup_frequency
                  }
                  disabled={
                    !settings.backup_enabled
                  }
                  onChange={event =>
                    setSettings({...settings, backup_frequency: event.target.value as BackupFrequency})
                  }
                >
                  <option value={BackupFrequency.MANUAL}>Manual</option>
                  <option value={BackupFrequency.DAILY}>Diario</option>
                  <option value={BackupFrequency.WEEKLY}>Semanal</option>
                  <option value={BackupFrequency.MONTHLY}>Mensual</option>
                </select>
              </label>
            </div>


            <div>
              <label>
                Hora

                <input
                  type="time"
                  disabled={
                    !settings.backup_enabled ||
                    settings.backup_frequency ===
                      BackupFrequency.MANUAL
                  }
                  value={settings.backup_time.substring(0,5)}
                  onChange={e =>setSettings({...settings, backup_time: `${e.target.value}:00`})}
                />
              </label>
            </div>

            {settings.backup_frequency === BackupFrequency.WEEKLY && (
              <div>
                <label>
                  Día de la semana
                  <select
                    value={settings.backup_weekday ?? 0}
                    onChange={e => setSettings({...settings, backup_weekday: Number(e.target.value)})}
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

            {settings.backup_frequency === BackupFrequency.MONTHLY && (
              <div>
                <label>
                  Día del mes

                  <input
                    type="number"
                    min={1}
                    max={31}
                    value={settings.backup_monthday ?? 1}
                    onChange={e => setSettings({...settings, backup_monthday: Number(e.target.value)})}
                  />

                </label>
              </div>
            )}

          </div>

        </div>


        <div className="backup-config-group">
          <h3>Destino del backup</h3>
          <div className="backup-destination-options">

            <label className="checkbox-label">
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

              <span>
                Conservar copia local
              </span>
            </label>


            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.backup_send_email}
                disabled={!status.email_enabled}
                onChange={e =>
                  setSettings({
                    ...settings,
                    backup_send_email: e.target.checked
                  })
                }
              />

              <span>
                Enviar copia por correo
              </span>
            </label>

            {!status.email_enabled && (
              <p className="backup-config-warning">
                Configure el servidor SMTP para
                habilitar el envío por correo.
              </p>
            )}
          </div>
        </div>

        <div className="backup-config-group">

          <h3>Retención</h3>

          <div className="backup-retention-grid">

            <label>
              Backups diarios
              <span className="field-hint">
                Días de conservación
              </span>

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
              Backups semanales
              <span className="field-hint">
                Días de conservación
              </span>

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
              Backups mensuales
              <span className="field-hint">
                Días de conservación
              </span>

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

      {/* Configuración del correo y del envío por correo electrónico */}
        <div className="backup-config-group">
          <div className="backup-section__header">
            <div>
              <h2>Servidor SMTP</h2>
            </div>
          </div>

          <div className="backup-email-status">

            {status.email_enabled ? (
              <span className="status-badge status-badge--active">
                Correo configurado
              </span>
            ) : (
              <span className="status-badge status-badge--inactive">
                Correo no configurado
              </span>
            )}

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

          <div className="backup-email-actions-block">

            <div className="backup-email-actions-header">
              <h4>Acciones de correo</h4>
              <p>
                Verifique la configuración o genere un backup y envíelo
                inmediatamente por correo.
              </p>
            </div>

            <div className="backup-email-actions">

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
                    <div className="admin-table-actions">

                      <button
                        className="btn btn-secondary"
                        onClick={() =>
                          handleDownload(file.filename)
                        }
                      >
                        Descargar
                      </button>

                      <button
                        className="btn btn-primary"
                        onClick={() =>
                          restoreBackup(file.filename)
                        }
                      >
                        Restaurar
                      </button>

                      <button
                        className="btn btn-danger"
                        onClick={() =>
                          deleteBackup(file.filename)
                        }
                      >
                        Eliminar
                      </button>

                    </div>
                  </td>
                </tr>
            ))}
            </tbody>
          </table>
        </section>

    </main>
  )
}
