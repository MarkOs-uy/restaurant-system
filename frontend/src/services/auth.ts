// services/auth.ts

import { wsService } from "./wsService"

export function logout() {
  localStorage.removeItem("token") 
  wsService.disconnect()
  window.dispatchEvent(new Event("authChanged"))
  window.location.href = "/login"
}