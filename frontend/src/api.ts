export const API_URL = "/api"

export const WS_URL = "ws://localhost:8000"

export const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem("token")}`
})

export const logout = () => {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  window.location.href = "/login"
}

type ApiFetchOptions = Omit<RequestInit, "body"> & {
  body?: any
}

export async function apiFetch(
  url: string,
  options: ApiFetchOptions = {}
) {

  const isJsonBody =
    options.body &&
    typeof options.body === "object" &&
    !(options.body instanceof FormData)

  const body = isJsonBody
    ? JSON.stringify(options.body)
    : options.body

  const res = await fetch(`${API_URL}${url}`, {
    ...options,
    body,
    headers: {
      ...getAuthHeaders(),
      ...(isJsonBody ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {})
    }
  })

  const data = await res.json().catch(() => null)

  if (res.status === 401) {
    logout()
  }

  if (!res.ok) {
    throw {
      message: data?.detail || "Server error",
      code: data?.error,
      context: data?.context
    }
  }

  return data
}