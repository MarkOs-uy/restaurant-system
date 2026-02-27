export const API_URL = "http://localhost:8000"

export const API_HEADERS = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token")}`
}

export const getAuthHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token")}`
})

export const logout = () => {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  window.location.href = "/login"
}


