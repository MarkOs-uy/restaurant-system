import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../api"
import { jwtDecode } from "jwt-decode"
import toast from "react-hot-toast"

export default function LoginPage() {

  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const login = async (e?: React.FormEvent) => {

    if (e) e.preventDefault()

    try {

      const formData = new URLSearchParams()
      formData.append("username", username)
      formData.append("password", password)
      formData.append("grant_type", "password")

      const data: any = await apiFetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData.toString(),
        suppressErrorToast: true
      })

      const token = data.access_token
      localStorage.setItem("token", token)

      const decoded: any = jwtDecode(token)

      const role = decoded.role
      const restaurantId = decoded.restaurant_id

      localStorage.setItem("role", role)
      localStorage.setItem("restaurant_id", String(restaurantId))
      
      window.dispatchEvent(new Event("authChanged"))

      switch (role) {

        case "ADMIN":
          navigate("/")
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

    } catch (error: any) {

      console.error("Login error:", error)

      const message =
        error?.status === 401
          ? "Usuario o contraseña incorrectos"
          : error?.message || "No pudimos iniciar sesión"

      toast.error(message, {
        duration: 4500,
        style: {
          border: "1px solid #fecaca",
          background: "#fff7f7",
          color: "#7f1d1d",
          fontWeight: 600
        },
        iconTheme: {
          primary: "#dc2626",
          secondary: "#fff"
        }
      })

    }

  }

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f5f5f5"
      }}
    >
      <form
        onSubmit={login}
        style={{
          background: "white",
          padding: 40,
          borderRadius: 10,
          boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
          width: 320,
          display: "flex",
          flexDirection: "column",
          gap: 15
        }}
      >

        <h2 style={{ textAlign: "center", marginBottom: 10 }}>
          🍽️ Restaurant POS
        </h2>

        <input
          placeholder="Usuario"
          value={username}
          onChange={e => setUsername(e.target.value)}
          style={{
            padding: 10,
            borderRadius: 6,
            border: "1px solid #ccc"
          }}
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{
            padding: 10,
            borderRadius: 6,
            border: "1px solid #ccc"
          }}
        />

        <button
          type="submit"
          style={{
            padding: 10,
            borderRadius: 6,
            border: "none",
            background: "#2d8cff",
            color: "white",
            fontWeight: "bold",
            cursor: "pointer"
          }}
        >
          Ingresar
        </button>

      </form>
    </div>
  )
}
