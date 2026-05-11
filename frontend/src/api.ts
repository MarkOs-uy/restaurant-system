export const API_URL = import.meta.env.VITE_API_URL || "/api"

const defaultWsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
export const WS_URL =
  import.meta.env.VITE_WS_URL || `${defaultWsProtocol}//${window.location.host}`

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

import { handleApiError } from "./utils/handleApiError"

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

  let data = null

  try {
    data = await res.json()
  } catch {}

  if (res.status === 401) {
    logout()
  }

  if (!res.ok) {
    const error = new Error(data?.detail || `HTTP ${res.status}`) as any
    error.code = data?.error
    error.context = data?.context
    error.status = res.status

    handleApiError(error)

    throw error
  }

  return data
}


