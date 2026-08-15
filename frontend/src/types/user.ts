import type { UserRole } from "./userRole"

export interface User {
  id: number
  username: string
  role: UserRole
  active: boolean
}

export interface UserCreate {
  username: string
  password: string
  role: UserRole
}

export interface UserUpdate {
  username?: string
  password?: string
  role?: UserRole
}