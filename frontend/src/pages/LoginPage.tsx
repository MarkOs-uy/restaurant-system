import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { jwtDecode } from "jwt-decode"

import { apiFetch } from "../api"
import { showToast } from "../utils/showToast"
import type { ApiError } from "../types/apiError"

// ---------------------------------------------------------------------------------------------
// Respuesta devuelta por el endpoint de autenticación.
// ---------------------------------------------------------------------------------------------
interface LoginResponse {
  access_token: string
  token_type: string
}

// ---------------------------------------------------------------------------------------------
// Claims del JWT utilizados por el frontend.
// El backend puede incluir otros claims.
// ---------------------------------------------------------------------------------------------
interface AuthPayload {
  role: string
  restaurant_id: number
}

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  const navigate = useNavigate()

  // -------------------------------------------------------------------------------------------
  // Autentica al usuario y establece la sesión local.
  // -------------------------------------------------------------------------------------------
  async function login(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault()

    try {
      const formData = new URLSearchParams()

      formData.append("username", username)
      formData.append("password", password)
      formData.append("grant_type", "password")

      const data = await apiFetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData.toString(),
        suppressErrorToast: true
      }) as LoginResponse

      const token = data.access_token

      if (!token) {
        throw new Error("El servidor no devolvió un token de autenticación")
      }

      const decoded = jwtDecode<AuthPayload>(token)

      localStorage.setItem("token", token)
      localStorage.setItem("role", decoded.role)
      localStorage.setItem(
        "restaurant_id",
        String(decoded.restaurant_id)
      )

      window.dispatchEvent(
        new Event("authChanged")
      )

      switch (decoded.role) {
        case "ADMIN":
          navigate("/admin")
          break

        case "WAITER":
          navigate("/waiter")
          break

        case "KITCHEN":
          localStorage.removeItem("kitchen_station_id")
          navigate("/kitchen")
          break

        case "CASHIER":
          navigate("/cashier")
          break

        default:
          navigate("/")
      }

    } catch (error: unknown) {
      console.error("Login error:", error)

      const apiError = error as ApiError

      if (apiError.status === 401) {
        showToast("Usuario o contraseña incorrectos")
        return
      }

      showToast(
        apiError.message ?? "No pudimos iniciar sesión"
      )
    }
  }

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background:
          "radial-gradient(circle at top, #1a233a 0%, #0c0f17 100%)",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 9999
      }}
    >
      <form
        onSubmit={login}
        style={{
          background: "rgba(22, 28, 45, 0.45)",
          backdropFilter: "blur(12px) saturate(180%)",
          WebkitBackdropFilter: "blur(12px) saturate(180%)",
          border: "1px solid var(--color-border)",
          padding: "40px",
          borderRadius: "var(--radius-lg)",
          boxShadow: "var(--shadow-lg), var(--shadow-glass)",
          width: "360px",
          display: "flex",
          flexDirection: "column",
          gap: "20px"
        }}
      >
        <h2
          style={{
            textAlign: "center",
            marginBottom: "10px",
            fontSize: "28px",
            fontWeight: "700",
            letterSpacing: "-0.5px"
          }}
        >
          🍳{" "}
          <span style={{ color: "var(--color-primary)" }}>
            Marcha
          </span>
        </h2>

        <input
          type="text"
          placeholder="Usuario"
          autoComplete="username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Contraseña"
          autoComplete="current-password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />

        <button
          type="submit"
          className="btn-primary"
          style={{
            padding: "12px",
            fontSize: "16px",
            marginTop: "10px"
          }}
        >
          Ingresar
        </button>
      </form>
    </div>
  )
}