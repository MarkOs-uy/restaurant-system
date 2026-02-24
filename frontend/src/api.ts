export const API_URL = "http://localhost:8000"

export const API_HEADERS = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token")}`
}



