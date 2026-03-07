import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { API_URL } from "../api"
import { jwtDecode } from "jwt-decode"

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

      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData.toString()
      })

      const data = await res.json()

      if (!res.ok) {
        alert("Credenciales inválidas")
        return
      }

      const token = data.access_token
      localStorage.setItem("token", token)

      const decoded: any = jwtDecode(token)
      console.log("TOKEN DECODED:", decoded)

      const role = decoded.role
      const restaurantId = decoded.restaurant_id

      console.log("ROLE:", role)
      console.log("RESTAURANT:", restaurantId)

      localStorage.setItem("role", role)
      localStorage.setItem("restaurant_id", String(restaurantId))

      window.dispatchEvent(new Event("authChanged"))

      console.log("ROLE SAVED:", localStorage.getItem("role"))

      switch (role) {
        case "ADMIN":
          navigate("/")
          break
        case "WAITER":
          navigate("/waiter")
          break
        case "KITCHEN":
          navigate("/kitchen/1")
          break
        case "CASHIER":
          navigate("/cashier")
          break
        default:
          navigate("/")
      }

    } catch (error) {
      console.error("Error login:", error)
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