import { logout } from "./services/auth"
export const API_URL = import.meta.env.VITE_API_URL || "/api"

const defaultWsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
export const WS_URL =
  import.meta.env.VITE_WS_URL || `${defaultWsProtocol}//${window.location.host}`

export const getAuthHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem("token")}`
})

type ApiFetchOptions = Omit<RequestInit, "body"> & {
  body?: any
  suppressErrorToast?: boolean
}

import { handleApiError } from "./utils/handleApiError"

export async function apiFetch(
  url: string,
  options: ApiFetchOptions = {}
) {
  const {
    suppressErrorToast,
    ...fetchOptions
  } = options

  const isJsonBody =
    fetchOptions.body &&
    typeof fetchOptions.body === "object" &&
    !(fetchOptions.body instanceof FormData)

  const body = isJsonBody
    ? JSON.stringify(fetchOptions.body)
    : fetchOptions.body

  const res = await fetch(`${API_URL}${url}`, {
    ...fetchOptions,
    body,
    headers: {
      ...getAuthHeaders(),
      ...(isJsonBody ? { "Content-Type": "application/json" } : {}),
      ...(fetchOptions.headers || {})
    }
  })

  let data = null

  try {
    data = await res.json()
  } catch {}

  if (res.status === 401 && url !== "/auth/login") {
    logout()
  }

  if (!res.ok) {
    const error = new Error(data?.detail || `HTTP ${res.status}`) as any
    error.code = data?.error
    error.context = data?.context
    error.status = res.status

    if (!suppressErrorToast) {
      handleApiError(error)
    }

    throw error
  }

  return data
}


