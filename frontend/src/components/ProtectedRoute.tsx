import { useEffect, type ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { readAuth } from "../services/auth"

interface Props {
  children: ReactNode
  allowedRoles?: string[]
}

export default function ProtectedRoute({ children, allowedRoles }: Props) {
  const { token, role } = readAuth()

  useEffect(() => {
    if (!token) {
      window.dispatchEvent(new Event("authChanged"))
    }
  }, [token])

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

