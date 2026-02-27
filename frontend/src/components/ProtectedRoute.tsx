import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"

interface Props {
  children: ReactNode
  allowedRoles?: string[]
}

export default function ProtectedRoute({ children, allowedRoles }: Props) {
  const token = localStorage.getItem("token")
  const role = localStorage.getItem("role")

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

