import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { API_URL } from "../api"
import { jwtDecode } from "jwt-decode"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const login = async () => {
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

      // 🔥 DECODIFICAMOS
      const decoded: any = jwtDecode(token)

      const role = decoded.role
      const restaurantId = decoded.restaurant_id

      localStorage.setItem("role", role)
      localStorage.setItem("restaurant_id", restaurantId)

      // 🔥 REDIRECCIÓN
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
    <div style={{ padding: 40 }}>
      <h1>Login</h1>

      <input
        placeholder="Usuario"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />

      <button onClick={login}>Ingresar</button>
    </div>
  )
}
