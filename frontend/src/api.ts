export const API_URL = "/api"

export const WS_URL =
  location.origin.replace("http", "ws") + "/ws"

export const getAuthHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token")}`
})

export const logout = () => {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  window.location.href = "/login"
}


