import type { UserRole } from "./userRole"

// ---------------------------------------------------------------------------
// Respuesta devuelta por el endpoint de autenticación.
// ---------------------------------------------------------------------------
export interface LoginResponse {
  access_token: string
  token_type: string
}

// ----------------------------------------------------------------------------
// Claims del JWT utilizados por el frontend.
// El backend puede incluir otros claims.
// ----------------------------------------------------------------------------
export interface AuthPayload {
  role: UserRole
  restaurant_id: number
}

export interface AuthState {
  token: string | null
  role: UserRole | null
  restaurantId: number | null
}