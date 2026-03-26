export const API_URL = "/api"

export const WS_URL = "ws://localhost:8000"

export const getAuthHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token")}`
})

export const logout = () => {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  window.location.href = "/login"
}


