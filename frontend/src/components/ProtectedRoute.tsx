import { useEffect, type ReactNode } from "react"
import { Navigate } from "react-router-dom"

import { readAuth } from "../services/auth"

// ---------------------------------------------------------------------------------------------
// Props de la ruta protegida.
// allowedRoles permite restringir opcionalmente el acceso según el rol del usuario.
// ---------------------------------------------------------------------------------------------
interface Props {
  children: ReactNode
  allowedRoles?: string[]
}

// ---------------------------------------------------------------------------------------------
// Protege rutas que requieren autenticación y, opcionalmente, determinados roles.
// ---------------------------------------------------------------------------------------------
export default function ProtectedRoute({
  children,
  allowedRoles
}: Props) {

  const { token, role } = readAuth()

  // -------------------------------------------------------------------------------------------
  // Notifica a la aplicación cuando la sesión local deja de ser válida.
  // -------------------------------------------------------------------------------------------
  useEffect(() => {

    if (!token) {
      window.dispatchEvent(
        new Event("authChanged")
      )
    }

  }, [token])

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (
    allowedRoles &&
    (!role || !allowedRoles.includes(role))
  ) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}