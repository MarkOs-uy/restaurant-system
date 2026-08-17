// types/systemSettings.ts

export const BackupFrequency = {
  MANUAL: "manual",
  DAILY: "daily",
  WEEKLY: "weekly",
  MONTHLY: "monthly"
} as const

export type BackupFrequency =
  typeof BackupFrequency[
    keyof typeof BackupFrequency
  ]


export interface SystemSettings {
  smtp_host: string
  smtp_port: number
  smtp_user: string
  smtp_password: string
  smtp_from: string
  smtp_use_tls: boolean

  backup_email: string

  backup_enabled: boolean
  backup_frequency: BackupFrequency

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

export interface RawSystemSettings {
  smtp_host: string | null
  smtp_port: number
  smtp_user: string | null
  smtp_from: string | null
  smtp_use_tls: boolean
  smtp_password_configured: boolean

  backup_email: string | null

  backup_enabled: boolean
  backup_frequency: BackupFrequency

  backup_time: string

  backup_weekday: number | null
  backup_monthday: number | null

  backup_retention_daily: number
  backup_retention_weekly: number
  backup_retention_monthly: number

  backup_keep_local: boolean
  backup_send_email: boolean

  backup_timezone: string

  last_automatic_backup_at: string | null
  next_automatic_backup_at: string | null
  last_backup_result: string | null
}