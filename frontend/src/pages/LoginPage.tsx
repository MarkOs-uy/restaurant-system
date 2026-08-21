import {
  useState,
} from "react"

import { useNavigate } from "react-router-dom"
import { jwtDecode } from "jwt-decode"

import { apiFetch } from "../api"

import { UserRole } from "../types/userRole"

import type {
  AuthPayload,
  LoginResponse
} from "../types/auth"

import {
  isApiError
} from "../types/apiError"

import { showToast } from "../utils/showToast"


export default function LoginPage() {
  const [username, setUsername] =
    useState("")

  const [password, setPassword] =
    useState("")

  const [loggingIn, setLoggingIn] =
    useState(false)

  const navigate = useNavigate()


  // -------------------------------------------------------------------------------------------
  // Autentica al usuario y establece la sesión local.
  // -------------------------------------------------------------------------------------------
  async function login(): Promise<void> {

    if (loggingIn) return

    const trimmedUsername =
      username.trim()

    if (!trimmedUsername || !password) {
      showToast(
        "Ingrese usuario y contraseña"
      )
      return
    }

    setLoggingIn(true)

    try {
      const formData =
        new URLSearchParams()

      formData.append(
        "username",
        trimmedUsername
      )

      formData.append(
        "password",
        password
      )

      formData.append(
        "grant_type",
        "password"
      )

      const data =
        await apiFetch<LoginResponse>(
          "/auth/login",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/x-www-form-urlencoded"
            },

            body:
              formData.toString(),

            suppressErrorToast: true
          }
        )

      const token = data.access_token

      if (!token) {
        throw new Error(
          "El servidor no devolvió un token de autenticación"
        )
      }

      const decoded = jwtDecode<AuthPayload>(token)

      localStorage.setItem( "token", token)

      localStorage.setItem( "role", decoded.role)

      localStorage.setItem( "restaurant_id", String(decoded.restaurant_id))

      window.dispatchEvent(new Event("authChanged"))

      switch (decoded.role) {
        case UserRole.ADMIN:
          navigate("/admin")
          break

        case UserRole.WAITER:
          navigate("/waiter")
          break

        case UserRole.KITCHEN:
          localStorage.removeItem(
            "kitchen_station_id"
          )
          navigate("/kitchen")
          break

        case UserRole.CASHIER:
          navigate("/cashier")
          break
      }

    } catch (error: unknown) {
      console.error("Login error:", error)

      if (isApiError(error) && error.status === 401) {
        showToast("Usuario o contraseña incorrectos")
        return
      }

      if (error instanceof Error) {
        showToast(error.message)
        return
      }

      showToast("No pudimos iniciar sesión")

    } finally {
      setLoggingIn(false)
    }
  }

  return (
    <div className="login-page">
      <form
        className="login-card"
        onSubmit={event => {
          event.preventDefault()
          void login()
        }}
      >
        <h1 className="login-title">
          <span className="login-icon">
            🍳
          </span>

          <span>
            Marcha
          </span>
        </h1>

        <div className="login-fields">
          <input
            type="text"
            placeholder="Usuario"
            autoComplete="username"
            value={username}
            onChange={event =>
              setUsername(
                event.target.value
              )
            }
          />

          <input
            type="password"
            placeholder="Contraseña"
            autoComplete="current-password"
            value={password}
            onChange={event =>
              setPassword(
                event.target.value
              )
            }
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary login-submit"
          disabled={loggingIn}
        >
          {loggingIn
            ? "Ingresando..."
            : "Ingresar"}
        </button>
      </form>
    </div>
  )
}