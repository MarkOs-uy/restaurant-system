import { jwtDecode } from "jwt-decode"

import { wsService } from "./wsService"


// ---------------------------------------------------------------------------------------------
// Datos del JWT utilizados por el frontend.
// El backend puede incluir otros claims, pero auth solamente necesita exp.
// ---------------------------------------------------------------------------------------------
interface AuthPayload {
  exp?: number
}


// ---------------------------------------------------------------------------------------------
// Elimina toda la información de autenticación almacenada localmente.
// ---------------------------------------------------------------------------------------------
export function clearStoredAuth(): void {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  localStorage.removeItem("restaurant_id")
  localStorage.removeItem("kitchen_station_id")
}


// ---------------------------------------------------------------------------------------------
// Verifica localmente si un token existe y no está vencido.
// Esto NO reemplaza la validación realizada por el backend.
// ---------------------------------------------------------------------------------------------
function isTokenValid(token: string | null): boolean {

  if (!token) {
    return false
  }

  try {
    const decoded = jwtDecode<AuthPayload>(token)

    if (!decoded.exp) {
      return false
    }

    return decoded.exp * 1000 > Date.now()

  } catch {
    return false
  }
}


// ---------------------------------------------------------------------------------------------
// Lee y valida la sesión almacenada localmente.
// Si la información es inexistente o inválida, limpia la sesión.
// ---------------------------------------------------------------------------------------------
export function readAuth(): {
  token: string | null
  role: string | null
} {

  const token = localStorage.getItem("token")
  const role = localStorage.getItem("role")

  if (
    !token ||
    !role ||
    !isTokenValid(token)
  ) {
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


// ---------------------------------------------------------------------------------------------
// Cierra la sesión local y desconecta el WebSocket global.
// Finalmente notifica al resto de la aplicación y redirige al login.
// ---------------------------------------------------------------------------------------------
export function logout(): void {

  clearStoredAuth()

  wsService.disconnect()

  window.dispatchEvent(
    new Event("authChanged")
  )

  window.location.href = "/login"
}