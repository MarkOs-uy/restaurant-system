import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { API_URL } from "../api"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const login = async () => {
    const formData = new URLSearchParams()
    formData.append("username", username)
    formData.append("password", password)

    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData.toString()
    })

    if (!res.ok) {
      alert("Credenciales inválidas")
      return
    }

    const data = await res.json()

    localStorage.setItem("token", data.access_token)
    localStorage.setItem("role", data.role)

    // 🔥 Redirigir según rol
    if (data.role === "ADMIN") navigate("/")
    if (data.role === "WAITER") navigate("/waiter")
    if (data.role === "KITCHEN") navigate("/kitchen/1")
    if (data.role === "CASHIER") navigate("/cashier")
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
