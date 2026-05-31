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

    } catch (error: any) {

      console.error("Login error:", error)

      const message =
        error?.status === 401
          ? "Usuario o contraseña incorrectos"
          : error?.message || "No pudimos iniciar sesión"

      toast.error(message, {
        duration: 4500,
        style: {
          border: "1px solid rgba(239, 68, 68, 0.25)",
          background: "#161c24",
          color: "#fca5a5",
          fontWeight: 600,
          borderRadius: "10px"
        },
        iconTheme: {
          primary: "#ef4444",
          secondary: "#161c24"
        }
      })

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
        background: "radial-gradient(circle at top, #1a233a 0%, #0c0f17 100%)",
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

        <h2 style={{ textAlign: "center", marginBottom: "10px", fontSize: "28px", fontWeight: "700", letterSpacing: "-0.5px" }}>
          🍳 <span style={{ color: "var(--color-primary)" }}>Marcha</span>
        </h2>

        <input
          placeholder="Usuario"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Contraseña"
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
