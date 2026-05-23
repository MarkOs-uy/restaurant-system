// services/auth.ts

import { jwtDecode } from "jwt-decode"
import { wsService } from "./wsService"

interface AuthPayload {
  exp?: number
}

export function clearStoredAuth() {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  localStorage.removeItem("restaurant_id")
  localStorage.removeItem("kitchen_station_id")
}

function isTokenValid(token: string | null) {
  if (!token) return false

  try {
    const decoded = jwtDecode<AuthPayload>(token)
    if (!decoded.exp) return false
    return decoded.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

export function readAuth() {
  const token = localStorage.getItem("token")
  const role = localStorage.getItem("role")

  if (!token || !role || !isTokenValid(token)) {
    clearStoredAuth()
    return {
      token: null,
      role: null
    }
  }

  return {
    token,
    role
  }
}

export function logout() {
  clearStoredAuth()
  wsService.disconnect()
  window.dispatchEvent(new Event("authChanged"))
  window.location.href = "/login"
}
