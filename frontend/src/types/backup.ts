/**
 * Interface de backups
 */

export const BackupType = {
  MANUAL: "manual",
  DAILY: "daily",
  WEEKLY: "weekly",
  MONTHLY: "monthly",
  BEFORE_RESTORE: "before_restore"
} as const

export type BackupType =
  typeof BackupType[keyof typeof BackupType]


export interface BackupStatus {
  last_backup_at: string | null
  last_backup_file: string | null
  last_backup_size: number | null
  last_backup_source: BackupType | null

  email_enabled: boolean
  email_from: string | null

  last_automatic_backup_at: string | null
  next_automatic_backup_at: string | null
  last_backup_result: string | null
}


export interface BackupFile {
  filename: string
  created_at: string
  size: number
  type: BackupType
}


export interface BackupRestoreResponse {
  restart_required: boolean
}